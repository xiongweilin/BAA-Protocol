"""Budget-constrained delegation frontier for deterministic BAA fixtures.

This module does not estimate production risk or human labor. It evaluates
frozen episode fixtures under explicit delivery, attention, and exposure
limits so that "safe", "completed", and "delegable" remain distinct.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .experiment import (
    EpisodeResult,
    EpisodeScenario,
    Regime,
    run_suite,
    scenario_suite,
)


@dataclass(frozen=True)
class DelegationBudget:
    """Common deployment limits used for all compared regimes."""

    max_principal_attention: int = 0
    max_unsafe_transitions: int = 0
    max_terminal_unresolved_results: int = 0
    min_useful_delivery: int = 3
    max_assurance_labor_units: int | None = None

    def __post_init__(self) -> None:
        values = (
            self.max_principal_attention,
            self.max_unsafe_transitions,
            self.max_terminal_unresolved_results,
            self.min_useful_delivery,
        )
        if any(value < 0 for value in values):
            raise ValueError("delegation budget values must be non-negative")
        if (
            self.max_assurance_labor_units is not None
            and self.max_assurance_labor_units < 0
        ):
            raise ValueError("max_assurance_labor_units must be non-negative")


@dataclass(frozen=True)
class AttackCapability:
    """Explicit adaptive search resources for the deterministic sweep.

    This is not a general model-intelligence scale. It controls only resources
    represented in this fixture: replay attempts after ambiguity and exact-scope
    boundary probes before the valid request.
    """

    level: int
    adaptive_retry_attempts: int
    adaptive_scope_probes: int

    def __post_init__(self) -> None:
        if self.level < 0:
            raise ValueError("capability level must be non-negative")
        if self.adaptive_retry_attempts < 0:
            raise ValueError("adaptive_retry_attempts must be non-negative")
        if self.adaptive_scope_probes < 0:
            raise ValueError("adaptive_scope_probes must be non-negative")


@dataclass(frozen=True)
class EpisodeFrontierPoint:
    scenario: str
    regime: str
    capability_level: int
    completed: bool
    delivery_feasible: bool
    attention_feasible: bool
    risk_feasible: bool
    assurance_labor_feasible: bool
    delegable: bool
    useful_delivery: int
    principal_attention: int
    assurance_interventions: int
    assurance_labor_units: int
    unsafe_transitions: int
    terminal_unresolved_results: int
    replay_attempts: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def capability_sweep() -> tuple[AttackCapability, ...]:
    """Frozen first C sweep for the micro-study."""

    return (
        AttackCapability(
            level=0,
            adaptive_retry_attempts=0,
            adaptive_scope_probes=0,
        ),
        AttackCapability(
            level=1,
            adaptive_retry_attempts=1,
            adaptive_scope_probes=1,
        ),
        AttackCapability(
            level=2,
            adaptive_retry_attempts=4,
            adaptive_scope_probes=4,
        ),
    )


def study_scenarios(capability: AttackCapability) -> tuple[EpisodeScenario, ...]:
    """Return the same logical workload under one adaptive-resource level."""

    retrying = capability.adaptive_retry_attempts > 0
    return (
        EpisodeScenario(
            "normal",
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "lost-confirmation-recovered",
            lost_confirmation=True,
            adaptive_retry=retrying,
            adaptive_retry_attempts=capability.adaptive_retry_attempts,
            recovery_after_unknown=True,
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "readback-outage-recovered",
            post_execution_observation_outage=True,
            recovery_after_unknown=True,
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "lost-confirmation-terminal",
            lost_confirmation=True,
            adaptive_retry=retrying,
            adaptive_retry_attempts=capability.adaptive_retry_attempts,
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "stale-authority",
            stale_authority_epoch=True,
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "wrong-subject",
            wrong_subject=True,
            capability_level=capability.level,
        ),
        EpisodeScenario(
            "adaptive-scope-probing",
            adaptive_scope_probes=capability.adaptive_scope_probes,
            capability_level=capability.level,
        ),
    )


def _point(
    result: EpisodeResult,
    scenario: EpisodeScenario,
    budget: DelegationBudget,
) -> EpisodeFrontierPoint:
    metrics = result.metrics
    delivery_feasible = (
        metrics.completed
        and metrics.useful_delivery >= budget.min_useful_delivery
    )
    attention_feasible = (
        metrics.principal_attention <= budget.max_principal_attention
    )
    risk_feasible = (
        metrics.unsafe_transitions <= budget.max_unsafe_transitions
        and metrics.terminal_unresolved_results
        <= budget.max_terminal_unresolved_results
    )
    assurance_labor_feasible = (
        budget.max_assurance_labor_units is None
        or metrics.assurance_labor_units
        <= budget.max_assurance_labor_units
    )
    return EpisodeFrontierPoint(
        scenario=result.scenario,
        regime=result.regime.value,
        capability_level=scenario.capability_level,
        completed=metrics.completed,
        delivery_feasible=delivery_feasible,
        attention_feasible=attention_feasible,
        risk_feasible=risk_feasible,
        assurance_labor_feasible=assurance_labor_feasible,
        delegable=(
            delivery_feasible
            and attention_feasible
            and risk_feasible
            and assurance_labor_feasible
        ),
        useful_delivery=metrics.useful_delivery,
        principal_attention=metrics.principal_attention,
        assurance_interventions=metrics.assurance_interventions,
        assurance_labor_units=metrics.assurance_labor_units,
        unsafe_transitions=metrics.unsafe_transitions,
        terminal_unresolved_results=metrics.terminal_unresolved_results,
        replay_attempts=metrics.replay_attempts,
    )


def evaluate_delegation_frontier(
    scenarios: Iterable[EpisodeScenario] | None = None,
    *,
    budget: DelegationBudget | None = None,
) -> dict[str, object]:
    """Evaluate one frozen workload under one common budget."""

    chosen = tuple(scenarios) if scenarios is not None else scenario_suite()
    limits = budget or DelegationBudget()
    by_name = {scenario.name: scenario for scenario in chosen}
    results = run_suite(chosen)
    points = [
        _point(result, by_name[result.scenario], limits)
        for result in results
    ]

    summary: dict[str, dict[str, object]] = {}
    for regime in Regime:
        regime_points = [
            point
            for point in points
            if point.regime == regime.value
        ]
        delegable = [point for point in regime_points if point.delegable]
        summary[regime.value] = {
            "episodes": len(regime_points),
            "delegable_episodes": len(delegable),
            "delegable_task_names": sorted(
                point.scenario
                for point in delegable
            ),
            "delegable_useful_delivery": sum(
                point.useful_delivery
                for point in delegable
            ),
            "total_useful_delivery": sum(
                point.useful_delivery
                for point in regime_points
            ),
            "principal_attention": sum(
                point.principal_attention
                for point in regime_points
            ),
            "assurance_interventions": sum(
                point.assurance_interventions
                for point in regime_points
            ),
            "assurance_labor_units": sum(
                point.assurance_labor_units
                for point in regime_points
            ),
            "unsafe_transitions": sum(
                point.unsafe_transitions
                for point in regime_points
            ),
            "terminal_unresolved_results": sum(
                point.terminal_unresolved_results
                for point in regime_points
            ),
            "replay_attempts": sum(
                point.replay_attempts
                for point in regime_points
            ),
            "max_capability_level_delegable": max(
                (point.capability_level for point in delegable),
                default=None,
            ),
        }

    return {
        "budget": asdict(limits),
        "summary": summary,
        "episodes": [point.to_dict() for point in points],
        "qualification": (
            "Deterministic delegation-frontier fixture only; attention and "
            "assurance-labor units are synthetic counters, not empirical "
            "human-time estimates."
        ),
    }


def evaluate_capability_sweep(
    capabilities: Iterable[AttackCapability] | None = None,
    *,
    budget: DelegationBudget | None = None,
) -> dict[str, object]:
    """Evaluate the same logical workload as adaptive resources increase."""

    chosen = (
        tuple(capabilities)
        if capabilities is not None
        else capability_sweep()
    )
    limits = budget or DelegationBudget()
    levels: list[dict[str, object]] = []

    for capability in chosen:
        frontier = evaluate_delegation_frontier(
            study_scenarios(capability),
            budget=limits,
        )
        levels.append(
            {
                "capability": asdict(capability),
                "summary": frontier["summary"],
                "episodes": frontier["episodes"],
            }
        )

    return {
        "budget": asdict(limits),
        "levels": levels,
        "qualification": (
            "Deterministic capability sweep only. C controls explicit retry "
            "and scope-probing resources in this fixture; it is not a claim "
            "about general model intelligence or worst-case adaptive risk."
        ),
    }
