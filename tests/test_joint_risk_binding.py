import unittest

from baa_protocol.exposure_bridge import ExposureMetricDeclaration
from baa_protocol.formal_model import FiniteBAAModel, ProposalSpec
from baa_protocol.offboarding import (
    OFFBOARDING_RISK_FACTOR_IDS_V1,
    OffboardingKernel,
    OffboardingProposal,
    exposure_declaration_for_proposal,
    risk_factor_declaration_for_proposal,
)
from baa_protocol.risk_bridge import (
    PAIRWISE_SHARED_FACTOR_MIN_V1,
    RiskFactorDeclaration,
    bind_risk_term,
    declared_joint_risk,
)


def offboarding_proposal(
    *,
    proposal_id: str,
    target_system: str,
    operation: str,
) -> OffboardingProposal:
    return OffboardingProposal(
        proposal_id=proposal_id,
        obligation_id=f"obl:{proposal_id}",
        case_id="case:1",
        authority_epoch=7,
        governance_basis_id="basis:1",
        subject_ref="employee:1",
        target_system=target_system,
        operation=operation,
        state_version=3,
        effective_at=100,
        expires_at=200,
        request_identity=f"request:{proposal_id}",
    )


class JointRiskBindingContractTests(unittest.TestCase):
    def test_exact_binding_reproduces_structural_pairwise_function(self):
        exposures = (
            ExposureMetricDeclaration("p:1", "metric:v1", "employee:1", 1),
            ExposureMetricDeclaration("p:2", "metric:v1", "employee:2", 1),
            ExposureMetricDeclaration("p:3", "metric:v1", "employee:3", 1),
        )
        risks = (
            RiskFactorDeclaration("p:1", "metric:v1", "shared"),
            RiskFactorDeclaration("p:2", "metric:v1", "shared"),
            RiskFactorDeclaration("p:3", "metric:v1", "independent"),
        )
        terms = []
        for exposure, risk in zip(exposures, risks):
            assessment = bind_risk_term(exposure, risk)
            self.assertTrue(assessment.established)
            self.assertIsNotNone(assessment.term)
            terms.append(assessment.term)

        observed = declared_joint_risk(terms, interaction_penalty=1)

        model = FiniteBAAModel(
            (
                ProposalSpec("p:1", "employee:1", "op", 1, 1, "shared"),
                ProposalSpec("p:2", "employee:2", "op", 1, 1, "shared"),
                ProposalSpec("p:3", "employee:3", "op", 1, 1, "independent"),
            ),
            risk_budget=99,
            interaction_penalty=1,
        )
        expected = model.risk(
            [(1, "shared"), (1, "shared"), (1, "independent")]
        )

        self.assertEqual(observed, expected)
        self.assertEqual(observed, 4)

    def test_proposal_metric_and_functional_rebound_fail_closed(self):
        exposure = ExposureMetricDeclaration(
            "p:1",
            "metric:v1",
            "employee:1",
            1,
        )

        cases = (
            RiskFactorDeclaration("p:other", "metric:v1", "shared"),
            RiskFactorDeclaration("p:1", "metric:other", "shared"),
            RiskFactorDeclaration(
                "p:1",
                "metric:v1",
                "shared",
                joint_risk_functional_id="other-functional-v1",
            ),
        )
        for risk in cases:
            with self.subTest(risk=risk):
                assessment = bind_risk_term(exposure, risk)
                self.assertFalse(assessment.established)
                self.assertIsNone(assessment.term)

    def test_empty_risk_factor_fails_closed(self):
        exposure = ExposureMetricDeclaration(
            "p:1",
            "metric:v1",
            "employee:1",
            1,
        )
        assessment = bind_risk_term(
            exposure,
            RiskFactorDeclaration(
                "p:1",
                "metric:v1",
                " ",
                joint_risk_functional_id=PAIRWISE_SHARED_FACTOR_MIN_V1,
            ),
        )
        self.assertFalse(assessment.established)
        self.assertIn("risk factor is empty", assessment.reason)

    def test_joint_risk_rejects_mixed_metric_units(self):
        left = bind_risk_term(
            ExposureMetricDeclaration("p:1", "subject-count-v1", "employee:1", 1),
            RiskFactorDeclaration("p:1", "subject-count-v1", "shared"),
        )
        right = bind_risk_term(
            ExposureMetricDeclaration("p:2", "dollars-v1", "employee:2", 1),
            RiskFactorDeclaration("p:2", "dollars-v1", "shared"),
        )
        self.assertTrue(left.established)
        self.assertTrue(right.established)
        assert left.term is not None
        assert right.term is not None
        with self.assertRaisesRegex(ValueError, "incompatible exposure metrics"):
            declared_joint_risk([left.term, right.term], interaction_penalty=1)

    def test_joint_risk_rejects_duplicate_proposal_terms(self):
        bound = bind_risk_term(
            ExposureMetricDeclaration("p:1", "subject-count-v1", "employee:1", 1),
            RiskFactorDeclaration("p:1", "subject-count-v1", "shared"),
        )
        self.assertTrue(bound.established)
        assert bound.term is not None
        with self.assertRaisesRegex(ValueError, "duplicate proposal identity"):
            declared_joint_risk([bound.term, bound.term], interaction_penalty=1)

    def test_current_offboarding_has_no_calibrated_risk_factor_mapping(self):
        self.assertEqual(OFFBOARDING_RISK_FACTOR_IDS_V1, {})

        for index, (target_system, operation) in enumerate(
            sorted(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS)
        ):
            with self.subTest(target_system=target_system, operation=operation):
                item = offboarding_proposal(
                    proposal_id=f"p:{index}",
                    target_system=target_system,
                    operation=operation,
                )
                exposure = exposure_declaration_for_proposal(item)
                self.assertEqual(exposure.exposure_bound, 1)

                with self.assertRaisesRegex(
                    ValueError,
                    "no calibrated risk-factor declaration",
                ):
                    risk_factor_declaration_for_proposal(item)

    def test_interaction_penalty_remains_a_separate_calibration_parameter(self):
        terms = []
        for proposal_id in ("p:1", "p:2"):
            exposure = ExposureMetricDeclaration(
                proposal_id,
                "metric:v1",
                proposal_id,
                1,
            )
            assessment = bind_risk_term(
                exposure,
                RiskFactorDeclaration(
                    proposal_id,
                    "metric:v1",
                    "shared",
                ),
            )
            self.assertTrue(assessment.established)
            assert assessment.term is not None
            terms.append(assessment.term)

        self.assertEqual(declared_joint_risk(terms, interaction_penalty=0), 2)
        self.assertEqual(declared_joint_risk(terms, interaction_penalty=1), 3)
        self.assertEqual(declared_joint_risk(terms, interaction_penalty=2), 4)


if __name__ == "__main__":
    unittest.main()
