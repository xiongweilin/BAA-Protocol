"""Run the frozen P2 read-only maintenance proposal experiment.

No product URLs or network requests are made except optional *local model*
gateway generation. Study input is pinned, sanitized P7 product evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from baa_protocol.p2_readonly_maintenance_model import (
    load_cases, make_client, run_pilot,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workload", type=Path,
        default=Path("experiments/p2_readonly_maintenance_v1.json"),
    )
    parser.add_argument("--gateway-base", default="http://127.0.0.1:4101")
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-calls", type=int, default=96)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    args = parser.parse_args()
    # Exact origin is intentionally pinned: a string-prefix check would
    # allow malformed authority/userinfo URLs to route outside loopback.
    if args.gateway_base.rstrip("/") != "http://127.0.0.1:4101":
        parser.error("v1 model gateway must be exactly http://127.0.0.1:4101")
    if not (1 <= args.max_calls <= 96):
        parser.error("max-calls must be bounded to 1..96")

    workload = load_cases(args.workload)
    client = make_client(
        base_url=args.gateway_base, model_id=args.model,
        timeout_s=args.timeout_seconds,
    )
    result = run_pilot(client, workload, max_calls=args.max_calls)
    result["model_id"] = client.model_id
    result["tool_interface"] = client.interface_mode
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    # Errors invalidate qualification; they are still archived as evidence.
    if result["model_call_error_types"]:
        raise SystemExit("P2 model interface unqualified: errors archived")


if __name__ == "__main__":
    main()
