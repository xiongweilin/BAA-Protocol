import hashlib
import importlib.util
from pathlib import Path
import unittest

from baa_protocol.prospective_canary_study import load_canary_workload


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_prospective_canary_v5_robustness.py"
EXPECTED_SHA256 = "e1c5802edcbc9c1f33d5a72c18a102d6af406ca7e25962a71a2fb62b2b232bd9"
EXPECTED_GROUPS = {
    "recoverable_lag_early": 4,
    "recoverable_lag_mid": 4,
    "recoverable_lag_late": 4,
    "missing_observer_control": 4,
    "guardrail_control": 4,
    "clean_control": 4,
}


def load_generator():
    spec = importlib.util.spec_from_file_location("canary_v5_generator", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CanaryV5RobustnessWorkloadTests(unittest.TestCase):
    def setUp(self):
        self.gen = load_generator()
        self.raw = self.gen.build_workload()

    def test_canonical_hash_is_frozen(self):
        digest = hashlib.sha256(self.gen.canonical_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SHA256)
        self.assertEqual(self.gen.CANONICAL_SHA256, EXPECTED_SHA256)

    def test_grid_has_24_unique_episodes_and_six_equal_strata(self):
        episodes = self.raw["episodes"]
        self.assertEqual(self.raw["version"], "prospective-canary-v5-robustness")
        self.assertEqual(len(episodes), 24)
        self.assertEqual(len({ep["id"] for ep in episodes}), 24)
        self.assertEqual(len({ep["logical_name"] for ep in episodes}), 24)
        counts = {}
        for ep in episodes:
            counts[ep["study_group"]] = counts.get(ep["study_group"], 0) + 1
        self.assertEqual(counts, EXPECTED_GROUPS)

    def test_recovery_grid_is_parameterized_not_trace_selected(self):
        metadata = self.raw["generator"]
        self.assertEqual(
            metadata["timing_grid"],
            {
                "recoverable_lag_early": [1, 2],
                "recoverable_lag_mid": [2, 3],
                "recoverable_lag_late": [3, 4],
            },
        )
        self.assertEqual(metadata["profiles_per_stratum"], 4)
        self.assertIn("not selected from v4 model traces", metadata["selection_note"])

    def test_recoverable_strata_have_route_alignment_and_future_stage_evidence(self):
        for ep in self.raw["episodes"]:
            if not ep["study_group"].startswith("recoverable_lag_"):
                continue
            events = ep["runtime_events"]
            self.assertEqual(len(events), 3)
            self.assertEqual(events[0]["type"], "route_readback")
            self.assertEqual(events[1]["type"], "observer_evidence_available")
            self.assertEqual(events[1]["stage_evidence"]["stage_index"], 0)
            self.assertEqual(events[2]["type"], "observer_evidence_available")
            self.assertEqual(events[2]["stage_evidence"]["stage_index"], 1)
            self.assertEqual(events[1]["after_turn"], events[0]["after_turn"])
            self.assertGreaterEqual(
                events[2]["after_turn"],
                events[1]["after_turn"],
            )

    def test_missing_observer_control_never_exposes_current_stage_fixture(self):
        for ep in self.raw["episodes"]:
            if ep["study_group"] != "missing_observer_control":
                continue
            route_event, observer_event = ep["runtime_events"]
            self.assertEqual(route_event["type"], "route_readback")
            self.assertEqual(observer_event["type"], "observer_evidence_available")
            self.assertEqual(observer_event["stage_evidence"]["stage_index"], 2)

    def test_clean_and_guardrail_controls_are_mechanically_distinct(self):
        for ep in self.raw["episodes"]:
            ev = ep["public_context"]["runtime_state"]["stage_evidence"]
            if ep["study_group"] == "clean_control":
                self.assertLess(
                    ev["candidate_error_rate"],
                    ep["control_context"]["guardrails"]["max_candidate_error_rate"],
                )
                self.assertTrue(ep["runtime_events"])
            if ep["study_group"] == "guardrail_control":
                self.assertGreater(
                    ev["candidate_error_rate"],
                    ep["control_context"]["guardrails"]["max_candidate_error_rate"],
                )
                self.assertEqual(ep["runtime_events"], [])

    def test_generated_bytes_round_trip_through_frozen_loader(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workload.json"
            path.write_bytes(self.gen.canonical_bytes())
            version, episodes = load_canary_workload(path)
        self.assertEqual(version, "prospective-canary-v5-robustness")
        self.assertEqual(len(episodes), 24)


if __name__ == "__main__":
    unittest.main()
