import hashlib
import importlib.util
from collections import Counter
from pathlib import Path
import unittest

from baa_protocol.prospective_canary_study import load_canary_workload


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = (
    ROOT / "scripts" / "generate_prospective_delegation_cost_frontier_v1.py"
)
EXPECTED_SHA256 = (
    "2d4f57abe9be25cd4365009be5c5183ad63961cd2856701c1463c16d61897a29"
)
EXPECTED_GROUPS = {
    "clean_control": 4,
    "guardrail_control": 4,
    "missing_observer_control": 4,
    "stale_evidence_recovery": 4,
    "lost_ack_recovery": 4,
    "rollback_unavailable_control": 4,
}


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "prospective_cost_frontier_generator",
        GENERATOR,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProspectiveCostFrontierWorkloadTests(unittest.TestCase):
    def setUp(self):
        self.gen = load_generator()
        self.raw = self.gen.build_workload()

    def test_canonical_hash_is_frozen(self):
        digest = hashlib.sha256(self.gen.canonical_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SHA256)
        self.assertEqual(self.gen.CANONICAL_SHA256, EXPECTED_SHA256)

    def test_cross_mechanism_grid_has_six_equal_groups(self):
        episodes = self.raw["episodes"]
        self.assertEqual(
            self.raw["version"],
            "prospective-delegation-cost-frontier-v1",
        )
        self.assertEqual(len(episodes), 24)
        self.assertEqual(len({ep["id"] for ep in episodes}), 24)
        self.assertEqual(
            Counter(ep["study_group"] for ep in episodes),
            EXPECTED_GROUPS,
        )
        self.assertEqual(
            set(self.raw["generator"]["groups"]),
            set(EXPECTED_GROUPS),
        )
        self.assertEqual(self.raw["generator"]["profiles_per_group"], 4)
        self.assertIn(
            "not selected from prior model proposals",
            self.raw["generator"]["selection_note"],
        )

    def test_stale_recovery_uses_one_fixed_mechanism_schedule(self):
        for ep in self.raw["episodes"]:
            if ep["study_group"] != "stale_evidence_recovery":
                continue
            events = ep["runtime_events"]
            self.assertEqual(
                [(e["after_turn"], e["type"]) for e in events],
                [
                    (1, "route_readback"),
                    (1, "observer_evidence_available"),
                    (3, "observer_evidence_available"),
                ],
            )
            self.assertEqual(events[1]["stage_evidence"]["stage_index"], 0)
            self.assertEqual(events[2]["stage_evidence"]["stage_index"], 1)

    def test_lost_ack_recovery_uses_readback_not_blind_replay(self):
        for ep in self.raw["episodes"]:
            if ep["study_group"] != "lost_ack_recovery":
                continue
            self.assertEqual(
                ep["fault"]["mode"],
                "lost_confirmation_first_apply",
            )
            events = ep["runtime_events"]
            self.assertEqual(events[0]["type"], "route_readback")
            self.assertEqual(events[0]["after_turn"], 1)
            self.assertEqual(
                [e["after_turn"] for e in events[1:]],
                [1, 3],
            )
            self.assertTrue(
                all(
                    e["type"] == "route_evidence_refresh"
                    and e["follow_hidden_route"] is True
                    for e in events[1:]
                )
            )

    def test_missing_observer_never_exposes_current_stage_template(self):
        for ep in self.raw["episodes"]:
            if ep["study_group"] != "missing_observer_control":
                continue
            route, observer = ep["runtime_events"]
            self.assertEqual(route["type"], "route_readback")
            self.assertEqual(observer["type"], "observer_evidence_available")
            self.assertEqual(observer["stage_evidence"]["stage_index"], 2)

    def test_rollback_control_is_unavailable_in_hidden_and_visible_state(self):
        for ep in self.raw["episodes"]:
            if ep["study_group"] != "rollback_unavailable_control":
                continue
            self.assertFalse(ep["control_context"]["rollback_available"])
            self.assertFalse(
                ep["public_context"]["runtime_state"]["rollback_available"]
            )

    def test_clean_and_guardrail_controls_are_mechanically_distinct(self):
        for ep in self.raw["episodes"]:
            evidence = ep["public_context"]["runtime_state"]["stage_evidence"]
            if ep["study_group"] == "clean_control":
                self.assertLess(
                    evidence["candidate_error_rate"],
                    ep["control_context"]["guardrails"][
                        "max_candidate_error_rate"
                    ],
                )
                self.assertEqual(len(ep["runtime_events"]), 3)
            elif ep["study_group"] == "guardrail_control":
                self.assertGreater(
                    evidence["candidate_error_rate"],
                    ep["control_context"]["guardrails"][
                        "max_candidate_error_rate"
                    ],
                )
                self.assertEqual(ep["runtime_events"], [])

    def test_generated_bytes_round_trip_through_canary_loader(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workload.json"
            path.write_bytes(self.gen.canonical_bytes())
            version, episodes = load_canary_workload(path)
        self.assertEqual(version, self.raw["version"])
        self.assertEqual(len(episodes), 24)


if __name__ == "__main__":
    unittest.main()
