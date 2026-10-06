import json
from pathlib import Path
import unittest

from baa_protocol.prospective_canary_evidence_horizon_study import (
    HORIZONS,
    _snapshot,
    run_canary_evidence_horizon_study,
)
from baa_protocol.prospective_canary_evidence_study import EVIDENCE_POLICIES
from baa_protocol.prospective_canary_study import load_canary_workload


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryEvidenceHorizonStudyTests(unittest.TestCase):
    def setUp(self):
        version, self.episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")

    def stale_episode(self):
        return next(
            episode
            for episode in self.episodes
            if episode.logical_name == "stale-route-refresh-b"
        )

    def test_v4_freezes_v1_workload_two_evidence_policies_and_h4_h8(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(EVIDENCE_POLICIES, ("no_reacquire", "reacquire"))
        self.assertEqual(HORIZONS, (4, 8))

    def test_h4_snapshot_is_a_pure_prefix_score(self):
        class FakeResult:
            def to_dict(self):
                return {
                    "metrics": {},
                    "delegable": False,
                    "completed": False,
                    "study_group": "fake",
                }

        class MutatingSimulator:
            def __init__(self):
                self.finalized = False

            def finalize(self, **kwargs):
                self.finalized = True
                return FakeResult()

        simulator = MutatingSimulator()
        row = _snapshot(
            simulator,
            evidence_policy="reacquire",
            horizon=4,
            evidence_reacquisitions=1,
            model_calls=5,
            input_tokens=10,
            output_tokens=2,
        )
        self.assertFalse(simulator.finalized)
        self.assertEqual(row["horizon"], 4)
        self.assertEqual(row["evidence_reacquisitions"], 1)

    def test_scripted_interaction_requires_reacquisition_and_extra_horizon(self):
        class ScriptedModel:
            model_id = "scripted-evidence-horizon"

            def generate(
                self,
                prompt,
                *,
                episode_id,
                capability_level,
                phase,
                regime,
            ):
                marker = (
                    "Episode state:\n"
                    if "Episode state:\n" in prompt
                    else "Episode:\n"
                )
                value = json.loads(prompt.split(marker, 1)[1])
                runtime = (
                    value["runtime_state"]
                    if marker == "Episode state:\n"
                    else value["evidence"]["runtime_state"]
                )
                ids = {
                    "experiment_id": runtime["experiment_id"],
                    "target_id": runtime["target_id"],
                    "control_release_id": runtime["control_release_id"],
                    "candidate_deployment_id": runtime[
                        "candidate_deployment_id"
                    ],
                    "state_version": runtime["state_version"],
                }
                assurance = value.get("assurance_feedback") or {}
                safe = assurance.get("safe_next_action")

                if phase in {
                    "initial-shared",
                    "adaptive-1",
                    "adaptive-2",
                    "adaptive-4",
                }:
                    action = {"kind": "wait"}
                elif phase == "adaptive-3":
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:skip",
                    }
                elif (
                    phase.endswith("-repair")
                    and isinstance(safe, dict)
                    and safe.get("kind") == "apply"
                ):
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": safe["stage_index"],
                        "candidate_weight_percent": safe[
                            "candidate_weight_percent"
                        ],
                        "operation_id": f"{episode_id}:{phase}:repair",
                    }
                elif int(runtime["current_weight_percent"]) == 10:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 1,
                        "candidate_weight_percent": 50,
                        "operation_id": f"{episode_id}:{phase}:to-50",
                    }
                elif int(runtime["current_weight_percent"]) == 50:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:to-100",
                    }
                else:
                    action = {"kind": "complete"}

                return json.dumps({"actions": [action]}), {}, 0.01

        result = run_canary_evidence_horizon_study(
            ScriptedModel(),
            (self.stale_episode(),),
        )

        def row(policy, horizon):
            return next(
                item
                for item in result["episodes"]
                if (
                    item["evidence_policy"] == policy
                    and item["horizon"] == horizon
                )
            )

        self.assertFalse(row("no_reacquire", 4)["delegable"])
        self.assertFalse(row("reacquire", 4)["delegable"])
        self.assertFalse(row("no_reacquire", 8)["delegable"])
        self.assertTrue(row("reacquire", 8)["delegable"])

        self.assertEqual(
            row("reacquire", 4)["evidence_reacquisitions"],
            1,
        )
        self.assertGreaterEqual(
            row("reacquire", 8)["evidence_reacquisitions"],
            2,
        )
        self.assertEqual(
            row("reacquire", 8)["metrics"]["unsafe_transitions"],
            0,
        )
        self.assertEqual(
            result["endpoints"]["stale_reacquire_contrast_h4"],
            0,
        )
        self.assertEqual(
            result["endpoints"]["stale_reacquire_contrast_h8"],
            1,
        )
        self.assertEqual(
            result["endpoints"]["stale_evidence_horizon_interaction"],
            1,
        )

    def test_identical_prompts_share_one_h8_physical_trajectory(self):
        class CountingWaitModel:
            model_id = "counting-wait"

            def __init__(self):
                self.calls = 0

            def generate(
                self,
                prompt,
                *,
                episode_id,
                capability_level,
                phase,
                regime,
            ):
                self.calls += 1
                return json.dumps(
                    {"actions": [{"kind": "wait"}]}
                ), {}, 0.0

        clean = (
            next(
                episode
                for episode in self.episodes
                if episode.study_group == "clean_progression"
            ),
        )
        model = CountingWaitModel()
        result = run_canary_evidence_horizon_study(model, clean)

        self.assertEqual(model.calls, 9)
        self.assertEqual(result["physical_sampling"]["calls"], 9)
        for policy in EVIDENCE_POLICIES:
            self.assertEqual(
                result["cells"][policy]["4"]["logical_model_calls"],
                5,
            )
            self.assertEqual(
                result["cells"][policy]["8"]["logical_model_calls"],
                9,
            )


if __name__ == "__main__":
    unittest.main()
