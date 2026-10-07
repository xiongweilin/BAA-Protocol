#!/usr/bin/env python3
"""Run the finite BAA structural model check and emit a machine-readable report."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from baa_protocol.formal_model import reference_model_v1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()

    report = asdict(reference_model_v1().check())
    payload = json.dumps(report, indent=2, sort_keys=True)
    print(payload, flush=True)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
