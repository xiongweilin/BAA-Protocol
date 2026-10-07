import json
import unittest
from pathlib import Path

from baa_protocol.offboarding import (
    OffboardingProposal,
    exposure_declaration_for_proposal,
)


_RESULT = (
    Path(__file__).resolve().parents[1]
    / "formal"
    / "composed-exposure-binding-v1-result.json"
)


class ComposedExposureEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(_RESULT.read_text(encoding="utf-8"))

    def test_tested_tree_is_exactly_the_accepted_tree(self):
        provenance = self.data["provenance"]
        self.assertEqual(provenance["tested_tree"], provenance["accepted_tree"])
        self.assertNotEqual(
            provenance["aios_tested_commit"],
            provenance["aios_accepted_commit"],
        )

    def test_normal_episode_matches_frozen_offboarding_declarations(self):
        normal = self.data["scenarios"]["normal"]
        bindings = normal["bindings"]
        self.assertEqual(
            {item["operation"] for item in bindings},
            {"identity.disable", "sessions.revoke", "employee.deactivate"},
        )

        for item in bindings:
            with self.subTest(operation=item["operation"]):
                proposal = OffboardingProposal(
                    proposal_id=item["proposal_id"],
                    obligation_id=item["obligation_id"],
                    case_id="case:evidence",
                    authority_epoch=1,
                    governance_basis_id="governance:evidence",
                    subject_ref=item["declared_subject_ref"],
                    target_system=item["target_system"],
                    operation=item["operation"],
                    state_version=1,
                    effective_at=0,
                    expires_at=1,
                    request_identity=f"aios-{item['effect_id']}",
                )
                declaration = exposure_declaration_for_proposal(proposal)

                self.assertEqual(
                    item["proposal_id"],
                    f"effect:{item['effect_id']}",
                )
                self.assertEqual(
                    declaration.metric_id,
                    self.data["metric_id"],
                )
                self.assertEqual(
                    declaration.declared_subject_ref,
                    item["declared_subject_ref"],
                )
                self.assertEqual(
                    declaration.exposure_bound,
                    item["exposure_bound"],
                )
                self.assertTrue(item["assessment_established"])
                self.assertTrue(item["scope_complete"])
                self.assertEqual(item["realized_exposure"], 1)
                self.assertEqual(item["exposure_bound"], 1)
                self.assertEqual(
                    item["changed_subject_refs"],
                    [item["declared_subject_ref"]],
                )
                self.assertGreaterEqual(item["managed_subject_count_before"], 2)
                self.assertEqual(
                    item["managed_subject_count_before"],
                    item["managed_subject_count_after"],
                )

    def test_recovery_scenarios_preserve_the_established_binding_result(self):
        for scenario in ("lost_ack", "readback_outage"):
            with self.subTest(scenario=scenario):
                record = self.data["scenarios"][scenario]
                self.assertTrue(record["bindings_match_normal"])
                self.assertEqual(record["status_trace"][-1], "completed")

    def test_runtime_bypass_has_no_observed_provider_effect(self):
        bypass = self.data["scenarios"]["runtime_bypass"]
        self.assertEqual(bypass["http_status"], 403)
        self.assertTrue(bypass["authorization_boundary_reached"])
        self.assertFalse(bypass["provider_effect_observed"])
        self.assertTrue(bypass["product_state_unchanged"])

    def test_artifacts_are_content_addressed(self):
        for scenario, record in self.data["scenarios"].items():
            with self.subTest(scenario=scenario):
                self.assertGreater(record["artifact_id"], 0)
                digest = record["artifact_digest"]
                self.assertTrue(digest.startswith("sha256:"))
                self.assertEqual(len(digest), len("sha256:") + 64)


if __name__ == "__main__":
    unittest.main()
