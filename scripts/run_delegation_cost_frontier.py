#!/usr/bin/env python3
"""Reclassify accepted BAA traces over delegation-cost ceilings."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from baa_protocol.cost_frontier import (
    architecture_grid,
    baseline_report,
    canary_grid,
    pareto_points,
    source_from_results,
)


ARCH_RESOURCE_FIELDS = (
    "max_principal_attention",
    "max_unsafe_transitions",
    "max_terminal_unresolved_results",
    "max_assurance_labor_units",
    "max_assurance_interventions",
)
CANARY_RESOURCE_FIELDS = (
    "max_assurance_interventions",
    "max_evidence_reacquisitions",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offboarding-result", required=True)
    parser.add_argument("--canary-result", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--offboarding-run-id", type=int, default=37406741476)
    parser.add_argument("--offboarding-artifact-id", type=int, default=11386984007)
    parser.add_argument("--canary-run-id", type=int, default=37466492295)
    parser.add_argument("--canary-artifact-id", type=int, default=11416980785)
    return parser.parse_args()


def _read(path: str) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_bytes()
    return json.loads(raw.decode("utf-8-sig")), hashlib.sha256(raw).hexdigest()


def _group_pareto(
    rows: list[dict[str, Any]],
    *,
    key_fields: tuple[str, ...],
    resource_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        grouped.setdefault(key, []).append(row)

    output: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        selected = pareto_points(group, resource_fields=resource_fields)
        output.extend(
            sorted(
                selected,
                key=lambda item: (
                    item["delegable_episodes"],
                    tuple(item["ceiling"][field] for field in resource_fields),
                ),
            )
        )
    return output


def main() -> None:
    args = parse_args()
    offboarding, offboarding_sha = _read(args.offboarding_result)
    canary, canary_sha = _read(args.canary_result)

    provenance = {
        "offboarding": {
            "run_id": args.offboarding_run_id,
            "artifact_id": args.offboarding_artifact_id,
            "result_sha256": f"sha256:{offboarding_sha}",
        },
        "canary": {
            "run_id": args.canary_run_id,
            "artifact_id": args.canary_artifact_id,
            "result_sha256": f"sha256:{canary_sha}",
        },
    }
    source = source_from_results(
        offboarding,
        canary,
        provenance=provenance,
    )
    arch_grid = architecture_grid(source)
    canary_cost_grid = canary_grid(source)

    result = {
        "study_version": "delegation-cost-frontier-v1",
        "provenance": provenance,
        "baseline": baseline_report(source),
        "architecture_pareto": _group_pareto(
            arch_grid,
            key_fields=("capability_level", "regime"),
            resource_fields=ARCH_RESOURCE_FIELDS,
        ),
        "canary_assurance_pareto": _group_pareto(
            canary_cost_grid,
            key_fields=("horizon", "evidence_policy"),
            resource_fields=CANARY_RESOURCE_FIELDS,
        ),
        "grid_definition": {
            "architecture": {
                "capability_levels": [0, 1, 2],
                "max_principal_attention": [0, 1],
                "max_unsafe_transitions": [0, 1, 2, 3],
                "max_terminal_unresolved_results": [0, 1],
                "max_assurance_labor_units": [0, 1, 2, 3, 4, 5],
                "max_assurance_interventions": [0, 1, 2, 3],
                "min_useful_delivery": 3,
                "require_completed": True,
            },
            "canary_assurance_mechanism": {
                "horizons": [4, 8],
                "max_assurance_interventions": list(range(18)),
                "max_evidence_reacquisitions": [0, 1, 2],
                "min_useful_delivery": 1,
                "require_completed": True,
            },
        },
        "interpretation": (
            "Retrospective budget reclassification of already accepted frozen "
            "traces. This measures the observed accounting surface and does not "
            "constitute a new prospective causal experiment."
        ),
    }

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "study_version": result["study_version"],
                "provenance": provenance,
                "architecture_c2": result["baseline"]["architecture"]["2"],
                "canary_h8": result["baseline"]["canary_assurance_mechanism"]["8"],
                "architecture_pareto_points": len(result["architecture_pareto"]),
                "canary_pareto_points": len(result["canary_assurance_pareto"]),
            },
            indent=2,
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
