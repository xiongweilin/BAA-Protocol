"""Offline source verifier tests; no model gateway or product network."""
from __future__ import annotations

import hashlib
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from baa_protocol import p2_maintenance_source_qualification as qual
from baa_protocol.p2_readonly_maintenance_model import load_cases

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments/p2_readonly_maintenance_v1.json"
SOURCES = ("runtime_health", "runtime_capabilities", "keycloak_realm", "odoo_root")


def sensor_records(projected):
    return [
        {
            "round": item["round"],
            "source": item["source"],
            "result": item["result"],
            "capability_fingerprint": (
                "frozen-verified-real-source-fingerprint"
                if item["source"] == "runtime_capabilities"
                and item["contract_qualified"]
                else None
            ),
        }
        for item in projected
    ]


def make_artifact(path, workload, *, actual_qualified=True, distinguish=False):
    cases = {e["id"]: e for e in workload["episodes"]}
    actual = (
        cases["M04"]["initial"]
        + [x for block in cases["M04"]["next_rounds"] for x in block]
    )
    assert len(actual) == 16

    healthy_first_two = cases["M01"]["initial"]
    normal = [dict(r) for r in healthy_first_two]
    for offset in (2, 3):
        for item in healthy_first_two[-4:]:
            normal.append({**item, "round": offset})
    gap = [dict(r) for r in actual]
    if distinguish:
        gap[6]["result"] = "ok"
    anomaly = cases["M05"]["initial"]
    scenarios = [
        ("normal", normal, 0, "verified_stable"),
        ("observer_transport_gap", gap, 1, "verified_recovered_evidence"),
        ("observer_contract_anomaly", anomaly, 1, "escalate_contract_or_authority"),
    ]
    diagnostic = {
        "results": [
            {
                "case": name,
                "qualified": True,
                "simulated_instrument_faults": count,
                "assessment": {"status": status},
                "records": sensor_records(rows),
            }
            for name, rows, count, status in scenarios
        ]
    }
    effect = {
        "qualified": actual_qualified,
        "actual_keycloak_outage_observed": actual_qualified,
        "other_three_sources_remained_ok_in_fault_round": True,
        "unpause_succeeded": True,
        "real_business_effect_count": 0,
        "assessment": {"status": "verified_recovered_evidence"},
        "snapshot": {"records": sensor_records(actual)},
    }
    provenance = {
        "run_id": qual.SOURCE_RUN_ID,
        "AIOS_SHA": qual.SOURCE_PR_CHECKOUT_SHA,
        "attempt": "1",
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for key, value in (
            ("provenance.json", provenance),
            ("real-isolated-outage.json", effect),
            ("maintenance-triage.json", diagnostic),
        ):
            z.writestr(key, json.dumps(value, sort_keys=True))
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FrozenP2SourceQualifierTests(unittest.TestCase):
    def setUp(self):
        self.original = load_cases(WORKLOAD)

    def qualify_fixture(self, path, raw, digest):
        from copy import deepcopy
        payload = deepcopy(raw)
        payload["provenance"]["source_archive_sha256"] = digest
        with patch.object(qual, "SOURCE_ARCHIVE_SHA256", digest):
            return qual.qualify_p2_source_archive(payload, path)

    def test_accepted_zip_must_support_all_five_views(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original)
            result = self.qualify_fixture(p, self.original, digest)
            self.assertTrue(result["qualified"])
            self.assertEqual(result["verified_p2_episodes"], 5)
            self.assertTrue(result["observer_only_gap_indistinguishable_at_sensor_level"])
            self.assertEqual(result["new_model_calls"], 0)

    def test_byte_tampering_fails_before_model_sampling(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original)
            with p.open("ab") as f:
                f.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                self.qualify_fixture(p, self.original, digest)

    def test_unverified_actual_pause_is_not_an_observed_real_outage(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original, actual_qualified=False)
            with self.assertRaisesRegex(ValueError, "not qualified"):
                self.qualify_fixture(p, self.original, digest)

    def test_correlated_obs_only_gap_cannot_claim_a_distinct_sensor_cause(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original, distinguish=True)
            with self.assertRaisesRegex(ValueError, "distinguishable"):
                self.qualify_fixture(p, self.original, digest)

    def test_altered_model_workload_fails_source_projection_match(self):
        from copy import deepcopy
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original)
            workload = deepcopy(self.original)
            workload["episodes"][1]["initial"][6]["result"] = "ok"
            with self.assertRaisesRegex(ValueError, "faithful projection"):
                self.qualify_fixture(p, workload, digest)

    def test_untrusted_pins_fail_even_if_archive_bytes_match(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "artifact.zip"
            digest = make_artifact(p, self.original)
            from copy import deepcopy
            altered = deepcopy(self.original)
            altered["provenance"]["source_head"] = "fake-head"
            with self.assertRaisesRegex(ValueError, "metadata"):
                self.qualify_fixture(p, altered, digest)


if __name__ == "__main__":
    unittest.main()
