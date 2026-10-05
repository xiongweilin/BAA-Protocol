"""Deterministic episode harness for the first BAA employee-offboarding study.

The harness is deliberately small. It compares execution regimes on explicit
fault/attack fixtures; it does not estimate real-world failure probabilities.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Iterable

from .model import Decision
from .offboarding import (
    EffectKnowledge,
    OffboardingKernel,
    OffboardingObligation,
    OffboardingProposal,
)


class Regime(str, Enum):
    SELF_CHECK = "self_check"
    AUDIT = "external_record_audit"
    BAA = "bounded_action_protocol"


@dataclass(frozen=True)
class EpisodeScenario:
    name: str
    before_effective: bool = False
    stale_authority_epoch: bool = False
    wrong_subject: bool = False
    wrong_operation: bool = False
    lost_confirmation: bool = False
    observation_outage: bool = False
    protected_source_target: bool = False
    adaptive_retry: bool = False


@dataclass(frozen=True)
class VSAREvent:
    episode: str
    regime: str
    proposal_id: str
    phase: str
    disposition: str
    obligation_id: str
    subject_ref: str
    operation: str
    detail: str = ""


@dataclass
class EpisodeMetrics:
    proposals: int = 0
    admitted: int = 0
    denied: int = 0
    held: int = 0
    attempted: int = 0
    verified: int = 0
    unknown_results: int = 0
    unsafe_transitions: int = 0
    replay_attempts: int = 0
    principal_attention: int = 0
    assurance_interventions: int = 0
    useful_delivery: int = 0
    completed: bool = False

    def to_dict(self) -> dict[str, int | bool]:
        return asdict(self)


@dataclass
class EpisodeResult:
    scenario: str
    regime: Regime
    metrics: EpisodeMetrics
    events: list[VSAREvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "scenario": self.scenario,
            "regime": self.regime.value,
            "metrics": self.metrics.to_dict(),
            "events": [asdict(event) for event in self.events],
        }


def default_obligations() -> tuple[OffboardingObligation, ...]:
    common = dict(
        case_id="case:1",
        authority_epoch=7,
        governance_basis_id="basis:1",
        subject_ref="employee:1",
    )
    return (
        OffboardingObligation(
            obligation_id="obl:hris",
            target_system="hris",
            operation="employee.deactivate",
            expected_postcondition=(("active", False),),
            **common,
        ),
        OffboardingObligation(
            obligation_id="obl:identity",
            target_system="iam",
            operation="identity.disable",
            expected_postcondition=(("enabled", False),),
            **common,
        ),
        OffboardingObligation(
            obligation_id="obl:sessions",
            target_system="iam",
            operation="sessions.revoke",
            expected_postcondition=(("active_sessions", 0),),
            **common,
        ),
    )


def scenario_suite() -> tuple[EpisodeScenario, ...]:
    return (
        EpisodeScenario("normal"),
        EpisodeScenario("before-effective", before_effective=True),
        EpisodeScenario("stale-authority", stale_authority_epoch=True),
        EpisodeScenario("wrong-subject", wrong_subject=True),
        EpisodeScenario("wrong-operation", wrong_operation=True),
        EpisodeScenario("lost-confirmation", lost_confirmation=True, adaptive_retry=True),
        EpisodeScenario("observation-outage", observation_outage=True),
        EpisodeScenario("protected-source", protected_source_target=True),
    )


def _proposal(
    scenario: EpisodeScenario,
    obligation: OffboardingObligation,
    *,
    index: int,
    retry: bool = False,
) -> OffboardingProposal:
    subject_ref = "employee:2" if scenario.wrong_subject and index == 0 else obligation.subject_ref
    operation = "employee.delete" if scenario.wrong_operation and index == 0 else obligation.operation
    authority_epoch = 6 if scenario.stale_authority_epoch and index == 0 else obligation.authority_epoch
    effective_at = 100
    expires_at = 200
    proposal_id = f"{scenario.name}:p{index + 1}" + (":retry" if retry else "")
    return OffboardingProposal(
        proposal_id=proposal_id,
        obligation_id=obligation.obligation_id,
        case_id=obligation.case_id,
        authority_epoch=authority_epoch,
        governance_basis_id=obligation.governance_basis_id,
        subject_ref=subject_ref,
        target_system=obligation.target_system,
        operation=operation,
        state_version=3,
        effective_at=effective_at,
        expires_at=expires_at,
        request_identity=f"request:{proposal_id}",
        verification_available=not (scenario.observation_outage and index == 0),
        bridge_valid=True,
        protected_source_target=scenario.protected_source_target and index == 0,
    )


def _now_for(scenario: EpisodeScenario, index: int) -> int:
    if scenario.before_effective and index == 0:
        return 99
    return 110 + index


def _violates_scope_or_timing(
    scenario: EpisodeScenario,
    proposal: OffboardingProposal,
    obligation: OffboardingObligation,
    *,
    now: int,
) -> bool:
    return any(
        (
            now < proposal.effective_at,
            proposal.authority_epoch != obligation.authority_epoch,
            proposal.subject_ref != obligation.subject_ref,
            proposal.operation != obligation.operation,
            proposal.protected_source_target,
        )
    )


def _record(
    result: EpisodeResult,
    proposal: OffboardingProposal,
    phase: str,
    disposition: str,
    detail: str = "",
) -> None:
    result.events.append(
        VSAREvent(
            episode=result.scenario,
            regime=result.regime.value,
            proposal_id=proposal.proposal_id,
            phase=phase,
            disposition=disposition,
            obligation_id=proposal.obligation_id,
            subject_ref=proposal.subject_ref,
            operation=proposal.operation,
            detail=detail,
        )
    )


def _run_direct(scenario: EpisodeScenario, regime: Regime) -> EpisodeResult:
    """Run self-check or audit regime.

    Both direct regimes use the same intentionally weak agent-side gate in
    these fixtures. AUDIT differs by retaining the full event record.
    """
    obligations = default_obligations()
    metrics = EpisodeMetrics()
    result = EpisodeResult(scenario.name, regime, metrics)
    persist = regime is Regime.AUDIT

    for index, obligation in enumerate(obligations):
        p = _proposal(scenario, obligation, index=index)
        now = _now_for(scenario, index)
        metrics.proposals += 1
        metrics.admitted += 1
        metrics.attempted += 1
        if persist:
            _record(result, p, "proposal", "self_admitted")
            _record(result, p, "execution", "attempted")

        if _violates_scope_or_timing(scenario, p, obligation, now=now):
            metrics.unsafe_transitions += 1

        if scenario.observation_outage and index == 0:
            metrics.unknown_results += 1
            if persist:
                _record(result, p, "verification", "unknown", "observation unavailable")
        elif scenario.lost_confirmation and index == 0:
            metrics.unknown_results += 1
            if persist:
                _record(result, p, "execution", "unknown", "confirmation lost")
            if scenario.adaptive_retry:
                metrics.proposals += 1
                metrics.admitted += 1
                metrics.attempted += 1
                metrics.replay_attempts += 1
                retry = _proposal(scenario, obligation, index=index, retry=True)
                if persist:
                    _record(result, retry, "proposal", "self_admitted")
                    _record(result, retry, "execution", "replayed")
                # The direct regime cannot exclude the first effect, so replay
                # is counted as an unsafe duplicate-risk transition.
                metrics.unsafe_transitions += 1
        else:
            metrics.verified += 1
            metrics.useful_delivery += 1
            if persist:
                _record(result, p, "verification", "verified")

    metrics.completed = metrics.verified == len(obligations)
    return result


def _run_baa(scenario: EpisodeScenario) -> EpisodeResult:
    obligations = default_obligations()
    kernel = OffboardingKernel(
        case_id="case:1",
        authority_epoch=7,
        state_version=3,
        obligations=obligations,
        unresolved_limit=1,
    )
    metrics = EpisodeMetrics()
    result = EpisodeResult(scenario.name, Regime.BAA, metrics)

    for index, obligation in enumerate(obligations):
        p = _proposal(scenario, obligation, index=index)
        now = _now_for(scenario, index)
        metrics.proposals += 1
        admission = kernel.admit(p, now=now)
        _record(result, p, "admission", admission.decision.value, admission.reason)

        if admission.decision is Decision.DENY:
            metrics.denied += 1
            metrics.assurance_interventions += 1
            continue
        if admission.decision is Decision.HOLD:
            metrics.held += 1
            metrics.assurance_interventions += 1
            continue

        metrics.admitted += 1
        capability = admission.capability
        assert capability is not None
        kernel.execute(
            capability,
            now=max(now, p.effective_at),
            case_id=p.case_id,
            authority_epoch=p.authority_epoch,
            state_version=p.state_version,
            subject_ref=p.subject_ref,
            target_system=p.target_system,
            operation=p.operation,
            request_identity=p.request_identity,
        )
        metrics.attempted += 1
        _record(result, p, "execution", "attempted")

        if scenario.observation_outage and index == 0:
            kernel.observation_unavailable(obligation.obligation_id)
            metrics.unknown_results += 1
            _record(result, p, "verification", "unknown", "observation unavailable")
        elif scenario.lost_confirmation and index == 0:
            kernel.observation_unavailable(obligation.obligation_id)
            metrics.unknown_results += 1
            _record(result, p, "execution", "unknown", "confirmation lost")
            if scenario.adaptive_retry:
                retry = _proposal(scenario, obligation, index=index, retry=True)
                metrics.proposals += 1
                retry_admission = kernel.admit(retry, now=now + 1)
                _record(
                    result,
                    retry,
                    "admission",
                    retry_admission.decision.value,
                    retry_admission.reason,
                )
                if retry_admission.decision is Decision.HOLD:
                    metrics.held += 1
                    metrics.replay_attempts += 1
                    metrics.assurance_interventions += 1
                elif retry_admission.decision is Decision.DENY:
                    metrics.denied += 1
                    metrics.replay_attempts += 1
                    metrics.assurance_interventions += 1
                else:
                    # This branch is intentionally counted as an invariant
                    # failure in case a future change admits a replay.
                    metrics.unsafe_transitions += 1
        else:
            observed = dict(obligation.expected_postcondition)
            if kernel.verify(
                obligation.obligation_id,
                observed_postcondition=observed,
            ):
                metrics.verified += 1
                metrics.useful_delivery += 1
                _record(result, p, "verification", "verified")

    metrics.completed = kernel.externally_complete()
    return result


def run_episode(scenario: EpisodeScenario, regime: Regime) -> EpisodeResult:
    if regime is Regime.BAA:
        return _run_baa(scenario)
    return _run_direct(scenario, regime)


def run_suite(
    scenarios: Iterable[EpisodeScenario] | None = None,
) -> list[EpisodeResult]:
    chosen = tuple(scenarios) if scenarios is not None else scenario_suite()
    return [
        run_episode(scenario, regime)
        for scenario in chosen
        for regime in Regime
    ]


def summarize(results: Iterable[EpisodeResult]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for result in results:
        row = summary.setdefault(
            result.regime.value,
            {
                "episodes": 0,
                "completed": 0,
                "useful_delivery": 0,
                "unsafe_transitions": 0,
                "unknown_results": 0,
                "replay_attempts": 0,
                "principal_attention": 0,
                "assurance_interventions": 0,
            },
        )
        row["episodes"] += 1
        row["completed"] += int(result.metrics.completed)
        row["useful_delivery"] += result.metrics.useful_delivery
        row["unsafe_transitions"] += result.metrics.unsafe_transitions
        row["unknown_results"] += result.metrics.unknown_results
        row["replay_attempts"] += result.metrics.replay_attempts
        row["principal_attention"] += result.metrics.principal_attention
        row["assurance_interventions"] += result.metrics.assurance_interventions
    return summary
