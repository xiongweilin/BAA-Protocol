"""Budget-constrained delegation frontier for deterministic BAA fixtures.

This module does not estimate production risk or human labor. It evaluates the
existing deterministic episode fixtures under explicit attention and exposure
limits so that "safe" and "completed" cannot be conflated with "delegable".
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


@dataclass(frozen=True)
class EpisodeFrontierPoint:
    scenario: str
    regime: str
    capability_level: int
    completed: bool
    attention_feasible: bool
    risk_feasible: bool
    delegable: bool
    useful_delivery: int
    principal_attention: int
    assurance_interventions: int
    unsafe_transitions: int
    terminal_unresolved_results: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _point(
    result: EpisodeResult,
    scenario: EpisodeScenario,
    budget: DelegationBudget,
) -> EpisodeFrontierPoint:
    metrics = result.metrics
    attention_feasible = metrics.principal_attention <= budget.max_principal_attention
    risk_feasible = (
        metrics.unsafe_transitions <= budget.max_unsafe_transitions
        and metrics.terminal_unresolved_results
        <= budget.max_terminal_unresolved_results
    )
    return EpisodeFrontierPoint(
        scenario=result.scenario,
        regime=result.regime.value,
        capability_level=scenario.capability_level,
        completed=metrics.completed,
        attention_feasible=attention_feasible,
        risk_feasible=risk_feasible,
        delegable=metrics.completed and attention_feasible and risk_feasible,
        useful_delivery=metrics.useful_delivery,
        principal_attention=metrics.principal_attention,
        assurance_interventions=metrics.assurance_interventions,
        unsafe_transitions=metrics.unsafe_transitions,
        terminal_unresolved_results=metrics.terminal_unresolved_results,
    )


def evaluate_delegation_frontier(
    scenarios: Iterable[EpisodeScenario] | None = None,
    *,
    budget: DelegationBudget | None = None,
) -> dict[str, object]:
    """Evaluate the same deterministic workload under one common budget.

    A task instance is counted as delegable only when it both completes and
    remains within the common attention/risk limits. Automatic assurance
    interventions are reported separately and are not silently converted into
    human labor.
    """

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
        regime_points = [point for point in points if point.regime == regime.value]
        delegable = [point for point in regime_points if point.delegable]
        summary[regime.value] = {
            "episodes": len(regime_points),
            "delegable_episodes": len(delegable),
            "delegable_task_names": sorted(point.scenario for point in delegable),
            "delegable_useful_delivery": sum(
                point.useful_delivery for point in delegable
            ),
            "total_useful_delivery": sum(
                point.useful_delivery for point in regime_points
            ),
            "principal_attention": sum(
                point.principal_attention for point in regime_points
            ),
            "assurance_interventions": sum(
                point.assurance_interventions for point in regime_points
            ),
            "unsafe_transitions": sum(
                point.unsafe_transitions for point in regime_points
            ),
            "terminal_unresolved_results": sum(
                point.terminal_unresolved_results for point in regime_points
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
            "Deterministic delegation-frontier fixture only; attention units "
            "and assurance interventions are not empirical human-time estimates."
        ),
    }
