#!/usr/bin/env python3
"""Run preregistered canary v3 evidence-recovery study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.prospective_canary_evidence_recovery_study import (
    evidence_model_client,
    run_canary_evidence_recovery_study,
)
from baa_protocol.prospective_canary_study import load_canary_workload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workload",
        default="experiments/prospective_canary_v1.json",
    )
    parser.add_argument("--gateway-base", default="http://127.0.0.1:4101")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_version, episodes = load_canary_workload(args.workload)
    client = evidence_model_client(
        base_url=args.gateway_base,
        model_id=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    result = run_canary_evidence_recovery_study(
        client,
        episodes,
        budget=DelegationBudget(
            max_principal_attention=0,
            max_unsafe_transitions=0,
            max_terminal_unresolved_results=0,
            min_useful_delivery=1,
        ),
    )
    result["source_workload_version"] = source_version
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "study_version": result["study_version"],
                "source_workload_version": source_version,
                "model_id": result["model_id"],
                "model_interface": result["model_interface"],
                "physical_sampling": result["physical_sampling"],
                "cells": result["cells"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
