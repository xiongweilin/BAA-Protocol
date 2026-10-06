import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.prospective_canary_evidence_study import (
    EVIDENCE_POLICIES,
    HORIZONS,
    EvidenceRetentionSimulator,
    run_canary_evidence_study,
)
from baa_protocol.prospective_canary_study import load_canary_workload


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryEvidenceStudyTests(unittest.TestCase):
    def setUp(self):
        version, self.episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")

    def _stale(self):
        return next(
            episode for episode in self.episodes
            if episode.study_group == "stale_route_refresh"
        )

    def test_v3_reuses_frozen_v1_workload(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(EVIDENCE_POLICIES, ("latest_only", "versioned_current_stage"))
        self.assertEqual(HORIZONS, (4, 8))

    def test_versioned_policy_retains_current_stage_evidence_after_latest_advances(self):
        episode = self._stale()
        latest = EvidenceRetentionSimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="latest_only",
        )
        versioned = EvidenceRetentionSimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="versioned_current_stage",
        )

        for simulator in (latest, versioned):
            simulator.apply_events(1)
            self.assertEqual(simulator.visible["current_stage_index"], 0)
            self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 0)
            simulator.apply_events(2)
            self.assertEqual(simulator.visible["current_stage_index"], 0)
            self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 1)

        self.assertEqual(latest._evidence().stage_index, 1)
        selected = versioned._evidence()
        self.assertIsNotNone(selected)
        self.assertEqual(selected.stage_index, 0)
        self.assertEqual(selected.weight_percent, 10)
        self.assertGreaterEqual(versioned.evidence_retrievals, 1)

    def test_versioned_policy_never_substitutes_evidence_for_another_route(self):
        episode = self._stale()
        simulator = EvidenceRetentionSimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="versioned_current_stage",
        )
        simulator.apply_events(1)
        simulator.apply_events(2)
        simulator.visible["current_stage_index"] = 2
        simulator.visible["current_weight_percent"] = 100
        self.assertIsNone(simulator._evidence())
        self.assertGreaterEqual(simulator.evidence_misses, 1)

    def test_evidence_store_does_not_change_model_visible_latest_evidence(self):
        episode = self._stale()
        simulator = EvidenceRetentionSimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="versioned_current_stage",
        )
        simulator.apply_events(1)
        simulator.apply_events(2)
        self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 1)
        retained = simulator._evidence()
        self.assertEqual(retained.stage_index, 0)
        self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 1)

    def test_scripted_current_stage_retention_can_recover_stale_route(self):
        class ScriptedModel:
            model_id = "scripted-evidence"

            def generate(
                self,
                prompt,
                *,
                episode_id,
                capability_level,
                phase,
                regime,
            ):
                marker = "Episode state:\n" if "Episode state:\n" in prompt else "Episode:\n"
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
                    "candidate_deployment_id": runtime["candidate_deployment_id"],
                    "state_version": runtime["state_version"],
                }

                correction = value.get("assurance_feedback") if marker == "Episode state:\n" else None
                if phase == "initial-shared":
                    action = {"kind": "wait"}
                elif correction and correction.get("safe_next_action", {}).get("kind") == "apply":
                    next_action = correction["safe_next_action"]
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": next_action["stage_index"],
                        "candidate_weight_percent": next_action["candidate_weight_percent"],
                        "operation_id": f"{episode_id}:{phase}:repair",
                    }
                elif int(runtime["current_weight_percent"]) == 50:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:to-100",
                    }
                elif (
                    int(runtime["current_weight_percent"]) == 10
                    and phase.startswith("adaptive-")
                    and not phase.startswith("adaptive-1")
                ):
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:skip",
                    }
                else:
                    action = {"kind": "wait"}
                return json.dumps({"actions": [action]}), {}, 0.01

        target = tuple(
            episode for episode in self.episodes
            if episode.study_group == "stale_route_refresh"
        )[:1]
        result = run_canary_evidence_study(
            ScriptedModel(),
            target,
        )
        latest = result["cells"]["latest_only"]["4"]["stale_route"]
        versioned = result["cells"]["versioned_current_stage"]["4"]["stale_route"]
        self.assertEqual(latest["delegable_episodes"], 0)
        self.assertEqual(versioned["delegable_episodes"], 1)
        self.assertEqual(versioned["unsafe_transitions"], 0)
        self.assertGreaterEqual(versioned["evidence_retrievals"], 1)

    def test_identical_prompts_share_physical_samples_across_evidence_treatments(self):
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
                return json.dumps({"actions": [{"kind": "wait"}]}), {}, 0.0

        clean = tuple(
            episode for episode in self.episodes
            if episode.study_group == "clean_progression"
        )[:1]
        model = CountingWaitModel()
        result = run_canary_evidence_study(model, clean)

        self.assertEqual(model.calls, result["physical_sampling"]["calls"])
        self.assertLess(
            result["physical_sampling"]["calls"],
            sum(
                result["cells"][policy]["8"]["logical_model_calls"]
                for policy in EVIDENCE_POLICIES
            ),
        )


if __name__ == "__main__":
    unittest.main()
