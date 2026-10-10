"""Integrity guards for frozen reports (not a repeat of real-model experiments)."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrozenEvidenceAuditTests(unittest.TestCase):
    def test_zero_positive_strict_safe_cost_frontier_is_preserved(self) -> None:
        raw = json.loads(
            (ROOT / "experiments/prospective-delegation-cost-frontier-v1-result.json").read_text(
                encoding="utf-8"
            )
        )
        by_budget = raw["architecture_strict_safe"]
        for level in ("0", "1", "2"):
            with self.subTest(level=level):
                counts = by_budget[level]
                self.assertEqual(
                    counts["positive_cells"] + counts["negative_cells"] + counts["tie_cells"],
                    30,
                )
                self.assertEqual(counts, {"positive_cells": 0, "negative_cells": 0, "tie_cells": 30})
        self.assertIs(by_budget["persistence"]["met"], False)
        summary = (ROOT / "experiments/claim-evidence-index.md").read_text(encoding="utf-8")
        self.assertIn("0/30 strict-safe BAA-positive cells", summary)

    def test_finite_model_cardinality_is_reported_with_a_scope_boundary(self) -> None:
        raw = json.loads(
            (ROOT / "formal/structural-model-v1-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(raw["reachable_states"], 584)
        self.assertEqual(raw["explored_transitions"], 35040)
        index = (ROOT / "experiments/claim-evidence-index.md").read_text(encoding="utf-8")
        self.assertIn("584 states / 35,040 abstract transitions", index)
        self.assertIn("Complete mediation for all deployed action channels", index)

    def test_original_actions_evidence_inventory_has_distinct_zip_digests(self) -> None:
        inventory = (
            ROOT / "experiments/source-artifact-provenance-2026-10-10.md"
        ).read_text(encoding="utf-8")
        self.assertIn("A hash list does **not** preserve artifact bytes", inventory)
        digests = re.findall(r"\x60([0-9a-f]{64})\x60", inventory)
        self.assertEqual(len(digests), 6)
        self.assertEqual(len(set(digests)), 6)


if __name__ == "__main__":
    unittest.main()
