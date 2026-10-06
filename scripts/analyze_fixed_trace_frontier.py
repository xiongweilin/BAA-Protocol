#!/usr/bin/env python3
"""Compute fixed-trace feasible envelopes from accepted BAA result JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baa_protocol.fixed_trace_frontier import (
    analyze_fixed_trace_results,
    load_result,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result",
        action="append",
        required=True,
        metavar="LABEL=PATH",
        help="Accepted result JSON; repeat for multiple studies.",
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_named_result(value: str) -> tuple[str, Path]:
    label, separator, raw_path = value.partition("=")
    if not separator or not label.strip() or not raw_path.strip():
        raise ValueError("--result must use LABEL=PATH")
    return label.strip(), Path(raw_path.strip())


def main() -> None:
    args = parse_args()
    named_results = [
        (label, load_result(path))
        for label, path in (parse_named_result(value) for value in args.result)
    ]
    analysis = analyze_fixed_trace_results(named_results)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(analysis, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    compact: dict[str, object] = {
        "analysis_kind": analysis["analysis_kind"],
        "interpretation_limit": analysis["interpretation_limit"],
        "pooled": {},
    }
    for capability, regimes in analysis["pooled"].items():
        compact["pooled"][capability] = {
            regime: {
                "completed_terminal_resolved_rows": value[
                    "completed_terminal_resolved_rows"
                ],
                "attention_values_observed": value["attention_values_observed"],
                "envelope": value["envelope"],
            }
            for regime, value in regimes.items()
        }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
