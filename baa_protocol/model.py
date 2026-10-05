"""Minimal executable reference model for BAA-Protocol.

The model demonstrates protocol distinctions and regression properties. Its
toy risk functional is not a real-world risk model and must not be cited as a
safety proof.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Optional


class Decision(str, Enum):
    DENY = "deny"
    HOLD = "hold"
    ADMIT = "admit"


class ProposalState(str, Enum):
    PROPOSED = "proposed"
    DENIED = "denied"
    HELD = "held"
    ADMITTED = "admitted"
    PENDING = "pending"
    SETTLED = "settled"


@dataclass(frozen=True)
class Exposure:
    bound: int
    risk_factor: str


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    object_id: str
    operation: str
    quota: int
    exposure_bound: int
    risk_factor: str
    expires_at: int
    state_version: int
    verification_available: bool = True
    bridge_valid: bool = True
    fallback_viable: bool = True
    composition_bounded: bool = True


@dataclass(frozen=True)
class Capability:
    capability_id: str
    proposal_id: str
    object_id: str
    operation: str
    quota: int
    expires_at: int
    state_version: int


@dataclass
class Ledger:
    reserved: Dict[str, Exposure] = field(default_factory=dict)
    pending: Dict[str, Exposure] = field(default_factory=dict)
    settled: Dict[str, Exposure] = field(default_factory=dict)

    def all_exposures(self) -> Iterable[Exposure]:
        yield from self.reserved.values()
        yield from self.pending.values()
        yield from self.settled.values()


@dataclass(frozen=True)
class AdmissionResult:
    decision: Decision
    reason: str
    capability: Optional[Capability] = None


class AdmissionKernel:
    """Toy assurance kernel with composition-aware admission."""

    def __init__(
        self,
        *,
        risk_budget: int,
        interaction_penalty: int = 0,
        protected_sources: Optional[set[str]] = None,
    ) -> None:
        if risk_budget < 0:
            raise ValueError("risk_budget must be non-negative")
        if interaction_penalty < 0:
            raise ValueError("interaction_penalty must be non-negative")
        self.risk_budget = risk_budget
        self.interaction_penalty = interaction_penalty
        self.protected_sources = set(protected_sources or set())
        self.ledger = Ledger()
        self.states: Dict[str, ProposalState] = {}
        self.capabilities: Dict[str, Capability] = {}

    def risk(self, exposures: Iterable[Exposure]) -> int:
        """Return a toy joint-state risk score.

        Base bounds are additive. Exposures sharing a risk factor incur an
        additional pairwise interaction term. The term exists only to exercise
        composition-aware admission in tests.
        """
        items = list(exposures)
        total = sum(item.bound for item in items)
        if self.interaction_penalty == 0:
            return total

        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if left.risk_factor == right.risk_factor:
                    total += self.interaction_penalty * min(
                        left.bound, right.bound
                    )
        return total

    @property
    def current_risk(self) -> int:
        return self.risk(self.ledger.all_exposures())

    def projected_risk(self, proposal: Proposal) -> int:
        extra = Exposure(proposal.exposure_bound, proposal.risk_factor)
        return self.risk([*self.ledger.all_exposures(), extra])

    def evaluate(self, proposal: Proposal) -> AdmissionResult:
        self.states.setdefault(proposal.proposal_id, ProposalState.PROPOSED)

        if proposal.object_id in self.protected_sources:
            self.states[proposal.proposal_id] = ProposalState.DENIED
            return AdmissionResult(
                Decision.DENY,
                "guarantee-channel isolation: protected source is unreachable",
            )

        if not proposal.composition_bounded:
            self.states[proposal.proposal_id] = ProposalState.HELD
            return AdmissionResult(
                Decision.HOLD,
                "joint exposure is not bounded under the declared model",
            )

        if not proposal.verification_available:
            self.states[proposal.proposal_id] = ProposalState.HELD
            return AdmissionResult(
                Decision.HOLD,
                "required external verification path is unavailable",
            )

        if not proposal.bridge_valid:
            self.states[proposal.proposal_id] = ProposalState.HELD
            return AdmissionResult(
                Decision.HOLD,
                "semantic bridge required for the claim is not established",
            )

        if not proposal.fallback_viable:
            self.states[proposal.proposal_id] = ProposalState.HELD
            return AdmissionResult(
                Decision.HOLD,
                "post-admission state is outside the declared viable region",
            )

        projected = self.projected_risk(proposal)
        if projected > self.risk_budget:
            self.states[proposal.proposal_id] = ProposalState.DENIED
            return AdmissionResult(
                Decision.DENY,
                f"projected joint risk {projected} exceeds budget {self.risk_budget}",
            )

        exposure = Exposure(proposal.exposure_bound, proposal.risk_factor)
        self.ledger.reserved[proposal.proposal_id] = exposure
        self.states[proposal.proposal_id] = ProposalState.ADMITTED

        capability = Capability(
            capability_id=f"cap:{proposal.proposal_id}",
            proposal_id=proposal.proposal_id,
            object_id=proposal.object_id,
            operation=proposal.operation,
            quota=proposal.quota,
            expires_at=proposal.expires_at,
            state_version=proposal.state_version,
        )
        self.capabilities[capability.capability_id] = capability
        return AdmissionResult(Decision.ADMIT, "admitted", capability)

    def execute(
        self,
        capability: Capability,
        *,
        object_id: str,
        operation: str,
        amount: int,
        now: int,
        state_version: int,
    ) -> None:
        known = self.capabilities.get(capability.capability_id)
        if known != capability:
            raise PermissionError("unknown or altered capability")
        if self.states.get(capability.proposal_id) != ProposalState.ADMITTED:
            raise PermissionError("proposal is not in executable admitted state")
        if now > capability.expires_at:
            raise PermissionError("capability expired")
        if state_version != capability.state_version:
            raise PermissionError("capability is stale for current state version")
        if object_id != capability.object_id:
            raise PermissionError("object mismatch")
        if operation != capability.operation:
            raise PermissionError("operation mismatch")
        if amount < 0 or amount > capability.quota:
            raise PermissionError("quota exceeded")

        exposure = self.ledger.reserved.pop(capability.proposal_id)
        self.ledger.pending[capability.proposal_id] = exposure
        self.states[capability.proposal_id] = ProposalState.PENDING

    def verify(self, proposal_id: str, *, realized_exposure: int) -> None:
        if realized_exposure < 0:
            raise ValueError("realized_exposure must be non-negative")
        if self.states.get(proposal_id) != ProposalState.PENDING:
            raise ValueError("proposal is not pending")

        prior = self.ledger.pending.pop(proposal_id)
        self.ledger.settled[proposal_id] = Exposure(
            realized_exposure,
            prior.risk_factor,
        )
        self.states[proposal_id] = ProposalState.SETTLED

    def conservative_timeout_settlement(self, proposal_id: str) -> None:
        """Charge the declared pending upper bound when confirmation is lost."""
        if self.states.get(proposal_id) != ProposalState.PENDING:
            raise ValueError("proposal is not pending")

        prior = self.ledger.pending.pop(proposal_id)
        self.ledger.settled[proposal_id] = prior
        self.states[proposal_id] = ProposalState.SETTLED
