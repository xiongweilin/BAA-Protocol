"""Synthetic analyzer fixtures only; no sampled model or human outcomes."""
from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/analyze_contingent_strong_baseline.py"
SPEC = importlib.util.spec_from_file_location("strong_baseline_analysis", SCRIPT)
assert SPEC and SPEC.loader
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


class StrongPlannerAnalysisTests(unittest.TestCase):
    def write(self, rows):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "synthetic.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=analysis.REQUIRED)
            writer.writeheader()
            writer.writerows(rows)
        return path

    @staticmethod
    def row(case, arm, *, safety="safe", delivery="useful", unknown="0"):
        return {
            "case_id": case, "arm": arm, "task_sha256": "sha256:frozen-fixture",
            "task_source_ref": "synthetic-only", "information_cutoff": "fixture:pre",
            "model_id": "fixture", "authorization_policy_sha256": "sha256:policy-fixture",
            "observation_budget": "2", "effect_budget": "2",
            "horizon": "3", "review_budget_seconds": "60",
            "implementation_revision": f"fixture:{arm}", "safety_status": safety,
            "delivery_status": delivery, "terminal_unknown_effects": unknown,
            "principal_seconds": "10", "assurance_seconds": "5",
            "operations_seconds": "7", "model_calls": "2",
            "automatic_interventions": "1",
        }

    def test_strict_delivery_and_missingness_are_distinct_from_human_labor(self):
        rows = [
            self.row("A", "baa"), self.row("A", "strong_control", delivery="incomplete"),
            self.row("B", "baa", safety="unknown"), self.row("B", "strong_control"),
            self.row("C", "baa", safety="unsafe"), self.row("C", "strong_control"),
        ]
        rows[1]["assurance_seconds"] = "NA"
        result = analysis.analyze(self.write(rows))
        self.assertEqual(result["matched_cases"], 3)
        self.assertEqual(result["baa_only_strict_safe_useful"], 1)
        self.assertEqual(result["strong_control_only_strict_safe_useful"], 1)
        self.assertEqual(result["unknown_strict_pairs"], 1)
        self.assertEqual(result["strict_safe_delivery_delta_bounds"], [-1 / 3, 1 / 3])
        self.assertEqual(result["labor_both_arms_complete_pairs"], 2)
        self.assertEqual(result["cases_with_recorded_unsafe_status"], {"baa": 1, "strong_control": 0})

    def test_rejects_weaker_control_and_incomplete_pair(self):
        rows = [self.row("A", "baa"), self.row("A", "strong_control")]
        rows[1]["observation_budget"] = "0"
        with self.assertRaisesRegex(ValueError, "unequal"):
            analysis.analyze(self.write(rows))
        with self.assertRaisesRegex(ValueError, "missing matched"):
            analysis.analyze(self.write([rows[0]]))

    def test_unknown_safety_cannot_be_made_safe_by_useful_delivery(self):
        rows = [
            self.row("A", "baa", safety="unknown", delivery="useful"),
            self.row("A", "strong_control", safety="safe", delivery="useful", unknown="1"),
        ]
        result = analysis.analyze(self.write(rows))
        self.assertEqual(result["fully_known_strict_pairs"], 0)
        self.assertEqual(result["unknown_strict_pairs"], 1)

    def test_unresolved_effect_counts_as_unknown(self):
        rows = [
            self.row("A", "baa", unknown="1"),
            self.row("A", "strong_control"),
        ]
        result = analysis.analyze(self.write(rows))
        self.assertEqual(result["unknown_strict_pairs"], 1)
        self.assertEqual(result["fully_known_strict_pairs"], 0)
        self.assertEqual(result["strict_safe_delivery_delta_bounds"], [-1, 1])

    def test_witnessed_unsafe_is_known_negative(self):
        rows = [
            self.row("A", "baa", safety="unsafe", delivery="unknown", unknown="1"),
            self.row("A", "strong_control"),
        ]
        result = analysis.analyze(self.write(rows))
        self.assertEqual(result["unknown_strict_pairs"], 0)
        self.assertEqual(result["strong_control_only_strict_safe_useful"], 1)

    def test_fractional_discrete_counts_rejected(self):
        for field in ("terminal_unknown_effects", "model_calls",
                      "automatic_interventions", "horizon"):
            with self.subTest(field=field):
                rows = [self.row("A", "baa"), self.row("A", "strong_control")]
                rows[0][field] = "0.5"
                with self.assertRaisesRegex(ValueError, "integer count"):
                    analysis.analyze(self.write(rows))

    def test_rejects_missing_human_or_unbounded_numeric_fields(self):
        rows = [self.row("A", "baa"), self.row("A", "strong_control")]
        rows[0]["principal_seconds"] = "-1"
        with self.assertRaisesRegex(ValueError, "negative"):
            analysis.analyze(self.write(rows))
        rows[0]["principal_seconds"] = "NA"
        rows[0]["model_calls"] = "nan"
        with self.assertRaisesRegex(ValueError, "integer count"):
            analysis.analyze(self.write(rows))
        rows[0]["model_calls"] = "2"
        rows[0]["principal_seconds"] = "nan"
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            analysis.analyze(self.write(rows))


if __name__ == "__main__":
    unittest.main()
