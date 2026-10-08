#!/usr/bin/env python3
"""Qualify or execute frozen P2 read-only maintenance replay.

This program has NO live product connector. Its sole optional network access
is a loopback Responses-compatible model gateway; provider access is neither
required nor accepted. It never sends hidden origin/reference fields.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from baa_protocol.maintenance_model_replay import (
    HORIZONS,
    REGIMES,
    VERSION,
    decision_tool_schema,
    load_maintenance_windows,
    maintenance_prompt,
    run_maintenance_model_replay,
)
from baa_protocol.progress import ProgressModelClient
from baa_protocol.prospective_transport import ReplaySafeTransportClient
from baa_protocol.prospective_types import ResponsesGatewayClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKLOAD = ROOT / "experiments" / "p2_readonly_maintenance_replay_v1.json"


def args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", type=Path, default=DEFAULT_WORKLOAD)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qualify-only", action="store_true")
    parser.add_argument("--gateway-base", default="http://127.0.0.1:4101")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--heartbeat-seconds", type=float, default=30.0)
    return parser


def main() -> None:
    args = args_parser().parse_args()
    windows = load_maintenance_windows(args.workload)
    # Structural privacy qualification before any model call.
    for horizon in HORIZONS:
        if maintenance_prompt(windows[1], horizon) != maintenance_prompt(windows[3], horizon):
            raise ValueError("frozen indistinguishable-cause prompts diverged")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": VERSION,
        "qualification": "workload_structural_only",
        "case_count": len(windows),
        "sample_horizons": list(HORIZONS),
        "regimes": [x.value for x in REGIMES],
        "expected_physical_calls": len(windows) * len(HORIZONS),
        "expected_replayed_rows": len(windows) * len(HORIZONS) * len(REGIMES),
        "source_artifacts": sorted({w.artifact_id for w in windows}),
        "source_archive_sha256": sorted({w.archive_sha256 for w in windows}),
        "origin_blind_pair_qualified": True,
        "live_business_systems_contacted": False,
        "causal_P2_effect_estimated": False,
    }
    if args.qualify_only:
        args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(manifest, sort_keys=True))
        return

    gateway = urlparse(args.gateway_base)
    if gateway.scheme != "http" or gateway.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("P2 model evaluation permits only loopback model gateways")
    if args.timeout_seconds <= 0:
        raise ValueError("model timeout must be positive")

    raw_client = ResponsesGatewayClient(
        base_url=args.gateway_base,
        model_id=args.model,
        timeout_seconds=args.timeout_seconds,
        proposal_tool=True,
        tool_name="submit_maintenance_disposition",
        tool_schema=decision_tool_schema(),
        tool_description="Submit one read-only diagnostic disposition; never perform service effects.",
    )
    transport = ReplaySafeTransportClient(raw_client, max_retries=1)
    try:
        with ProgressModelClient(
            transport, label=VERSION, heartbeat_seconds=args.heartbeat_seconds
        ) as client:
            result = run_maintenance_model_replay(client, windows)
    except Exception as exc:
        # No exception text: remote provider errors may carry sensitive input.
        invalid = {
            **manifest,
            "qualification": "failed",
            "failure_class": type(exc).__name__,
            "model_sampling_not_complete": True,
            "results_not_valid_for_regime_comparison": True,
            "http_attempts": transport.http_attempts,
            "transport_retries": transport.transport_retries,
        }
        args.output.write_text(json.dumps(invalid, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise SystemExit("P2 sampling invalid: see sanitized failure_class in output") from None

    qualified = {
        **manifest,
        **result,
        "qualification": "model_interface_and_finite_replay_qualified",
        "http_attempts": transport.http_attempts,
        "transport_failures_seen": transport.transport_failures_seen,
        "transport_retries": transport.transport_retries,
        "recovered_transport_calls": transport.recovered_transport_calls,
    }
    args.output.write_text(json.dumps(qualified, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "version": VERSION,
        "qualification": qualified["qualification"],
        "physical_model_samples": qualified["physical_model_samples"],
        "summary": qualified["summary"],
        "causal_P2_effect_estimated": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
