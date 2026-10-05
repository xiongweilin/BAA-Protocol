#!/usr/bin/env python3
"""Run the deterministic BAA capability-sweep micro-study."""

from __future__ import annotations

import json

from baa_protocol.delegation_frontier import (
    DelegationBudget,
    evaluate_capability_sweep,
)


def main() -> None:
    result = evaluate_capability_sweep(
        budget=DelegationBudget(
            max_principal_attention=0,
            max_unsafe_transitions=0,
            max_terminal_unresolved_results=0,
            min_useful_delivery=3,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
