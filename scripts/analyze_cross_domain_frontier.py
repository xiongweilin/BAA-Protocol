#!/usr/bin/env python3
"""Analyze accepted offboarding-v6 and canary-v1 result artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baa_protocol.frontier_sensitivity import analyze_pair


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offboarding-v6", required=True)
    parser.add_argument("--canary-v1", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main() -> None:
    args = parse_args()
    result = analyze_pair(load(args.offboarding_v6), load(args.canary_v1))
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
