"""Structural stress experiment expectations, not empirical outcome samples."""
import unittest

from scripts.run_contingent_model_stress import run


class ContingentModelStressTests(unittest.TestCase):
    def test_each_adversarial_model_downgrades_previously_valid_policy(self):
        result = run()
        self.assertEqual(result["evidence_class"], "synthetic_model_perturbation_only")
        self.assertEqual(result["caught_model_perturbations"], 5)
        self.assertEqual(
            {case["case"] for case in result["cases"]},
            {
                "unmodeled_initial_world",
                "underreported_unsafe_successor",
                "revoked_effect_authority",
                "unobserved_pending_effect",
                "unqualified_readback",
            },
        )
        self.assertTrue(all(not x["adversarial_model_accepts"] for x in result["cases"]))


if __name__ == "__main__":
    unittest.main()
