import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_canary_feedback_study import (
    FEEDBACK_POLICIES,
    HORIZONS,
    _adaptive_feedback_prompt,
    _mechanical_correction,
    run_canary_feedback_study,
)
from baa_protocol.prospective_canary_study import (
    CanaryAction,
    CanarySimulator,
    load_canary_workload,
)


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryFeedbackStudyTests(unittest.TestCase):
    def setUp(self):
        _, self.episodes = load_canary_workload(WORKLOAD)

    def test_v2_reuses_frozen_v1_workload_without_mutation(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(
            sorted({episode.study_group for episode in self.episodes}),
            [
                "clean_progression",
                "evidence_maturation",
                "guardrail_recovery",
                "irrecoverable_control",
                "lost_ack_recovery",
                "stale_route_refresh",
            ],
        )

    def test_corrective_feedback_is_mechanical_next_stage_only(self):
        episode = next(
            item for item in self.episodes
            if item.study_group == "stale_route_refresh"
        )
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator.apply_events(1)
        action = CanaryAction(
            kind="apply",
            experiment_id=simulator.context["experiment_id"],
            target_id=simulator.context["target_id"],
            control_release_id=simulator.context["control_release_id"],
            candidate_deployment_id=simulator.context["candidate_deployment_id"],
            stage_index=2,
            candidate_weight_percent=100,
            state_version=simulator.context["state_version"],
            operation_id="skip",
        )
        self.assertEqual(simulator.execute(action), "deny")
        correction = _mechanical_correction(simulator)
        self.assertIsNotNone(correction)
        self.assertEqual(
            correction["safe_next_action"],
            {
                "kind": "apply",
                "stage_index": 1,
                "candidate_weight_percent": 50,
            },
        )
        self.assertNotIn("hidden", json.dumps(correction))

    def test_feedback_policy_names_are_not_in_model_visible_prompt(self):
        episode = self.episodes[0]
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        for policy in FEEDBACK_POLICIES:
            prompt = _adaptive_feedback_prompt(
                episode,
                simulator,
                feedback_policy=policy,
            )
            self.assertNotIn(f'"feedback_policy": "{policy}"', prompt)
            self.assertNotIn("bounded_action_protocol", prompt)
            self.assertNotIn("self_check", prompt)
            self.assertNotIn("external_record_audit", prompt)

    def test_minimal_feedback_strips_reason(self):
        episode = next(
            item for item in self.episodes
            if item.study_group == "stale_route_refresh"
        )
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator._record(
            phase="admission",
            disposition="deny",
            reason="proposal is stale or skips a stage",
        )
        prompt = _adaptive_feedback_prompt(
            episode,
            simulator,
            feedback_policy="minimal",
        )
        self.assertNotIn("proposal is stale or skips a stage", prompt)

    def test_scripted_feedback_study_has_complete_factorial_denominators(self):
        class ScriptedModel:
            model_id = "scripted"

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
                if marker == "Episode state:\n" and value.get("assurance_feedback"):
                    next_action = value["assurance_feedback"].get("safe_next_action")
                    if next_action and next_action["kind"] == "apply":
                        action = {
                            "kind": "apply",
                            "experiment_id": runtime["experiment_id"],
                            "target_id": runtime["target_id"],
                            "control_release_id": runtime["control_release_id"],
                            "candidate_deployment_id": runtime["candidate_deployment_id"],
                            "stage_index": next_action["stage_index"],
                            "candidate_weight_percent": next_action["candidate_weight_percent"],
                            "state_version": runtime["state_version"],
                            "operation_id": f"{episode_id}:{phase}:corrected",
                        }
                        return json.dumps({"actions": [action]}), {}, 0.01

                if int(runtime["current_weight_percent"]) == 10:
                    action = {
                        "kind": "apply",
                        "experiment_id": runtime["experiment_id"],
                        "target_id": runtime["target_id"],
                        "control_release_id": runtime["control_release_id"],
                        "candidate_deployment_id": runtime["candidate_deployment_id"],
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "state_version": runtime["state_version"],
                        "operation_id": f"{episode_id}:{phase}:skip",
                    }
                else:
                    action = {"kind": "wait"}
                return json.dumps({"actions": [action]}), {}, 0.01

        target = tuple(
            item for item in self.episodes
            if item.study_group == "stale_route_refresh"
        )[:1]
        result = run_canary_feedback_study(
            ScriptedModel(),
            target,
            horizons=(2, 4),
        )

        for policy in FEEDBACK_POLICIES:
            for horizon in (2, 4):
                self.assertEqual(
                    result["cells"][policy][str(horizon)]["episodes"],
                    1,
                )

        self.assertEqual(
            result["cells"]["corrective"]["4"]["unsafe_transitions"],
            0,
        )
        self.assertGreaterEqual(
            result["cells"]["corrective"]["4"]["stale_route"]["completed"],
            result["cells"]["diagnostic"]["4"]["stale_route"]["completed"],
        )

    def test_frozen_horizons_are_increasing(self):
        self.assertEqual(HORIZONS, (2, 4, 8))


if __name__ == "__main__":
    unittest.main()
