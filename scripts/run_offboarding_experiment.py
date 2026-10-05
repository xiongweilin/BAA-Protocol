#!/usr/bin/env python3
"""Run the deterministic employee-offboarding BAA experiment suite."""

from __future__ import annotations

import json

from baa_protocol.experiment import run_suite, summarize


def main() -> None:
    results = run_suite()
    print(
        json.dumps(
            {
                "summary": summarize(results),
                "episodes": [result.to_dict() for result in results],
                "qualification": (
                    "Deterministic falsification fixtures only; "
                    "not an empirical real-world safety estimate."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
