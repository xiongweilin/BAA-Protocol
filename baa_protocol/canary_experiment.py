"""Deterministic delegation study for BAA canary-release promotion.

The fixtures exercise a second risk structure: progressive traffic exposure,
evidence-gated stage advancement, rollback viability, and ambiguous routing
effects. They are not estimates of production failure rates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable

from .canary_release import (
    CanaryEvidence,
    CanaryGuardrails,
    CanaryReleaseKernel,
    CanaryStagePolicy,
    TrafficProposal,
)
from .experiment import Regime
from .model import Decision


@dataclass(frozen=True)
class CanaryScenario:
    name: str
    premature_escalation: bool = False
    lost_acknowledgement: bool = False
    recovery_after_unknown: bool = False
    guardrail_regression: bool = False
    rollback_available: bool = True
    wrong_candidate_probe: bool = False


@dataclass(frozen=True)
class CanaryBudget:
    max_principal_attention: int = 0
    max_unsafe_transitions: int = 0
    max_terminal_unresolved_results: int = 0
    min_useful_delivery: int = 1
    max_assurance_labor_units: int | None = None


@dataclass
class CanaryMetrics:
    proposals: int = 0
    admitted: int = 0
    denied: int = 0
    held: int = 0
    attempted: int = 0
    verified_route_changes: int = 0
    unknown_results: int = 0
    terminal_unresolved_results: int = 0
    unsafe_transitions: int = 0
    replay_attempts: int = 0
    principal_attention: int = 0
    assurance_interventions: int = 0
    assurance_labor_units: int = 0
    useful_delivery: int = 0
    completed: bool = False


@dataclass
class CanaryEpisodeResult:
    scenario: str
    regime: Regime
    terminal_disposition: str
    metrics: CanaryMetrics
    history: list[dict[str, object]] = field(default_factory=list)


def default_stages() -> tuple[CanaryStagePolicy, ...]:
    return (
        CanaryStagePolicy(10, 60, 100),
        CanaryStagePolicy(50, 120, 200),
        CanaryStagePolicy(100, 180, 300),
    )


def default_guardrails() -> CanaryGuardrails:
    return CanaryGuardrails(
        max_candidate_error_rate=0.02,
        max_error_rate_delta=0.01,
        max_candidate_p95_latency_ms=250.0,
        max_p95_latency_ratio=1.25,
    )


def scenario_suite() -> tuple[CanaryScenario, ...]:
    return (
        CanaryScenario("clean"),
        CanaryScenario("premature-escalation-recovered", premature_escalation=True),
        CanaryScenario(
            "lost-ack-recovered",
            lost_acknowledgement=True,
            recovery_after_unknown=True,
        ),
        CanaryScenario("guardrail-rollback", guardrail_regression=True),
        CanaryScenario("terminal-insufficient-evidence", premature_escalation=True),
        CanaryScenario("rollback-unavailable", rollback_available=False),
        CanaryScenario("wrong-candidate-probe", wrong_candidate_probe=True),
    )


def _evidence(
    stage_index: int,
    *,
    sufficient: bool = True,
    regression: bool = False,
) -> CanaryEvidence:
    stage = default_stages()[stage_index]
    if sufficient:
        duration = stage.min_duration_seconds
        total = stage.min_requests
    else:
        duration = max(1, stage.min_duration_seconds // 4)
        total = max(1, stage.min_requests // 4)

    import math

    candidate = max(1, math.ceil(total * stage.weight_percent / 100))
    control = total - candidate
    if stage.weight_percent < 100 and control == 0:
        control = 1
        total = candidate + control

    return CanaryEvidence(
        experiment_id="experiment:canary:1",
        stage_index=stage_index,
        weight_percent=stage.weight_percent,
        observed_duration_seconds=duration,
        total_requests=total,
        candidate_requests=candidate,
        control_requests=control,
        candidate_error_rate=0.05 if regression else 0.005,
        control_error_rate=0.004 if control > 0 else None,
        candidate_p95_latency_ms=100.0,
        control_p95_latency_ms=95.0 if control > 0 else None,
        telemetry_complete=True,
    )


def _proposal(
    stage_index: int,
    *,
    suffix: str,
    candidate_deployment_id: str = "deployment:candidate:1",
) -> TrafficProposal:
    stage = default_stages()[stage_index]
    return TrafficProposal(
        proposal_id=f"canary:{suffix}",
        experiment_id="experiment:canary:1",
        target_id="target:product:1",
        control_release_id="release:control:1",
        candidate_deployment_id=candidate_deployment_id,
        stage_index=stage_index,
        candidate_weight_percent=stage.weight_percent,
        state_version=4,
        operation_id=f"route:{suffix}",
    )


def _kernel(*, rollback_available: bool) -> CanaryReleaseKernel:
    return CanaryReleaseKernel(
        experiment_id="experiment:canary:1",
        target_id="target:product:1",
        control_release_id="release:control:1",
        candidate_deployment_id="deployment:candidate:1",
        stages=default_stages(),
        guardrails=default_guardrails(),
        state_version=4,
        rollback_available=rollback_available,
    )


def _record(
    result: CanaryEpisodeResult,
    *,
    phase: str,
    disposition: str,
    detail: str = "",
    weight: int | None = None,
) -> None:
    item: dict[str, object] = {
        "phase": phase,
        "disposition": disposition,
    }
    if detail:
        item["detail"] = detail
    if weight is not None:
        item["candidate_weight_percent"] = weight
    result.history.append(item)


def _direct_apply(
    result: CanaryEpisodeResult,
    *,
    stage_index: int,
    safe: bool,
    detail: str = "",
) -> None:
    metrics = result.metrics
    metrics.proposals += 1
    metrics.admitted += 1
    metrics.attempted += 1
    if not safe:
        metrics.unsafe_transitions += 1
    weight = default_stages()[stage_index].weight_percent
    metrics.verified_route_changes += 1
    _record(
        result,
        phase="execution",
        disposition="verified",
        detail=detail,
        weight=weight,
    )


def _finish_promoted(result: CanaryEpisodeResult) -> None:
    result.terminal_disposition = "promoted"
    result.metrics.completed = True
    result.metrics.useful_delivery = 1


def _finish_rolled_back(result: CanaryEpisodeResult) -> None:
    result.terminal_disposition = "rolled_back"
    result.metrics.completed = True
    result.metrics.useful_delivery = 1


def _run_direct(scenario: CanaryScenario, regime: Regime) -> CanaryEpisodeResult:
    result = CanaryEpisodeResult(
        scenario=scenario.name,
        regime=regime,
        terminal_disposition="incomplete",
        metrics=CanaryMetrics(),
    )
    metrics = result.metrics

    if scenario.wrong_candidate_probe:
        metrics.proposals += 1
        metrics.admitted += 1
        metrics.attempted += 1
        metrics.unsafe_transitions += 1
        _record(
            result,
            phase="execution",
            disposition="unsafe",
            detail="wrong candidate deployment probe",
            weight=10,
        )

    if not scenario.rollback_available:
        for stage_index in range(3):
            _direct_apply(
                result,
                stage_index=stage_index,
                safe=False,
                detail="exposure increased without viable rollback",
            )
        _finish_promoted(result)
    else:
        # First exposure.
        metrics.proposals += 1
        metrics.admitted += 1
        metrics.attempted += 1
        if scenario.lost_acknowledgement:
            metrics.unknown_results += 1
            metrics.terminal_unresolved_results += 1
            _record(
                result,
                phase="execution",
                disposition="unknown",
                detail="traffic apply acknowledgement lost",
                weight=10,
            )
            metrics.proposals += 1
            metrics.admitted += 1
            metrics.attempted += 1
            metrics.replay_attempts += 1
            metrics.unsafe_transitions += 1
            _record(
                result,
                phase="execution",
                disposition="replayed",
                detail="blind replay while first route effect is unknown",
                weight=10,
            )
            if scenario.recovery_after_unknown:
                metrics.terminal_unresolved_results -= 1
                metrics.verified_route_changes += 1
                _record(
                    result,
                    phase="recovery",
                    disposition="verified",
                    detail="independent route readback",
                    weight=10,
                )
            else:
                result.terminal_disposition = "unknown"
        else:
            metrics.verified_route_changes += 1
            _record(result, phase="execution", disposition="verified", weight=10)

        if metrics.terminal_unresolved_results == 0:
            if scenario.guardrail_regression:
                _direct_apply(
                    result,
                    stage_index=1,
                    safe=False,
                    detail="escalated despite hard canary regression",
                )
                metrics.proposals += 1
                metrics.admitted += 1
                metrics.attempted += 1
                metrics.verified_route_changes += 1
                _record(
                    result,
                    phase="execution",
                    disposition="verified_restore",
                    detail="restored control after unsafe escalation",
                    weight=0,
                )
                _finish_rolled_back(result)
            elif scenario.premature_escalation:
                _direct_apply(
                    result,
                    stage_index=1,
                    safe=False,
                    detail="escalated before evidence threshold",
                )
                # One scenario receives a later public evidence update and can
                # then finish. The terminal-insufficient fixture intentionally
                # lacks that update but the weak direct regime still escalates.
                recovered = scenario.name.endswith("-recovered")
                _direct_apply(
                    result,
                    stage_index=2,
                    safe=recovered,
                    detail=(
                        "post-update final promotion"
                        if recovered
                        else "final escalation without sufficient evidence"
                    ),
                )
                _finish_promoted(result)
            else:
                _direct_apply(result, stage_index=1, safe=True)
                _direct_apply(result, stage_index=2, safe=True)
                _finish_promoted(result)

    metrics.principal_attention = int(metrics.terminal_unresolved_results > 0)
    if regime is Regime.AUDIT:
        metrics.assurance_labor_units = metrics.attempted
    return result


def _baa_execute_and_verify(
    result: CanaryEpisodeResult,
    kernel: CanaryReleaseKernel,
    proposal: TrafficProposal,
    *,
    evidence: CanaryEvidence | None,
) -> bool:
    metrics = result.metrics
    metrics.proposals += 1
    admission = kernel.admit_increase(proposal, evidence=evidence)
    _record(
        result,
        phase="admission",
        disposition=admission.decision.value,
        detail=admission.reason,
        weight=proposal.candidate_weight_percent,
    )
    if admission.decision is Decision.DENY:
        metrics.denied += 1
        metrics.assurance_interventions += 1
        return False
    if admission.decision is Decision.HOLD:
        metrics.held += 1
        metrics.assurance_interventions += 1
        return False

    metrics.admitted += 1
    capability = admission.capability
    assert capability is not None
    kernel.execute(capability)
    metrics.attempted += 1
    kernel.verify_route(
        capability,
        experiment_id=proposal.experiment_id,
        stage_index=proposal.stage_index,
        candidate_weight_percent=proposal.candidate_weight_percent,
    )
    metrics.verified_route_changes += 1
    _record(
        result,
        phase="verification",
        disposition="verified",
        weight=proposal.candidate_weight_percent,
    )
    return True


def _run_baa(scenario: CanaryScenario) -> CanaryEpisodeResult:
    result = CanaryEpisodeResult(
        scenario=scenario.name,
        regime=Regime.BAA,
        terminal_disposition="incomplete",
        metrics=CanaryMetrics(),
    )
    metrics = result.metrics
    kernel = _kernel(rollback_available=scenario.rollback_available)

    if scenario.wrong_candidate_probe:
        probe = _proposal(
            0,
            suffix="wrong-candidate",
            candidate_deployment_id="deployment:other",
        )
        metrics.proposals += 1
        admission = kernel.admit_increase(probe, evidence=None)
        _record(
            result,
            phase="admission",
            disposition=admission.decision.value,
            detail=admission.reason,
            weight=10,
        )
        if admission.decision is Decision.DENY:
            metrics.denied += 1
            metrics.assurance_interventions += 1

    first = _proposal(0, suffix="stage-0")
    metrics.proposals += 1
    first_admission = kernel.admit_increase(first, evidence=None)
    _record(
        result,
        phase="admission",
        disposition=first_admission.decision.value,
        detail=first_admission.reason,
        weight=10,
    )
    if first_admission.decision is not Decision.ADMIT:
        if first_admission.decision is Decision.DENY:
            metrics.denied += 1
        else:
            metrics.held += 1
        metrics.assurance_interventions += 1
        # No safe automated continuation exists when rollback is unavailable.
        result.terminal_disposition = "held"
        return result

    metrics.admitted += 1
    first_cap = first_admission.capability
    assert first_cap is not None
    kernel.execute(first_cap)
    metrics.attempted += 1

    if scenario.lost_acknowledgement:
        kernel.mark_unknown()
        metrics.unknown_results += 1
        metrics.terminal_unresolved_results += 1
        _record(
            result,
            phase="execution",
            disposition="unknown",
            detail="traffic apply acknowledgement lost",
            weight=10,
        )

        retry = _proposal(0, suffix="stage-0-retry")
        metrics.proposals += 1
        retry_admission = kernel.admit_increase(retry, evidence=None)
        _record(
            result,
            phase="admission",
            disposition=retry_admission.decision.value,
            detail=retry_admission.reason,
            weight=10,
        )
        if retry_admission.decision is Decision.HOLD:
            metrics.held += 1
            metrics.assurance_interventions += 1
        elif retry_admission.decision is Decision.DENY:
            metrics.denied += 1
            metrics.assurance_interventions += 1
        else:
            metrics.unsafe_transitions += 1

        if scenario.recovery_after_unknown:
            kernel.verify_route(
                first_cap,
                experiment_id=first.experiment_id,
                stage_index=0,
                candidate_weight_percent=10,
            )
            metrics.terminal_unresolved_results -= 1
            metrics.verified_route_changes += 1
            _record(
                result,
                phase="recovery",
                disposition="verified",
                detail="independent route readback",
                weight=10,
            )
        else:
            result.terminal_disposition = "unknown"
    else:
        kernel.verify_route(
            first_cap,
            experiment_id=first.experiment_id,
            stage_index=0,
            candidate_weight_percent=10,
        )
        metrics.verified_route_changes += 1
        _record(result, phase="verification", disposition="verified", weight=10)

    if metrics.terminal_unresolved_results == 0:
        second = _proposal(1, suffix="stage-1")

        if scenario.guardrail_regression:
            regression = _evidence(0, regression=True)
            metrics.proposals += 1
            admission = kernel.admit_increase(second, evidence=regression)
            _record(
                result,
                phase="admission",
                disposition=admission.decision.value,
                detail=admission.reason,
                weight=50,
            )
            if admission.decision is Decision.DENY:
                metrics.denied += 1
                metrics.assurance_interventions += 1

            restore = kernel.admit_restore(operation_id="restore:regression")
            metrics.proposals += 1
            _record(
                result,
                phase="admission",
                disposition=restore.decision.value,
                detail=restore.reason,
                weight=0,
            )
            if restore.decision is Decision.ADMIT:
                metrics.admitted += 1
                assert restore.capability is not None
                kernel.execute_restore(restore.capability)
                metrics.attempted += 1
                kernel.verify_restored(candidate_weight_percent=0)
                metrics.verified_route_changes += 1
                _record(
                    result,
                    phase="verification",
                    disposition="verified_restore",
                    weight=0,
                )
                _finish_rolled_back(result)
        elif scenario.premature_escalation:
            insufficient = _evidence(0, sufficient=False)
            metrics.proposals += 1
            admission = kernel.admit_increase(second, evidence=insufficient)
            _record(
                result,
                phase="admission",
                disposition=admission.decision.value,
                detail=admission.reason,
                weight=50,
            )
            if admission.decision is Decision.HOLD:
                metrics.held += 1
                metrics.assurance_interventions += 1
            elif admission.decision is Decision.DENY:
                metrics.denied += 1
                metrics.assurance_interventions += 1

            if scenario.name.endswith("-recovered"):
                if _baa_execute_and_verify(
                    result,
                    kernel,
                    _proposal(1, suffix="stage-1-after-evidence"),
                    evidence=_evidence(0),
                ):
                    if _baa_execute_and_verify(
                        result,
                        kernel,
                        _proposal(2, suffix="stage-2"),
                        evidence=_evidence(1),
                    ):
                        _finish_promoted(result)
            else:
                result.terminal_disposition = "held"
        else:
            if _baa_execute_and_verify(
                result,
                kernel,
                second,
                evidence=_evidence(0),
            ):
                if _baa_execute_and_verify(
                    result,
                    kernel,
                    _proposal(2, suffix="stage-2"),
                    evidence=_evidence(1),
                ):
                    _finish_promoted(result)

    metrics.principal_attention = int(metrics.terminal_unresolved_results > 0)
    return result


def run_episode(scenario: CanaryScenario, regime: Regime) -> CanaryEpisodeResult:
    if regime is Regime.BAA:
        return _run_baa(scenario)
    return _run_direct(scenario, regime)


def run_suite(
    scenarios: Iterable[CanaryScenario] | None = None,
) -> list[CanaryEpisodeResult]:
    chosen = tuple(scenarios) if scenarios is not None else scenario_suite()
    return [
        run_episode(scenario, regime)
        for scenario in chosen
        for regime in Regime
    ]


def evaluate_frontier(
    scenarios: Iterable[CanaryScenario] | None = None,
    *,
    budget: CanaryBudget | None = None,
) -> dict[str, object]:
    chosen = tuple(scenarios) if scenarios is not None else scenario_suite()
    limits = budget or CanaryBudget()
    results = run_suite(chosen)

    points: list[dict[str, object]] = []
    for result in results:
        metrics = result.metrics
        delivery = metrics.completed and metrics.useful_delivery >= limits.min_useful_delivery
        attention = metrics.principal_attention <= limits.max_principal_attention
        risk = (
            metrics.unsafe_transitions <= limits.max_unsafe_transitions
            and metrics.terminal_unresolved_results
            <= limits.max_terminal_unresolved_results
        )
        labor = (
            limits.max_assurance_labor_units is None
            or metrics.assurance_labor_units <= limits.max_assurance_labor_units
        )
        points.append(
            {
                "scenario": result.scenario,
                "regime": result.regime.value,
                "terminal_disposition": result.terminal_disposition,
                "completed": metrics.completed,
                "delivery_feasible": delivery,
                "attention_feasible": attention,
                "risk_feasible": risk,
                "assurance_labor_feasible": labor,
                "delegable": delivery and attention and risk and labor,
                **asdict(metrics),
            }
        )

    summary: dict[str, dict[str, object]] = {}
    for regime in Regime:
        rows = [row for row in points if row["regime"] == regime.value]
        delegable = [row for row in rows if row["delegable"]]
        summary[regime.value] = {
            "episodes": len(rows),
            "delegable_episodes": len(delegable),
            "delegable_task_names": sorted(str(row["scenario"]) for row in delegable),
            "completed": sum(int(bool(row["completed"])) for row in rows),
            "useful_delivery": sum(int(row["useful_delivery"]) for row in rows),
            "unsafe_transitions": sum(int(row["unsafe_transitions"]) for row in rows),
            "terminal_unresolved_results": sum(
                int(row["terminal_unresolved_results"]) for row in rows
            ),
            "principal_attention": sum(int(row["principal_attention"]) for row in rows),
            "assurance_interventions": sum(
                int(row["assurance_interventions"]) for row in rows
            ),
            "assurance_labor_units": sum(
                int(row["assurance_labor_units"]) for row in rows
            ),
            "replay_attempts": sum(int(row["replay_attempts"]) for row in rows),
        }

    return {
        "domain": "canary-release-promotion",
        "budget": asdict(limits),
        "summary": summary,
        "episodes": points,
        "qualification": (
            "Deterministic second-domain fixture only. It tests traffic-exposure "
            "and recovery semantics; it does not estimate production prevalence "
            "or model behavior."
        ),
    }
