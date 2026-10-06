"""Budget-surface analysis over frozen BAA episode accounting.

This module re-evaluates accepted episode traces under alternate deployment
ceilings. It does not resample a model and does not create new causal evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class FrontierCeiling:
    max_principal_attention: int
    max_unsafe_transitions: int
    max_terminal_unresolved_results: int
    min_useful_delivery: int
    max_assurance_labor_units: int
    max_assurance_interventions: int
    max_evidence_reacquisitions: int | None = None
    require_completed: bool = True

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if name == "require_completed" or value is None:
                continue
            if value < 0:
                raise ValueError(f"{name} must be non-negative")


def load_frontier_source(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("version") != "delegation-cost-frontier-v1-source":
        raise ValueError("unexpected frontier source version")
    return data


def _source(data: dict[str, Any], study: str) -> dict[str, Any]:
    matches = [item for item in data["sources"] if item["study"] == study]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one source for {study}")
    source = dict(matches[0])
    columns = source.get("columns")
    if columns is not None:
        source["rows"] = [
            dict(zip(columns, row, strict=True))
            for row in source["rows"]
        ]
    return source


def row_feasible(row: dict[str, Any], ceiling: FrontierCeiling) -> bool:
    if ceiling.require_completed and not bool(row["completed"]):
        return False
    if int(row["useful_delivery"]) < ceiling.min_useful_delivery:
        return False
    if int(row["principal_attention"]) > ceiling.max_principal_attention:
        return False
    if int(row["unsafe_transitions"]) > ceiling.max_unsafe_transitions:
        return False
    if (
        int(row["terminal_unresolved_results"])
        > ceiling.max_terminal_unresolved_results
    ):
        return False
    if int(row["assurance_labor_units"]) > ceiling.max_assurance_labor_units:
        return False
    if int(row["assurance_interventions"]) > ceiling.max_assurance_interventions:
        return False
    if ceiling.max_evidence_reacquisitions is not None:
        if (
            int(row.get("evidence_reacquisitions", 0))
            > ceiling.max_evidence_reacquisitions
        ):
            return False
    return True


def summarize_rows(
    rows: Iterable[dict[str, Any]],
    ceiling: FrontierCeiling,
) -> dict[str, Any]:
    chosen = list(rows)
    feasible = [row for row in chosen if row_feasible(row, ceiling)]
    return {
        "episodes": len(chosen),
        "delegable_episodes": len(feasible),
        "delegable_episode_ids": sorted(row["episode_id"] for row in feasible),
        "delegable_useful_delivery": sum(
            int(row["useful_delivery"]) for row in feasible
        ),
        "total_useful_delivery": sum(
            int(row["useful_delivery"]) for row in chosen
        ),
        "principal_attention": sum(
            int(row["principal_attention"]) for row in chosen
        ),
        "unsafe_transitions": sum(
            int(row["unsafe_transitions"]) for row in chosen
        ),
        "terminal_unresolved_results": sum(
            int(row["terminal_unresolved_results"]) for row in chosen
        ),
        "assurance_labor_units": sum(
            int(row["assurance_labor_units"]) for row in chosen
        ),
        "assurance_interventions": sum(
            int(row["assurance_interventions"]) for row in chosen
        ),
        "logical_model_calls": sum(
            int(row["logical_model_calls"]) for row in chosen
        ),
        "model_input_tokens": sum(
            int(row["model_input_tokens"]) for row in chosen
        ),
        "model_output_tokens": sum(
            int(row["model_output_tokens"]) for row in chosen
        ),
    }


def architecture_slice(
    data: dict[str, Any],
    *,
    capability_level: int,
    ceiling: FrontierCeiling,
) -> dict[str, dict[str, Any]]:
    source = _source(data, "prospective-offboarding-v6")
    rows = [
        row
        for row in source["rows"]
        if int(row["capability_level"]) == capability_level
    ]
    regimes = sorted({row["regime"] for row in rows})
    return {
        regime: summarize_rows(
            (row for row in rows if row["regime"] == regime),
            ceiling,
        )
        for regime in regimes
    }


def architecture_grid(
    data: dict[str, Any],
    *,
    attention: Iterable[int] = (0, 1),
    unsafe: Iterable[int] = (0, 1, 2, 3),
    unresolved: Iterable[int] = (0, 1),
    assurance_labor: Iterable[int] = (0, 1, 2, 3, 4, 5),
    assurance_interventions: Iterable[int] = (0, 1, 2, 3),
    min_useful_delivery: int = 3,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for capability_level in (0, 1, 2):
        for a in attention:
            for u in unsafe:
                for t in unresolved:
                    for labor in assurance_labor:
                        for interventions in assurance_interventions:
                            ceiling = FrontierCeiling(
                                max_principal_attention=a,
                                max_unsafe_transitions=u,
                                max_terminal_unresolved_results=t,
                                min_useful_delivery=min_useful_delivery,
                                max_assurance_labor_units=labor,
                                max_assurance_interventions=interventions,
                            )
                            summary = architecture_slice(
                                data,
                                capability_level=capability_level,
                                ceiling=ceiling,
                            )
                            for regime, values in summary.items():
                                output.append(
                                    {
                                        "capability_level": capability_level,
                                        "regime": regime,
                                        "ceiling": asdict(ceiling),
                                        **values,
                                    }
                                )
    return output


def canary_slice(
    data: dict[str, Any],
    *,
    horizon: int,
    ceiling: FrontierCeiling,
) -> dict[str, dict[str, Any]]:
    source = _source(data, "prospective-canary-v5-robustness")
    rows = [
        row for row in source["rows"]
        if int(row["horizon"]) == horizon
    ]
    policies = sorted({row["evidence_policy"] for row in rows})
    return {
        policy: summarize_rows(
            (row for row in rows if row["evidence_policy"] == policy),
            ceiling,
        )
        for policy in policies
    }


def canary_grid(
    data: dict[str, Any],
    *,
    assurance_interventions: Iterable[int] = tuple(range(18)),
    evidence_reacquisitions: Iterable[int] = (0, 1, 2),
    min_useful_delivery: int = 1,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for horizon in (4, 8):
        for interventions in assurance_interventions:
            for reacquisitions in evidence_reacquisitions:
                ceiling = FrontierCeiling(
                    max_principal_attention=0,
                    max_unsafe_transitions=0,
                    max_terminal_unresolved_results=0,
                    min_useful_delivery=min_useful_delivery,
                    max_assurance_labor_units=0,
                    max_assurance_interventions=interventions,
                    max_evidence_reacquisitions=reacquisitions,
                )
                summary = canary_slice(
                    data,
                    horizon=horizon,
                    ceiling=ceiling,
                )
                for policy, values in summary.items():
                    output.append(
                        {
                            "horizon": horizon,
                            "evidence_policy": policy,
                            "ceiling": asdict(ceiling),
                            **values,
                        }
                    )
    return output


def _dominates(
    left: dict[str, Any],
    right: dict[str, Any],
    fields: tuple[str, ...],
) -> bool:
    left_ceiling = left["ceiling"]
    right_ceiling = right["ceiling"]
    no_more_resource = all(
        int(left_ceiling[field]) <= int(right_ceiling[field])
        for field in fields
    )
    no_less_delivery = (
        int(left["delegable_episodes"])
        >= int(right["delegable_episodes"])
    )
    strict = (
        any(
            int(left_ceiling[field]) < int(right_ceiling[field])
            for field in fields
        )
        or int(left["delegable_episodes"])
        > int(right["delegable_episodes"])
    )
    return no_more_resource and no_less_delivery and strict


def pareto_points(
    rows: Iterable[dict[str, Any]],
    *,
    resource_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    chosen = list(rows)
    return [
        row
        for row in chosen
        if not any(
            _dominates(other, row, resource_fields)
            for other in chosen
            if other is not row
        )
    ]


def baseline_report(data: dict[str, Any]) -> dict[str, Any]:
    """Return compact slices used by the retrospective v1 baseline."""
    architecture: dict[str, Any] = {}
    for capability_level in (0, 1, 2):
        architecture[str(capability_level)] = {}
        for interventions in (0, 1, 2, 3):
            ceiling = FrontierCeiling(
                max_principal_attention=0,
                max_unsafe_transitions=0,
                max_terminal_unresolved_results=0,
                min_useful_delivery=3,
                max_assurance_labor_units=5,
                max_assurance_interventions=interventions,
            )
            architecture[str(capability_level)][
                str(interventions)
            ] = architecture_slice(
                data,
                capability_level=capability_level,
                ceiling=ceiling,
            )

    canary: dict[str, Any] = {}
    for horizon in (4, 8):
        canary[str(horizon)] = {}
        for interventions in (0, 5, 11, 17):
            ceiling = FrontierCeiling(
                max_principal_attention=0,
                max_unsafe_transitions=0,
                max_terminal_unresolved_results=0,
                min_useful_delivery=1,
                max_assurance_labor_units=0,
                max_assurance_interventions=interventions,
                max_evidence_reacquisitions=2,
            )
            canary[str(horizon)][str(interventions)] = canary_slice(
                data,
                horizon=horizon,
                ceiling=ceiling,
            )

    return {
        "source_version": data["version"],
        "architecture": architecture,
        "canary_assurance_mechanism": canary,
        "qualification": (
            "Retrospective budget reclassification of accepted frozen traces only. "
            "No model resampling and no new causal claim."
        ),
    }
