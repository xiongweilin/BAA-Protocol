import unittest

from baa_protocol.exposure_bridge import (
    MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
    ExposureMetricDeclaration,
    ManagedSubjectStateChangeMeasurement,
    SubjectScopeEvidence,
    assess_metric_bound,
    assess_subject_scope_exposure,
    evidence_from_target_readback,
    realized_exposure_for_settlement,
)
from baa_protocol.formal_model import Action, FiniteBAAModel, FormalState, ProposalSpec


class ExposureBridgeContractTests(unittest.TestCase):
    def test_current_target_readback_is_not_scope_complete(self):
        for observed in (
            {
                "target_system": "hris",
                "operation": "employee.deactivate",
                "subject_ref": "employee:1",
                "active": False,
            },
            {
                "target_system": "iam",
                "operation": "identity.disable",
                "subject_ref": "employee:1",
                "enabled": False,
            },
            {
                "target_system": "iam",
                "operation": "sessions.revoke",
                "subject_ref": "employee:1",
                "active_sessions": 0,
            },
        ):
            with self.subTest(operation=observed["operation"]):
                evidence = evidence_from_target_readback(
                    declared_subject_ref="employee:1",
                    observed_postcondition=observed,
                )
                assessment = assess_subject_scope_exposure(
                    evidence,
                    exposure_bound=1,
                )
                self.assertFalse(assessment.established)
                self.assertIsNone(assessment.realized_exposure)
                self.assertIn("scope-incomplete", assessment.reason)
                with self.assertRaises(ValueError):
                    realized_exposure_for_settlement(assessment)

    def test_complete_single_subject_evidence_establishes_unit_bound(self):
        evidence = SubjectScopeEvidence(
            declared_subject_ref="employee:1",
            observed_postcondition={
                "subject_ref": "employee:1",
                "enabled": False,
            },
            affected_subject_refs=("employee:1", "employee:1"),
            scope_complete=True,
        )
        assessment = assess_subject_scope_exposure(
            evidence,
            exposure_bound=1,
        )

        self.assertTrue(assessment.established)
        self.assertEqual(assessment.realized_exposure, 1)
        self.assertEqual(realized_exposure_for_settlement(assessment), 1)

    def test_complete_zero_effect_evidence_can_settle_zero(self):
        evidence = SubjectScopeEvidence(
            declared_subject_ref="employee:1",
            observed_postcondition={"subject_ref": "employee:1"},
            affected_subject_refs=(),
            scope_complete=True,
        )
        assessment = assess_subject_scope_exposure(
            evidence,
            exposure_bound=1,
        )

        self.assertTrue(assessment.established)
        self.assertEqual(realized_exposure_for_settlement(assessment), 0)

    def test_collateral_subject_explicitly_falsifies_bound(self):
        evidence = SubjectScopeEvidence(
            declared_subject_ref="employee:1",
            observed_postcondition={
                "subject_ref": "employee:1",
                "enabled": False,
            },
            affected_subject_refs=("employee:1", "employee:2"),
            scope_complete=True,
        )
        assessment = assess_subject_scope_exposure(
            evidence,
            exposure_bound=1,
        )

        self.assertFalse(assessment.established)
        self.assertEqual(assessment.realized_exposure, 2)
        self.assertIn("exceeds declared bound", assessment.reason)

        spec = ProposalSpec(
            proposal_id="p:1",
            object_id="employee:1",
            operation="identity.disable",
            quota=1,
            exposure_bound=1,
            risk_factor="iam-subject",
        )
        model = FiniteBAAModel(
            (spec,),
            risk_budget=1,
            interaction_penalty=0,
        )
        state = FormalState.initial(1)
        evaluated = model.step(state, Action("evaluate", 0))
        self.assertTrue(evaluated.accepted)
        executed = model.step(
            evaluated.after,
            Action(
                "execute",
                0,
                object_id="employee:1",
                operation="identity.disable",
                amount=1,
                now=1,
                state_version=1,
            ),
        )
        self.assertTrue(executed.accepted)
        settlement = model.step(
            executed.after,
            Action(
                "verify",
                0,
                realized_exposure=assessment.realized_exposure,
            ),
        )
        self.assertFalse(settlement.accepted)
        self.assertEqual(
            settlement.reason,
            "verification result outside Omega exposure bound",
        )

    def test_readback_subject_rebound_fails_even_before_scope_attestation(self):
        evidence = SubjectScopeEvidence(
            declared_subject_ref="employee:1",
            observed_postcondition={
                "subject_ref": "employee:2",
                "enabled": False,
            },
            affected_subject_refs=("employee:2",),
            scope_complete=True,
        )
        assessment = assess_subject_scope_exposure(
            evidence,
            exposure_bound=1,
        )

        self.assertFalse(assessment.established)
        self.assertIsNone(assessment.realized_exposure)
        self.assertIn("does not match declared subject", assessment.reason)

    def test_complete_evidence_outside_declared_subject_is_not_accepted(self):
        evidence = SubjectScopeEvidence(
            declared_subject_ref="employee:1",
            observed_postcondition={},
            affected_subject_refs=("employee:2",),
            scope_complete=True,
        )
        assessment = assess_subject_scope_exposure(
            evidence,
            exposure_bound=1,
        )

        self.assertFalse(assessment.established)
        self.assertEqual(assessment.realized_exposure, 1)
        self.assertIn("outside the declared target", assessment.reason)


    def test_exact_managed_subject_metric_binding_can_feed_settlement(self):
        declaration = ExposureMetricDeclaration(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            exposure_bound=1,
        )
        measurement = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            observed_postcondition={
                "subject_ref": "employee:1",
                "enabled": False,
            },
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:1",),
            scope_complete=True,
        )

        assessment = assess_metric_bound(declaration, measurement)

        self.assertTrue(assessment.established)
        self.assertEqual(realized_exposure_for_settlement(assessment), 1)

    def test_metric_identity_mismatch_fails_closed(self):
        declaration = ExposureMetricDeclaration(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            exposure_bound=1,
        )
        measurement = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:metric",
            metric_id="different-metric-v1",
            declared_subject_ref="employee:1",
            observed_postcondition={"subject_ref": "employee:1"},
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:1",),
            scope_complete=True,
        )

        assessment = assess_metric_bound(declaration, measurement)

        self.assertFalse(assessment.established)
        self.assertIsNone(assessment.realized_exposure)
        self.assertIn("metric identity", assessment.reason)

    def test_metric_binding_rejects_proposal_or_subject_rebound(self):
        declaration = ExposureMetricDeclaration(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            exposure_bound=1,
        )
        proposal_rebound = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:other",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            observed_postcondition={"subject_ref": "employee:1"},
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:1",),
            scope_complete=True,
        )
        subject_rebound = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:2",
            observed_postcondition={"subject_ref": "employee:2"},
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:2",),
            scope_complete=True,
        )

        self.assertFalse(
            assess_metric_bound(declaration, proposal_rebound).established
        )
        self.assertFalse(
            assess_metric_bound(declaration, subject_rebound).established
        )

    def test_managed_subject_metric_preserves_collateral_counterexample(self):
        declaration = ExposureMetricDeclaration(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            exposure_bound=1,
        )
        measurement = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            observed_postcondition={"subject_ref": "employee:1"},
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:1", "employee:2"),
            scope_complete=True,
        )

        assessment = assess_metric_bound(declaration, measurement)

        self.assertFalse(assessment.established)
        self.assertEqual(assessment.realized_exposure, 2)
        self.assertIn("exceeds declared bound", assessment.reason)

    def test_managed_subject_metric_requires_complete_scope(self):
        declaration = ExposureMetricDeclaration(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            exposure_bound=1,
        )
        measurement = ManagedSubjectStateChangeMeasurement(
            proposal_id="p:metric",
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref="employee:1",
            observed_postcondition={"subject_ref": "employee:1"},
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=("employee:1",),
            scope_complete=False,
        )

        assessment = assess_metric_bound(declaration, measurement)

        self.assertFalse(assessment.established)
        self.assertIsNone(assessment.realized_exposure)
        with self.assertRaises(ValueError):
            realized_exposure_for_settlement(assessment)


if __name__ == "__main__":
    unittest.main()
