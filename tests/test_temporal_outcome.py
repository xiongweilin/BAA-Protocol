"""P3 outcome instrument: synthetic instrumentation tests, not calibration data."""

import unittest

from baa_protocol.temporal_outcome import (
    AccessProbe,
    EvidenceKind,
    JointProjection,
    ObservationInterval,
    SubjectPolicy,
    measure_offboarding,
)


def projection(
    *,
    hris: bool | None,
    iam: bool | None,
    sessions: int | None,
    probe: AccessProbe,
) -> JointProjection:
    return JointProjection(hris, iam, sessions, probe)


PRE = projection(hris=True, iam=True, sessions=1, probe=AccessProbe.ALLOW)
POST = projection(hris=False, iam=False, sessions=0, probe=AccessProbe.DENY)
BAD_POST = projection(hris=False, iam=False, sessions=0, probe=AccessProbe.ALLOW)


def interval(subject, start, end, data, kind=EvidenceKind.INTERVAL_ATTESTED):
    return ObservationInterval(
        subject_id=subject,
        start_s=start,
        end_s=end,
        kind=kind,
        evidence_ref=f"synthetic:{subject}:{start}-{end}",
        projection=data,
    )


def run(*segments, subjects=None, start=0, end=30, skew=0):
    policies = subjects or (SubjectPolicy("s1", effective_at_s=10, grace_s=5),)
    return measure_offboarding(
        policies=policies,
        observations=tuple(segments),
        horizon_start_s=start,
        horizon_end_s=end,
        max_clock_error_s=skew,
    )


class TemporalOutcomeTests(unittest.TestCase):
    def test_fully_attested_compliant_trace_has_zero_joint_y(self):
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, POST),
        )
        self.assertTrue(outcome.fully_identified)
        self.assertEqual(
            (outcome.joint_violation.lower_s, outcome.joint_violation.upper_s),
            (0, 0),
        )
        self.assertEqual(outcome.subjects[0].transition_grace_s, 5)

    def test_postdeadline_access_probe_detects_violation_despite_safe_fields(self):
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 18, BAD_POST),
            interval("s1", 18, 30, POST),
        )
        self.assertEqual(outcome.joint_violation.lower_s, 3)
        self.assertEqual(outcome.joint_violation.upper_s, 3)
        self.assertEqual(outcome.postdeadline_access.lower_s, 3)

    def test_pre_effective_access_loss_is_distinct_endpoint(self):
        early_denied = projection(
            hris=True, iam=True, sessions=0, probe=AccessProbe.DENY
        )
        outcome = run(
            interval("s1", 0, 4, PRE),
            interval("s1", 4, 10, early_denied),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, POST),
        )
        self.assertEqual(outcome.premature_access_denial.lower_s, 6)
        self.assertEqual(outcome.postdeadline_access.upper_s, 0)
        self.assertEqual(outcome.joint_violation.lower_s, 6)

    def test_missing_interval_is_not_imputed_to_no_harm(self):
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            # Post-deadline [15,20) is unobserved.
            interval("s1", 20, 30, POST),
        )
        self.assertEqual(outcome.joint_violation.lower_s, 0)
        self.assertEqual(outcome.joint_violation.upper_s, 5)
        self.assertEqual(outcome.postdeadline_access.upper_s, 5)
        self.assertEqual(outcome.subjects[0].missing_or_unattested_s, 5)
        self.assertFalse(outcome.identified)

    def test_endpoint_snapshot_cannot_claim_continuous_observation(self):
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, POST, EvidenceKind.SNAPSHOT_ONLY),
        )
        self.assertEqual(outcome.joint_violation.upper_s, 15)
        self.assertFalse(outcome.identified)

    def test_incomplete_projection_stays_unknown_unless_violation_is_definite(self):
        unknown = projection(
            hris=False,
            iam=None,
            sessions=0,
            probe=AccessProbe.UNKNOWN,
        )
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, unknown),
        )
        self.assertEqual(outcome.joint_violation.upper_s, 15)
        self.assertEqual(outcome.joint_violation.lower_s, 0)

        known_violation = projection(
            hris=True,
            iam=None,
            sessions=0,
            probe=AccessProbe.UNKNOWN,
        )
        outcome2 = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, known_violation),
        )
        self.assertEqual(outcome2.joint_violation.lower_s, 15)
        self.assertEqual(outcome2.joint_violation.upper_s, 15)

    def test_clock_error_widens_uncertainty_near_deadline(self):
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, POST),
            skew=1,
        )
        self.assertGreater(outcome.subjects[0].clock_uncertain_s, 0)
        self.assertGreater(outcome.joint_violation.upper_s, 0)
        self.assertLessEqual(outcome.joint_violation.lower_s, outcome.joint_violation.upper_s)

    def test_multiple_subjects_are_aggregated_in_subject_seconds(self):
        policies = (
            SubjectPolicy("s1", effective_at_s=10, grace_s=5),
            SubjectPolicy("s2", effective_at_s=10, grace_s=5),
        )
        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 20, BAD_POST),
            interval("s1", 20, 30, POST),
            interval("s2", 0, 10, PRE),
            interval("s2", 10, 15, PRE),
            interval("s2", 15, 20, BAD_POST),
            interval("s2", 20, 30, POST),
            subjects=policies,
        )
        self.assertEqual(outcome.joint_violation.lower_s, 10)
        self.assertEqual(outcome.joint_violation.upper_s, 10)

    def test_unenumerated_subject_and_overlap_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside declared universe"):
            run(interval("s2", 0, 30, PRE))
        with self.assertRaisesRegex(ValueError, "overlapping"):
            run(interval("s1", 0, 16, PRE), interval("s1", 15, 30, POST))

    def test_boundaries_and_invalid_data_are_rejected(self):
        with self.assertRaises(ValueError):
            run(interval("s1", 0, 35, PRE))
        with self.assertRaises(ValueError):
            run(interval("s1", 10, 10, PRE))
        with self.assertRaises(ValueError):
            JointProjection(True, True, -1, AccessProbe.ALLOW)
        with self.assertRaises(ValueError):
            run(subjects=(SubjectPolicy("s1", 10, 5), SubjectPolicy("s1", 10, 5)))

    def test_no_observations_gives_full_unknown_except_grace(self):
        outcome = run()
        self.assertEqual(outcome.joint_violation.lower_s, 0)
        self.assertEqual(outcome.joint_violation.upper_s, 25)
        self.assertEqual(outcome.subjects[0].transition_grace_s, 5)

    def test_no_calibration_of_risk_factor_registry(self):
        from baa_protocol.offboarding import OFFBOARDING_RISK_FACTOR_IDS_V1

        outcome = run(
            interval("s1", 0, 10, PRE),
            interval("s1", 10, 15, PRE),
            interval("s1", 15, 30, POST),
        )
        self.assertTrue(outcome.identified)
        self.assertEqual(OFFBOARDING_RISK_FACTOR_IDS_V1, {})


if __name__ == "__main__":
    unittest.main()
