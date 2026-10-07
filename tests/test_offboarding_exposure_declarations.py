import unittest

from baa_protocol.exposure_bridge import (
    MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
    ManagedSubjectStateChangeMeasurement,
    assess_metric_bound,
    realized_exposure_for_settlement,
)
from baa_protocol.offboarding import (
    OFFBOARDING_EXPOSURE_BOUNDS_V1,
    OffboardingKernel,
    OffboardingProposal,
    exposure_declaration_for_proposal,
)


def proposal(
    *,
    proposal_id: str,
    target_system: str,
    operation: str,
    subject_ref: str = "employee:1",
) -> OffboardingProposal:
    return OffboardingProposal(
        proposal_id=proposal_id,
        obligation_id=f"obl:{proposal_id}",
        case_id="case:1",
        authority_epoch=7,
        governance_basis_id="basis:1",
        subject_ref=subject_ref,
        target_system=target_system,
        operation=operation,
        state_version=3,
        effective_at=100,
        expires_at=200,
        request_identity=f"request:{proposal_id}",
    )


class OffboardingExposureDeclarationTests(unittest.TestCase):
    def test_every_allowed_offboarding_operation_has_one_frozen_declaration(self):
        self.assertEqual(
            set(OFFBOARDING_EXPOSURE_BOUNDS_V1),
            set(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS),
        )

        for index, (target_system, operation) in enumerate(
            sorted(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS)
        ):
            with self.subTest(target_system=target_system, operation=operation):
                item = proposal(
                    proposal_id=f"p:{index}",
                    target_system=target_system,
                    operation=operation,
                )
                declaration = exposure_declaration_for_proposal(item)

                self.assertEqual(declaration.proposal_id, item.proposal_id)
                self.assertEqual(
                    declaration.metric_id,
                    MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
                )
                self.assertEqual(
                    declaration.declared_subject_ref,
                    item.subject_ref,
                )
                self.assertEqual(declaration.exposure_bound, 1)

    def test_undeclared_operation_cannot_acquire_exposure_semantics(self):
        item = proposal(
            proposal_id="p:unsupported",
            target_system="iam",
            operation="identity.delete",
        )

        with self.assertRaisesRegex(
            ValueError,
            "no frozen exposure declaration",
        ):
            exposure_declaration_for_proposal(item)

    def test_empty_subject_cannot_be_declared(self):
        item = proposal(
            proposal_id="p:empty-subject",
            target_system="iam",
            operation="identity.disable",
            subject_ref=" ",
        )

        with self.assertRaisesRegex(ValueError, "requires a subject"):
            exposure_declaration_for_proposal(item)

    def test_exact_measurement_can_bind_only_to_its_proposal_declaration(self):
        item = proposal(
            proposal_id="p:disable",
            target_system="iam",
            operation="identity.disable",
        )
        declaration = exposure_declaration_for_proposal(item)
        measurement = ManagedSubjectStateChangeMeasurement(
            proposal_id=item.proposal_id,
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref=item.subject_ref,
            observed_postcondition={
                "subject_ref": item.subject_ref,
                "enabled": False,
            },
            managed_subject_count_before=2,
            managed_subject_count_after=2,
            changed_subject_refs=(item.subject_ref,),
            scope_complete=True,
        )

        assessment = assess_metric_bound(declaration, measurement)

        self.assertTrue(assessment.established)
        self.assertEqual(realized_exposure_for_settlement(assessment), 1)

    def test_collateral_control_subject_falsifies_all_three_declared_unit_bounds(self):
        for index, (target_system, operation) in enumerate(
            sorted(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS)
        ):
            with self.subTest(target_system=target_system, operation=operation):
                item = proposal(
                    proposal_id=f"p:collateral:{index}",
                    target_system=target_system,
                    operation=operation,
                )
                declaration = exposure_declaration_for_proposal(item)
                measurement = ManagedSubjectStateChangeMeasurement(
                    proposal_id=item.proposal_id,
                    metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
                    declared_subject_ref=item.subject_ref,
                    observed_postcondition={"subject_ref": item.subject_ref},
                    managed_subject_count_before=2,
                    managed_subject_count_after=2,
                    changed_subject_refs=(item.subject_ref, "employee:control"),
                    scope_complete=True,
                )

                assessment = assess_metric_bound(declaration, measurement)

                self.assertFalse(assessment.established)
                self.assertEqual(assessment.realized_exposure, 2)
                self.assertIn("exceeds declared bound", assessment.reason)


if __name__ == "__main__":
    unittest.main()
