#!/usr/bin/env python3
"""Run the deterministic canary-release delegation frontier."""

from __future__ import annotations

import json

from baa_protocol.canary_experiment import CanaryBudget, evaluate_frontier


def main() -> None:
    result = evaluate_frontier(
        budget=CanaryBudget(
            max_principal_attention=0,
            max_unsafe_transitions=0,
            max_terminal_unresolved_results=0,
            min_useful_delivery=1,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
