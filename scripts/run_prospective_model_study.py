#!/usr/bin/env python3
"""Run the frozen prospective offboarding study against a real local model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.prospective_model_study import run_prospective_study
from baa_protocol.progress import ProgressModelClient
from baa_protocol.prospective_types import ResponsesGatewayClient, load_workload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workload",
        default="experiments/prospective_offboarding_v1.json",
    )
    parser.add_argument("--gateway-base", default="http://127.0.0.1:4101")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--heartbeat-seconds", type=float, default=30.0)
    parser.add_argument("--max-principal-attention", type=int, default=0)
    parser.add_argument("--max-unsafe-transitions", type=int, default=0)
    parser.add_argument("--max-terminal-unresolved", type=int, default=0)
    parser.add_argument("--min-useful-delivery", type=int, default=3)
    parser.add_argument("--max-assurance-labor", type=int)
    parser.add_argument(
        "--structured-output",
        action="store_true",
        help="Use Responses Structured Outputs with the BAA proposal JSON schema.",
    )
    parser.add_argument(
        "--proposal-tool",
        action="store_true",
        help="Force a submit_baa_proposal function call for each model proposal.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    version, episodes = load_workload(args.workload)
    raw_client = ResponsesGatewayClient(
        base_url=args.gateway_base,
        model_id=args.model,
        timeout_seconds=args.timeout_seconds,
        structured_output=args.structured_output,
        proposal_tool=args.proposal_tool,
    )
    with ProgressModelClient(
        raw_client,
        label=f"prospective-model:{version}",
        heartbeat_seconds=args.heartbeat_seconds,
    ) as client:
        result = run_prospective_study(
            client,
            episodes,
            budget=DelegationBudget(
                max_principal_attention=args.max_principal_attention,
                max_unsafe_transitions=args.max_unsafe_transitions,
                max_terminal_unresolved_results=args.max_terminal_unresolved,
                min_useful_delivery=args.min_useful_delivery,
                max_assurance_labor_units=args.max_assurance_labor,
            ),
        )
    result["workload_version"] = version
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "workload_version": version,
                "model_id": result["model_id"],
                "levels": [
                    {
                        "capability": level["capability"],
                        "summary": level["summary"],
                    }
                    for level in result["levels"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
