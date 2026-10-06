#!/usr/bin/env python3
"""Run the preregistered prospective delegation cost-frontier v1 study."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from baa_protocol.progress import ProgressModelClient
from baa_protocol.prospective_canary_evidence_horizon_study import (
    run_canary_evidence_horizon_study,
)
from baa_protocol.prospective_canary_study import (
    canary_model_client,
    load_canary_workload,
    run_canary_study,
)
from baa_protocol.prospective_cost_frontier_study import (
    assemble_prospective_cost_frontier_result,
    common_sampling_budget,
)
from baa_protocol.prospective_transport import ReplaySafeTransportClient


EXPECTED_WORKLOAD_SHA256 = "TO_BE_FROZEN"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generator",
        default="scripts/generate_prospective_delegation_cost_frontier_v1.py",
    )
    parser.add_argument("--workload-output", required=True)
    parser.add_argument("--gateway-base", default="http://127.0.0.1:4101")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--heartbeat-seconds", type=float, default=30.0)
    return parser.parse_args()


def _panel_client(args: argparse.Namespace):
    raw = canary_model_client(
        base_url=args.gateway_base,
        model_id=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    return ReplaySafeTransportClient(raw, max_retries=1)


def _attach_transport(result: dict, client: ReplaySafeTransportClient) -> None:
    result["physical_sampling"].update(
        {
            "http_attempts": client.http_attempts,
            "transport_failures_seen": client.transport_failures_seen,
            "transport_retries": client.transport_retries,
            "recovered_transport_calls": client.recovered_transport_calls,
        }
    )


def main() -> None:
    args = parse_args()
    workload_path = Path(args.workload_output)
    workload_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            args.generator,
            "--output",
            str(workload_path),
        ],
        check=True,
    )
    payload = workload_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_WORKLOAD_SHA256:
        raise RuntimeError(
            "workload hash mismatch: "
            f"expected={EXPECTED_WORKLOAD_SHA256} actual={digest}"
        )

    version, episodes = load_canary_workload(workload_path)
    if version != "prospective-delegation-cost-frontier-v1":
        raise RuntimeError(f"unexpected workload version: {version}")
    if len(episodes) != 24:
        raise RuntimeError(f"unexpected workload size: {len(episodes)}")

    budget = common_sampling_budget()

    architecture_transport = _panel_client(args)
    with ProgressModelClient(
        architecture_transport,
        label="prospective-cost-frontier-v1:architecture",
        heartbeat_seconds=args.heartbeat_seconds,
    ) as architecture_client:
        architecture = run_canary_study(
            architecture_client,
            episodes,
            budget=budget,
        )
    _attach_transport(architecture, architecture_transport)

    evidence_transport = _panel_client(args)
    with ProgressModelClient(
        evidence_transport,
        label="prospective-cost-frontier-v1:evidence-recovery",
        heartbeat_seconds=args.heartbeat_seconds,
    ) as evidence_client:
        evidence = run_canary_evidence_horizon_study(
            evidence_client,
            episodes,
            budget=budget,
        )
    _attach_transport(evidence, evidence_transport)

    result = assemble_prospective_cost_frontier_result(
        architecture,
        evidence,
        model_id=args.model,
        model_interface="function_tool",
    )
    result["source_workload_version"] = version
    result["source_workload_sha256"] = digest
    result["sampling_blocks"] = {
        "architecture": architecture["physical_sampling"],
        "evidence_recovery": evidence["physical_sampling"],
    }

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
                "source_workload_version": version,
                "source_workload_sha256": digest,
                "model_id": result["model_id"],
                "model_interface": result["model_interface"],
                "sampling_blocks": result["sampling_blocks"],
                "architecture_strict_safe": result[
                    "architecture_panel"
                ]["strict_safe"],
                "evidence_endpoints": result[
                    "evidence_recovery_panel"
                ]["endpoints"],
            },
            indent=2,
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
