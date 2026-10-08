"""Offline P2 archive cryptographic/source invariants, no live product requests."""
import hashlib
import io
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from baa_protocol.maintenance_archive_qualifier import qualify_archived_maintenance
from baa_protocol.maintenance_model_replay import load_maintenance_windows, SOURCES

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments/p2_readonly_maintenance_replay_v1.json"


def records(window):
    rows = []
    for round_number, values in enumerate(window.observations):
        for source in SOURCES:
            rows.append({
                "round": round_number,
                "source": source,
                "result": values[source],
                "capability_fingerprint": (
                    "sha256-reference"
                    if source == "runtime_capabilities"
                    and values["capability_contract"] == "qualified"
                    else None
                ),
            })
    return rows


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in files.items():
            archive.writestr(name, json.dumps(value, sort_keys=True))
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ArchiveQualificationTests(unittest.TestCase):
    def make_archives(self, folder):
        windows = load_maintenance_windows(WORKLOAD)
        triage = {
            "results": [
                {
                    "case": case,
                    "qualified": True,
                    "assessment": {"status": windows[i].expected_final},
                    "simulated_instrument_faults": 0 if i == 0 else 1,
                    "records": records(windows[i]),
                }
                for i, case in enumerate((
                    "normal", "observer_transport_gap", "observer_contract_anomaly"
                ))
            ]
        }
        actual = {
            "qualified": True,
            "actual_keycloak_outage_observed": True,
            "unpause_succeeded": True,
            "real_business_effect_count": 0,
            "assessment": {"status": windows[3].expected_final},
            "snapshot": {"records": records(windows[3])},
        }
        a = folder / "triage.zip"
        b = folder / "outage.zip"
        a_sha = write_zip(a, {"maintenance-triage.json": triage})
        b_sha = write_zip(b, {"real-isolated-outage.json": actual})
        remapped = tuple(
            replace(w, archive_sha256=a_sha if i < 3 else b_sha)
            for i, w in enumerate(windows)
        )
        return remapped, a, b

    def test_two_actual_bytes_checks_and_raw_sensor_rounds(self):
        with TemporaryDirectory() as tmp:
            windows, a, b = self.make_archives(Path(tmp))
            result = qualify_archived_maintenance(
                windows, triage_zip=a, outage_zip=b
            )
            self.assertTrue(result["qualified"])
            self.assertEqual(result["workload_episode_count"], 4)
            self.assertEqual(result["real_process_pause_episodes"], 1)
            self.assertEqual(result["observer_only_perturbation_episodes"], 2)

    def test_modified_archive_fails_even_if_status_claims_unchanged(self):
        with TemporaryDirectory() as tmp:
            windows, a, b = self.make_archives(Path(tmp))
            with b.open("ab") as handle:
                handle.write(b"tamper")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                qualify_archived_maintenance(windows, triage_zip=a, outage_zip=b)

    def test_workload_status_cannot_be_rewritten_without_detection(self):
        with TemporaryDirectory() as tmp:
            windows, a, b = self.make_archives(Path(tmp))
            changed = list(windows)
            samples = list(changed[1].observations)
            modified = dict(samples[1])
            modified["keycloak_realm"] = "ok"
            samples[1] = modified
            changed[1] = replace(changed[1], observations=tuple(samples))
            with self.assertRaisesRegex(ValueError, "differs from archived"):
                qualify_archived_maintenance(tuple(changed), triage_zip=a, outage_zip=b)

    def test_actual_fault_must_be_confirmed_not_merely_labellled(self):
        with TemporaryDirectory() as tmp:
            windows, a, b = self.make_archives(Path(tmp))
            with zipfile.ZipFile(b) as z:
                actual = json.loads(z.read("real-isolated-outage.json"))
            actual["actual_keycloak_outage_observed"] = False
            revised_digest = write_zip(b, {"real-isolated-outage.json": actual})
            fixed = tuple(
                replace(w, archive_sha256=revised_digest)
                if w.episode_id == "M04" else w for w in windows
            )
            with self.assertRaisesRegex(ValueError, "not qualified"):
                qualify_archived_maintenance(fixed, triage_zip=a, outage_zip=b)


if __name__ == "__main__":
    unittest.main()
