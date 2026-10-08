"""Synthetic qualification tests for the read-only P3 collector contract."""

import unittest

from baa_protocol.temporal_collector import (
    CollectorSources,
    ReadOnlyCollector,
    bracket_snapshots,
    classify_point,
)
from baa_protocol.temporal_outcome import (
    AccessProbe,
    EvidenceKind,
    SubjectPolicy,
    measure_offboarding,
)


def sources():
    return CollectorSources(
        collector_id="collector:fixture",
        hris_source="isolated-odoo-readback",
        iam_source="isolated-keycloak-readback",
        access_probe_source="isolated-relying-party-probe",
        hris_reader_domain="odoo:verifier",
        iam_reader_domain="keycloak:verifier",
        access_probe_domain="test-principal",
        hris_writer_domain="odoo:writer",
        iam_writer_domain="keycloak:writer",
    )


def collector(
    *,
    hris=lambda _: False,
    iam=lambda _: (False, 0),
    probe=lambda _: AccessProbe.DENY,
):
    return ReadOnlyCollector(
        sources=sources(),
        read_hris_active=hris,
        read_iam_state=iam,
        probe_access=probe,
    )


class ReadOnlyCollectorTests(unittest.TestCase):
    def test_compliant_control_has_no_point_violation(self):
        x = collector().capture(subject_id="s1", observed_at_s=20, sample_id="ok")
        self.assertIs(classify_point(x, policy=SubjectPolicy("s1", 10, 5)), False)
        self.assertEqual(x.errors, ())
        self.assertEqual(x.kind, EvidenceKind.SNAPSHOT_ONLY)

    def test_injected_violation_is_detected_by_independent_access_probe(self):
        # Product fields appear revoked; real access probe is still allowed.
        x = collector(
            probe=lambda _: AccessProbe.ALLOW
        ).capture(subject_id="s1", observed_at_s=20, sample_id="violation")
        self.assertIs(classify_point(x, policy=SubjectPolicy("s1", 10, 5)), True)

    def test_probe_outage_is_unknown_not_access_denial(self):
        def failed(_):
            raise TimeoutError("probe endpoint unavailable")
        x = collector(probe=failed).capture(
            subject_id="s1", observed_at_s=20, sample_id="outage"
        )
        self.assertEqual(x.projection.access_probe, AccessProbe.UNKNOWN)
        self.assertIn("probe:TimeoutError", x.errors)
        self.assertIs(classify_point(x, policy=SubjectPolicy("s1", 10, 5)), None)

    def test_readback_failure_with_known_violation_is_still_a_point_violation(self):
        def failed(_):
            raise ConnectionError("HRIS unavailable")
        x = collector(
            hris=failed,
            iam=lambda _: (True, 2),
        ).capture(subject_id="s1", observed_at_s=20, sample_id="partial")
        self.assertEqual(x.projection.hris_active, None)
        self.assertIn("hris:ConnectionError", x.errors)
        self.assertIs(classify_point(x, policy=SubjectPolicy("s1", 10, 5)), True)

    def test_two_matching_snapshots_do_not_establish_interval_y(self):
        c = collector()
        first = c.capture(subject_id="s1", observed_at_s=15, sample_id="first")
        second = c.capture(subject_id="s1", observed_at_s=30, sample_id="second")
        bracket = bracket_snapshots(first, second)
        self.assertEqual(bracket.kind, EvidenceKind.SNAPSHOT_ONLY)

        outcome = measure_offboarding(
            policies=(SubjectPolicy("s1", 10, 5),),
            observations=(bracket,),
            horizon_start_s=15,
            horizon_end_s=30,
        )
        self.assertEqual(outcome.joint_violation.lower_s, 0)
        self.assertEqual(outcome.joint_violation.upper_s, 15)
        self.assertFalse(outcome.identified)

    def test_collector_refuses_writer_verifier_domain_overlap(self):
        cfg = sources()
        with self.assertRaisesRegex(ValueError, "HRIS reader"):
            CollectorSources(
                collector_id=cfg.collector_id,
                hris_source=cfg.hris_source,
                iam_source=cfg.iam_source,
                access_probe_source=cfg.access_probe_source,
                hris_reader_domain=cfg.hris_writer_domain,
                iam_reader_domain=cfg.iam_reader_domain,
                access_probe_domain=cfg.access_probe_domain,
                hris_writer_domain=cfg.hris_writer_domain,
                iam_writer_domain=cfg.iam_writer_domain,
            )

    def test_bad_types_do_not_silently_become_authoritative(self):
        x = collector(
            hris=lambda _: 0,
            iam=lambda _: (False, -1),
            probe=lambda _: False,
        ).capture(subject_id="s1", observed_at_s=20, sample_id="badtypes")
        self.assertIsNone(x.projection.hris_active)
        self.assertIsNone(x.projection.iam_enabled)
        self.assertIsNone(x.projection.active_sessions)
        self.assertEqual(x.projection.access_probe, AccessProbe.UNKNOWN)
        self.assertEqual(len(x.errors), 3)

    def test_different_subjects_cannot_be_bracketed(self):
        c = collector()
        first = c.capture(subject_id="s1", observed_at_s=15, sample_id="a")
        second = c.capture(subject_id="s2", observed_at_s=20, sample_id="b")
        with self.assertRaisesRegex(ValueError, "different subjects"):
            bracket_snapshots(first, second)


if __name__ == "__main__":
    unittest.main()
