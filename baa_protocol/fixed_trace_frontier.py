"""Fixed-trace Pareto-envelope analysis for accepted delegation studies.

This module deliberately performs *retrospective reclassification* of already
observed episode traces.  It does not model a budget-aware agent and therefore
must not be interpreted as a policy-optimal frontier.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True, order=True)
class CostVector:
    """Separate, non-interchangeable cost coordinates."""

    principal_attention: int
    unsafe_transitions: int
    assurance_labor_units: int
    assurance_interventions: int

    def __post_init__(self) -> None:
        if min(asdict(self).values()) < 0:
            raise ValueError("cost coordinates must be non-negative")

    def add(self, other: "CostVector") -> "CostVector":
        return CostVector(
            principal_attention=self.principal_attention
            + other.principal_attention,
            unsafe_transitions=self.unsafe_transitions + other.unsafe_transitions,
            assurance_labor_units=self.assurance_labor_units
            + other.assurance_labor_units,
            assurance_interventions=self.assurance_interventions
            + other.assurance_interventions,
        )


ZERO_COST = CostVector(0, 0, 0, 0)


@dataclass(frozen=True)
class TraceOutcome:
    """One observed regime/episode outcome from an accepted study."""

    study: str
    capability_level: int
    episode_id: str
    logical_name: str
    study_group: str
    regime: str
    completed: bool
    principal_attention: int
    unsafe_transitions: int
    terminal_unresolved_results: int
    assurance_labor_units: int
    assurance_interventions: int
    logical_model_calls: int = 0
    model_input_tokens: int = 0
    model_output_tokens: int = 0

    @property
    def cost(self) -> CostVector:
        return CostVector(
            principal_attention=self.principal_attention,
            unsafe_transitions=self.unsafe_transitions,
            assurance_labor_units=self.assurance_labor_units,
            assurance_interventions=self.assurance_interventions,
        )

    @property
    def work_eligible(self) -> bool:
        """Whether the trace may contribute one completed work unit.

        Terminally unresolved traces are excluded from the envelope even if a
        source harness were ever to label them completed.  Risk, attention and
        assurance costs remain coordinates rather than hard exclusions.
        """

        return self.completed and self.terminal_unresolved_results == 0


@dataclass(frozen=True)
class EnvelopePoint:
    principal_attention: int
    unsafe_transitions: int
    assurance_labor_units: int
    assurance_interventions: int
    completed_work: int

    @property
    def cost(self) -> CostVector:
        return CostVector(
            self.principal_attention,
            self.unsafe_transitions,
            self.assurance_labor_units,
            self.assurance_interventions,
        )

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def _dominates(
    left_cost: CostVector,
    left_work: int,
    right_cost: CostVector,
    right_work: int,
) -> bool:
    left_values = (
        left_cost.principal_attention,
        left_cost.unsafe_transitions,
        left_cost.assurance_labor_units,
        left_cost.assurance_interventions,
    )
    right_values = (
        right_cost.principal_attention,
        right_cost.unsafe_transitions,
        right_cost.assurance_labor_units,
        right_cost.assurance_interventions,
    )
    weak_cost = all(a <= b for a, b in zip(left_values, right_values))
    weak_work = left_work >= right_work
    strict = left_values != right_values or left_work != right_work
    return weak_cost and weak_work and strict


def _pareto_prune(states: Mapping[CostVector, int]) -> dict[CostVector, int]:
    """Drop states dominated on all four costs and completed work."""

    items = list(states.items())
    kept: dict[CostVector, int] = {}
    for index, (cost, work) in enumerate(items):
        if any(
            index != other_index
            and _dominates(other_cost, other_work, cost, work)
            for other_index, (other_cost, other_work) in enumerate(items)
        ):
            continue
        kept[cost] = max(work, kept.get(cost, -1))
    return kept


def fixed_trace_envelope(outcomes: Iterable[TraceOutcome]) -> tuple[EnvelopePoint, ...]:
    """Return the exact nondominated envelope over observed completed traces.

    Each eligible observed episode may contribute at most one work unit.
    Principal attention, unsafe transitions, human assurance labor, and
    automated assurance interventions remain separate coordinates.
    """

    eligible = [outcome for outcome in outcomes if outcome.work_eligible]
    states: dict[CostVector, int] = {ZERO_COST: 0}

    for outcome in eligible:
        additions: dict[CostVector, int] = {}
        for cost, work in states.items():
            new_cost = cost.add(outcome.cost)
            additions[new_cost] = max(additions.get(new_cost, -1), work + 1)
        merged = dict(states)
        for cost, work in additions.items():
            merged[cost] = max(merged.get(cost, -1), work)
        states = _pareto_prune(merged)

    points = [
        EnvelopePoint(
            principal_attention=cost.principal_attention,
            unsafe_transitions=cost.unsafe_transitions,
            assurance_labor_units=cost.assurance_labor_units,
            assurance_interventions=cost.assurance_interventions,
            completed_work=work,
        )
        for cost, work in states.items()
    ]
    return tuple(
        sorted(
            points,
            key=lambda point: (
                point.principal_attention,
                point.unsafe_transitions,
                point.assurance_labor_units,
                point.assurance_interventions,
                -point.completed_work,
            ),
        )
    )


def _int_metric(metrics: Mapping[str, Any], name: str) -> int:
    value = metrics.get(name, 0)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"metric {name!r} must be an integer")
    return value


def outcomes_from_result(
    study: str,
    result: Mapping[str, Any],
) -> tuple[TraceOutcome, ...]:
    """Normalize either accepted offboarding or canary result JSON."""

    rows: list[TraceOutcome] = []
    levels = result.get("levels")
    if not isinstance(levels, list):
        raise ValueError("result requires a levels array")

    for level in levels:
        if not isinstance(level, Mapping):
            raise ValueError("level must be an object")
        capability = level.get("capability")
        if not isinstance(capability, Mapping):
            raise ValueError("level requires capability metadata")
        capability_level = capability.get("level")
        if isinstance(capability_level, bool) or not isinstance(capability_level, int):
            raise ValueError("capability level must be an integer")

        episodes = level.get("episodes")
        if not isinstance(episodes, list):
            raise ValueError("level requires an episodes array")
        for episode in episodes:
            if not isinstance(episode, Mapping):
                raise ValueError("episode row must be an object")
            metrics = episode.get("metrics")
            if not isinstance(metrics, Mapping):
                raise ValueError("episode row requires metrics")
            completed = episode.get("completed")
            if not isinstance(completed, bool):
                raise ValueError("completed must be boolean")
            regime = episode.get("regime")
            if not isinstance(regime, str) or not regime:
                raise ValueError("regime is required")
            rows.append(
                TraceOutcome(
                    study=study,
                    capability_level=capability_level,
                    episode_id=str(episode.get("episode_id", "")),
                    logical_name=str(episode.get("logical_name", "")),
                    study_group=str(episode.get("study_group", "unspecified")),
                    regime=regime,
                    completed=completed,
                    principal_attention=_int_metric(metrics, "principal_attention"),
                    unsafe_transitions=_int_metric(metrics, "unsafe_transitions"),
                    terminal_unresolved_results=_int_metric(
                        metrics, "terminal_unresolved_results"
                    ),
                    assurance_labor_units=_int_metric(
                        metrics, "assurance_labor_units"
                    ),
                    assurance_interventions=_int_metric(
                        metrics, "assurance_interventions"
                    ),
                    logical_model_calls=int(episode.get("model_calls", 0) or 0),
                    model_input_tokens=int(episode.get("model_input_tokens", 0) or 0),
                    model_output_tokens=int(episode.get("model_output_tokens", 0) or 0),
                )
            )
    return tuple(rows)


def load_result(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("result JSON must be an object")
    return value


def analyze_fixed_trace_results(
    named_results: Sequence[tuple[str, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Compute per-study and pooled envelopes for every C/regime pair."""

    all_rows: list[TraceOutcome] = []
    source_metadata: list[dict[str, Any]] = []
    for study, result in named_results:
        rows = outcomes_from_result(study, result)
        all_rows.extend(rows)
        source_metadata.append(
            {
                "study": study,
                "workload_version": result.get("workload_version"),
                "model_id": result.get("model_id"),
                "model_interface": result.get("model_interface"),
                "physical_sampling": result.get("physical_sampling"),
            }
        )

    studies = sorted({row.study for row in all_rows})
    capability_levels = sorted({row.capability_level for row in all_rows})
    regimes = sorted({row.regime for row in all_rows})

    def serialize(rows: Sequence[TraceOutcome]) -> dict[str, Any]:
        envelope = fixed_trace_envelope(rows)
        completed_resolved = [row for row in rows if row.work_eligible]
        return {
            "observed_episode_rows": len(rows),
            "completed_terminal_resolved_rows": len(completed_resolved),
            "attention_values_observed": sorted(
                {row.principal_attention for row in completed_resolved}
            ),
            "logical_model_calls_reported": sum(
                row.logical_model_calls for row in rows
            ),
            "note_on_model_calls": (
                "Logical model calls are reported descriptively only. They are not "
                "an additive portfolio cost because accepted harnesses may share "
                "physical/adaptive samples across logical rows."
            ),
            "envelope": [point.to_dict() for point in envelope],
        }

    by_study: dict[str, Any] = {}
    for study in studies:
        by_study[study] = {}
        for capability_level in capability_levels:
            key = f"C{capability_level}"
            by_study[study][key] = {}
            for regime in regimes:
                selected = [
                    row
                    for row in all_rows
                    if row.study == study
                    and row.capability_level == capability_level
                    and row.regime == regime
                ]
                if selected:
                    by_study[study][key][regime] = serialize(selected)

    pooled: dict[str, Any] = {}
    for capability_level in capability_levels:
        key = f"C{capability_level}"
        pooled[key] = {}
        for regime in regimes:
            selected = [
                row
                for row in all_rows
                if row.capability_level == capability_level and row.regime == regime
            ]
            if selected:
                pooled[key][regime] = serialize(selected)

    return {
        "analysis_kind": "fixed-trace-feasible-envelope",
        "interpretation_limit": (
            "Retrospective reclassification of accepted observed traces. This is "
            "not a budget-aware policy-optimal frontier and does not estimate how "
            "agent behavior would change under different budgets."
        ),
        "cost_axes": {
            "A": "principal_attention",
            "R": "unsafe_transitions",
            "L": "human assurance_labor_units",
            "I": "automated assurance_interventions",
            "W": "completed terminal-resolved episode count",
        },
        "source_results": source_metadata,
        "by_study": by_study,
        "pooled": pooled,
    }
