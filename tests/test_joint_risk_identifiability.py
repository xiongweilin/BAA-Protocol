"""Identification counterexamples for the offboarding joint-risk assumption.

All observations in this fixture are SYNTHETIC: they mirror the *shape* of the
three accepted real-product E2E measurements but are not copied raw evidence.
They prove only that those kinds of observations cannot uniquely identify a
risk-factor partition, interaction penalty or cross-action aggregation unit.
"""

import unittest
from dataclasses import dataclass

from baa_protocol.exposure_bridge import (
    MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
    ExposureMetricDeclaration,
)
from baa_protocol.offboarding import OFFBOARDING_RISK_FACTOR_IDS_V1
from baa_protocol.risk_bridge import (
    RiskFactorDeclaration,
    bind_risk_term,
    declared_joint_risk,
)


@dataclass(frozen=True)
class ProjectedEffect:
    proposal_id: str
    product_system: str
    subject_ref: str
    operation: str
    realized_per_effect: int


# Three product effects, same declared principal, but only two product-side
# subject identities (one HRIS record and one IAM user).  This is a synthetic
# observational-shape fixture, not an exact replay of the acceptance artifacts.
OBSERVED_SHAPE = (
    ProjectedEffect("p:hris", "hris", "employee:1", "employee.deactivate", 1),
    ProjectedEffect("p:disable", "iam", "employee:1", "identity.disable", 1),
    ProjectedEffect("p:sessions", "iam", "employee:1", "sessions.revoke", 1),
)


def declared_risk_for_factor_partition(
    factors: tuple[str, ...], *, interaction_penalty: int
) -> int:
    if len(factors) != len(OBSERVED_SHAPE):
        raise ValueError("every observed effect needs exactly one factor label")
    terms = []
    for effect, factor in zip(OBSERVED_SHAPE, factors):
        exposure = ExposureMetricDeclaration(
            proposal_id=effect.proposal_id,
            metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            declared_subject_ref=effect.subject_ref,
            exposure_bound=effect.realized_per_effect,
        )
        risk = RiskFactorDeclaration(
            proposal_id=effect.proposal_id,
            exposure_metric_id=MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
            risk_factor_id=factor,
        )
        bound = bind_risk_term(exposure, risk)
        if not bound.established or bound.term is None:
            raise AssertionError("synthetic demonstration must bind exact terms")
        terms.append(bound.term)
    return declared_joint_risk(terms, interaction_penalty=interaction_penalty)


class JointRiskIdentifiabilityTests(unittest.TestCase):
    def test_same_three_unit_measurements_do_not_identify_factor_partition(self):
        # All schemes are observationally indistinguishable in this fixture.
        all_distinct = declared_risk_for_factor_partition(
            ("hris", "identity", "sessions"), interaction_penalty=1
        )
        iam_shared = declared_risk_for_factor_partition(
            ("hris", "iam", "iam"), interaction_penalty=1
        )
        all_shared = declared_risk_for_factor_partition(
            ("principal", "principal", "principal"), interaction_penalty=1
        )
        self.assertEqual(
            tuple(e.realized_per_effect for e in OBSERVED_SHAPE), (1, 1, 1)
        )
        self.assertEqual((all_distinct, iam_shared, all_shared), (3, 4, 6))

    def test_same_measurement_and_partition_do_not_identify_penalty(self):
        risks = [
            declared_risk_for_factor_partition(
                ("hris", "iam", "iam"), interaction_penalty=penalty
            )
            for penalty in (0, 1, 2)
        ]
        self.assertEqual(risks, [3, 4, 5])

    def test_effect_count_distinct_product_subjects_and_principal_are_not_same(self):
        per_effect_sum = sum(e.realized_per_effect for e in OBSERVED_SHAPE)
        touched_product_subjects = {
            (e.product_system, e.subject_ref) for e in OBSERVED_SHAPE
        }
        # A cross-system principal correspondence is additionally ASSUMED in
        # the synthetic fixture, not measured or proven by these three events.
        assumed_principal_subjects = {e.subject_ref for e in OBSERVED_SHAPE}
        self.assertEqual(per_effect_sum, 3)
        self.assertEqual(len(touched_product_subjects), 2)
        self.assertEqual(len(assumed_principal_subjects), 1)
        self.assertNotEqual(per_effect_sum, len(touched_product_subjects))

    def test_intermediate_effects_cannot_be_recovered_from_terminal_net_change(self):
        # Net final snapshots can erase intervening effects. This fixture
        # describes two separately visible state transitions, not a real
        # observed Keycloak behavior in the acceptance run.
        transitions = ((True, False), (False, True))
        per_transition_change_count = sum(a != b for a, b in transitions)
        terminal_net_change_count = int(transitions[0][0] != transitions[-1][1])
        self.assertEqual(per_transition_change_count, 2)
        self.assertEqual(terminal_net_change_count, 0)

    def test_real_product_observation_does_not_auto_populate_risk_registry(self):
        # Offboarding factor identity is still an independent calibration.
        self.assertEqual(OFFBOARDING_RISK_FACTOR_IDS_V1, {})


if __name__ == "__main__":
    unittest.main()
