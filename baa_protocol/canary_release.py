"""Reference BAA model for progressive canary release promotion.

This module models one bounded reality-facing surface: increasing or restoring
candidate traffic. It is intentionally narrower than the full AIOS autonomous
development lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .model import Decision


class RouteKnowledge(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"


@dataclass(frozen=True)
class CanaryStagePolicy:
    weight_percent: int
    min_duration_seconds: int
    min_requests: int

    def __post_init__(self) -> None:
        if not 1 <= self.weight_percent <= 100:
            raise ValueError("weight_percent must be between 1 and 100")
        if self.min_duration_seconds < 1 or self.min_requests < 1:
            raise ValueError("evidence thresholds must be positive")


@dataclass(frozen=True)
class CanaryEvidence:
    experiment_id: str
    stage_index: int
    weight_percent: int
    observed_duration_seconds: int
    total_requests: int
    candidate_requests: int
    control_requests: int
    candidate_error_rate: float
    control_error_rate: float | None
    candidate_p95_latency_ms: float
    control_p95_latency_ms: float | None
    telemetry_complete: bool = True

    def __post_init__(self) -> None:
        if self.observed_duration_seconds < 0:
            raise ValueError("duration cannot be negative")
        for value in (self.total_requests, self.candidate_requests, self.control_requests):
            if value < 0:
                raise ValueError("request counts cannot be negative")
        if self.candidate_requests + self.control_requests != self.total_requests:
            raise ValueError("candidate and control requests must sum to total")
        if not 0.0 <= self.candidate_error_rate <= 1.0:
            raise ValueError("candidate_error_rate must be between 0 and 1")
        if self.control_error_rate is not None and not 0.0 <= self.control_error_rate <= 1.0:
            raise ValueError("control_error_rate must be between 0 and 1")
        if self.candidate_p95_latency_ms < 0:
            raise ValueError("candidate latency cannot be negative")
        if self.control_p95_latency_ms is not None and self.control_p95_latency_ms < 0:
            raise ValueError("control latency cannot be negative")


@dataclass(frozen=True)
class CanaryGuardrails:
    max_candidate_error_rate: float
    max_error_rate_delta: float
    max_candidate_p95_latency_ms: float
    max_p95_latency_ratio: float


@dataclass(frozen=True)
class TrafficProposal:
    proposal_id: str
    experiment_id: str
    target_id: str
    control_release_id: str
    candidate_deployment_id: str
    stage_index: int
    candidate_weight_percent: int
    state_version: int
    operation_id: str


@dataclass(frozen=True)
class TrafficCapability:
    capability_id: str
    proposal_id: str
    experiment_id: str
    target_id: str
    control_release_id: str
    candidate_deployment_id: str
    stage_index: int
    candidate_weight_percent: int
    state_version: int
    operation_id: str
    operation: str


@dataclass(frozen=True)
class Admission:
    decision: Decision
    reason: str
    capability: Optional[TrafficCapability] = None


class CanaryReleaseKernel:
    """Fail-closed admission for staged candidate traffic exposure."""

    def __init__(
        self,
        *,
        experiment_id: str,
        target_id: str,
        control_release_id: str,
        candidate_deployment_id: str,
        stages: tuple[CanaryStagePolicy, ...],
        guardrails: CanaryGuardrails,
        state_version: int = 1,
        rollback_available: bool = True,
        current_stage_index: int = 0,
        current_weight_percent: int = 0,
    ) -> None:
        if not stages:
            raise ValueError("stages are required")
        weights = tuple(item.weight_percent for item in stages)
        if weights != tuple(sorted(weights)) or weights[-1] != 100:
            raise ValueError("stages must increase monotonically and end at 100")
        self.experiment_id = experiment_id
        self.target_id = target_id
        self.control_release_id = control_release_id
        self.candidate_deployment_id = candidate_deployment_id
        self.stages = stages
        self.guardrails = guardrails
        self.state_version = state_version
        self.rollback_available = rollback_available
        if not 0 <= current_stage_index < len(stages):
            raise ValueError("current_stage_index is outside configured stages")
        if current_weight_percent != 0 and (
            stages[current_stage_index].weight_percent != current_weight_percent
        ):
            raise ValueError("current weight must match the current configured stage")
        self.current_stage_index = current_stage_index
        self.current_weight_percent = current_weight_percent
        self.route_knowledge = RouteKnowledge.VERIFIED
        self._capabilities: dict[str, TrafficCapability] = {}

    def _scope_matches(self, proposal: TrafficProposal) -> bool:
        return (
            proposal.experiment_id == self.experiment_id
            and proposal.target_id == self.target_id
            and proposal.control_release_id == self.control_release_id
            and proposal.candidate_deployment_id == self.candidate_deployment_id
        )

    def _guardrail_violations(self, evidence: CanaryEvidence) -> tuple[str, ...]:
        violations: list[str] = []
        if evidence.candidate_error_rate > self.guardrails.max_candidate_error_rate:
            violations.append("candidate_error_rate")
        if evidence.candidate_p95_latency_ms > self.guardrails.max_candidate_p95_latency_ms:
            violations.append("candidate_p95_latency_ms")
        if (
            evidence.control_requests > 0
            and evidence.control_error_rate is not None
            and evidence.control_p95_latency_ms is not None
            and evidence.control_p95_latency_ms > 0
        ):
            if (
                evidence.candidate_error_rate - evidence.control_error_rate
                > self.guardrails.max_error_rate_delta
            ):
                violations.append("error_rate_delta")
            if (
                evidence.candidate_p95_latency_ms / evidence.control_p95_latency_ms
                > self.guardrails.max_p95_latency_ratio
            ):
                violations.append("p95_latency_ratio")
        return tuple(violations)

    @staticmethod
    def _minimum_arm_requests(total: int, weight: int) -> tuple[int, int]:
        import math

        candidate = max(1, math.ceil(total * weight / 100))
        control = 0 if weight == 100 else max(1, math.ceil(total * (100 - weight) / 100))
        return candidate, control

    def _evidence_sufficient(
        self,
        evidence: CanaryEvidence,
        stage: CanaryStagePolicy,
    ) -> bool:
        if not evidence.telemetry_complete:
            return False
        if evidence.observed_duration_seconds < stage.min_duration_seconds:
            return False
        if evidence.total_requests < stage.min_requests:
            return False
        candidate_min, control_min = self._minimum_arm_requests(
            stage.min_requests, stage.weight_percent
        )
        if evidence.candidate_requests < candidate_min:
            return False
        if evidence.control_requests < control_min:
            return False
        if stage.weight_percent < 100:
            if evidence.control_error_rate is None:
                return False
            if evidence.control_p95_latency_ms is None or evidence.control_p95_latency_ms <= 0:
                return False
        return True

    def admit_increase(
        self,
        proposal: TrafficProposal,
        *,
        evidence: CanaryEvidence | None,
    ) -> Admission:
        if not self._scope_matches(proposal):
            return Admission(Decision.DENY, "scope mismatch")
        if proposal.state_version != self.state_version:
            return Admission(Decision.DENY, "stale state version")
        if self.route_knowledge is RouteKnowledge.PENDING:
            return Admission(Decision.HOLD, "traffic effect unresolved")
        if not self.rollback_available:
            return Admission(Decision.HOLD, "rollback path unavailable")
        if not 0 <= proposal.stage_index < len(self.stages):
            return Admission(Decision.DENY, "stage index outside experiment")

        stage = self.stages[proposal.stage_index]
        if proposal.candidate_weight_percent != stage.weight_percent:
            return Admission(Decision.DENY, "weight does not match configured stage")

        expected_stage = 0 if self.current_weight_percent == 0 else self.current_stage_index + 1
        if proposal.stage_index != expected_stage:
            return Admission(Decision.DENY, "proposal is stale or skips a stage")

        # Entering the first stage is allowed from zero after the prior quality
        # gates represented by the experiment contract. Later increases require
        # evidence from the currently exposed stage.
        if self.current_weight_percent > 0:
            if evidence is None:
                return Admission(Decision.HOLD, "stage evidence unavailable")
            if (
                evidence.experiment_id != self.experiment_id
                or evidence.stage_index != self.current_stage_index
                or evidence.weight_percent != self.current_weight_percent
            ):
                return Admission(Decision.HOLD, "stage evidence is stale or mismatched")
            if self._guardrail_violations(evidence):
                return Admission(Decision.DENY, "canary guardrail violation")
            current = self.stages[self.current_stage_index]
            if not self._evidence_sufficient(evidence, current):
                return Admission(Decision.HOLD, "insufficient canary evidence")
        capability = TrafficCapability(
            capability_id=f"traffic:{proposal.proposal_id}",
            proposal_id=proposal.proposal_id,
            experiment_id=proposal.experiment_id,
            target_id=proposal.target_id,
            control_release_id=proposal.control_release_id,
            candidate_deployment_id=proposal.candidate_deployment_id,
            stage_index=proposal.stage_index,
            candidate_weight_percent=proposal.candidate_weight_percent,
            state_version=proposal.state_version,
            operation_id=proposal.operation_id,
            operation="development.traffic.apply",
        )
        self._capabilities[capability.capability_id] = capability
        return Admission(Decision.ADMIT, "admitted", capability)

    def execute(self, capability: TrafficCapability) -> None:
        known = self._capabilities.get(capability.capability_id)
        if known != capability:
            raise PermissionError("unknown or altered capability")
        if capability.state_version != self.state_version:
            raise PermissionError("stale capability")
        if self.route_knowledge is RouteKnowledge.PENDING:
            raise PermissionError("traffic effect already unresolved")
        if capability.operation != "development.traffic.apply":
            raise PermissionError("wrong capability operation")
        self.route_knowledge = RouteKnowledge.PENDING

    def verify_route(
        self,
        capability: TrafficCapability,
        *,
        experiment_id: str,
        stage_index: int,
        candidate_weight_percent: int,
    ) -> None:
        if self.route_knowledge is not RouteKnowledge.PENDING:
            raise ValueError("no traffic effect awaits verification")
        if (
            experiment_id != capability.experiment_id
            or stage_index != capability.stage_index
            or candidate_weight_percent != capability.candidate_weight_percent
        ):
            raise ValueError("observed route does not match admitted capability")

        self.current_weight_percent = candidate_weight_percent
        self.current_stage_index = stage_index
        self.route_knowledge = RouteKnowledge.VERIFIED

    def mark_unknown(self) -> None:
        if self.route_knowledge is not RouteKnowledge.PENDING:
            raise ValueError("no dispatched traffic effect")
        # Deliberately preserve PENDING. Re-admission remains blocked.

    def admit_restore(self, *, operation_id: str) -> Admission:
        if not self.rollback_available:
            return Admission(Decision.HOLD, "rollback path unavailable")
        capability = TrafficCapability(
            capability_id=f"restore:{operation_id}",
            proposal_id=f"restore:{operation_id}",
            experiment_id=self.experiment_id,
            target_id=self.target_id,
            control_release_id=self.control_release_id,
            candidate_deployment_id=self.candidate_deployment_id,
            stage_index=self.current_stage_index,
            candidate_weight_percent=0,
            state_version=self.state_version,
            operation_id=operation_id,
            operation="development.traffic.restore",
        )
        self._capabilities[capability.capability_id] = capability
        return Admission(Decision.ADMIT, "restore admitted", capability)

    def execute_restore(self, capability: TrafficCapability) -> None:
        known = self._capabilities.get(capability.capability_id)
        if known != capability or capability.operation != "development.traffic.restore":
            raise PermissionError("invalid restore capability")
        if capability.state_version != self.state_version:
            raise PermissionError("stale restore capability")
        # Restore is the conservative compensating action and may execute even
        # when the preceding increase has an unknown outcome.
        self.route_knowledge = RouteKnowledge.PENDING

    def verify_restored(self, *, candidate_weight_percent: int) -> None:
        if self.route_knowledge is not RouteKnowledge.PENDING:
            raise ValueError("no route change awaits verification")
        if candidate_weight_percent != 0:
            raise ValueError("control route is not restored")
        self.current_weight_percent = 0
        self.current_stage_index = 0
        self.route_knowledge = RouteKnowledge.VERIFIED

    def advance_stage(self) -> None:
        """Move the expected stage after verified current-stage evidence.

        This is intentionally separate from route verification: evidence
        evaluation determines whether the next stage is allowed.
        """
        if self.current_stage_index >= len(self.stages) - 1:
            raise ValueError("already at final stage")
        self.current_stage_index += 1
