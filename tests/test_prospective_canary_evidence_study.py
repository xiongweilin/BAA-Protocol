import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_canary_evidence_study import (
    EVIDENCE_POLICIES,
    HORIZON,
    STALE_EVIDENCE_REASON,
    _evidence_bank,
    _reacquire_current_stage_evidence,
    run_canary_evidence_recovery_study,
)
from baa_protocol.prospective_canary_study import (
    CanaryAction,
    CanarySimulator,
    load_canary_workload,
)


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryEvidenceRecoveryStudyTests(unittest.TestCase):
    def setUp(self):
        version, self.episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")

    def _stale(self):
        return next(
            item for item in self.episodes
            if item.logical_name == "stale-route-refresh-b"
        )

    def test_v3_reuses_exact_frozen_v1_workload(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(EVIDENCE_POLICIES, ("no_reacquire", "reacquire"))
        self.assertEqual(HORIZON, 4)

    def test_evidence_bank_does_not_read_future_events(self):
        episode = self._stale()
        turn_one = _evidence_bank(episode, through_turn=1)
        turn_two = _evidence_bank(episode, through_turn=2)

        self.assertIn(0, turn_one)
        self.assertNotIn(1, turn_one)
        self.assertIn(1, turn_two)
        self.assertEqual(turn_one[0]["stage_index"], 0)
        self.assertEqual(turn_two[1]["stage_index"], 1)

    def test_reacquisition_refreshes_observation_not_hidden_truth(self):
        episode = self._stale()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator.apply_events(1)
        simulator.apply_events(2)

        self.assertEqual(simulator.context["current_stage_index"], 0)
        self.assertEqual(simulator.context["current_weight_percent"], 10)
        self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 1)

        hidden_before = json.loads(json.dumps(simulator.context))
        self.assertTrue(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=2,
            )
        )
        self.assertEqual(simulator.context, hidden_before)
        self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 0)
        self.assertEqual(simulator.visible["stage_evidence"]["weight_percent"], 10)
        self.assertEqual(
            simulator.history[-1]["disposition"],
            "evidence_reacquired",
        )

    def test_reacquisition_refuses_snapshot_not_yet_available(self):
        episode = self._stale()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        # Move the hidden route to stage 1 without advancing the frozen
        # environment clock to the stage-1 telemetry event.
        simulator.context["current_stage_index"] = 1
        simulator.context["current_weight_percent"] = 50

        self.assertFalse(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=1,
            )
        )

    def test_reacquire_treatment_can_recover_stale_route_without_unsafe_action(self):
        class ScriptedModel:
            model_id = "scripted-evidence-recovery"

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

                # Preserve the v2 failure timing: do not act until turn 2,
                # when stage-1 telemetry is visible while the realized route
                # is still stage 0.
                if phase in {
                    "initial-shared",
                    "initial-repair",
                    "adaptive-1",
                    "adaptive-1-repair",
                    "adaptive-1-repair-post-hold",
                }:
                    action = {"kind": "wait"}
                elif phase == "adaptive-2":
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
                elif int(runtime["current_weight_percent"]) == 10:
                    action = {
                        "kind": "apply",
                        "experiment_id": runtime["experiment_id"],
                        "target_id": runtime["target_id"],
                        "control_release_id": runtime["control_release_id"],
                        "candidate_deployment_id": runtime["candidate_deployment_id"],
                        "stage_index": 1,
                        "candidate_weight_percent": 50,
                        "state_version": runtime["state_version"],
                        "operation_id": f"{episode_id}:{phase}:to-50",
                    }
                elif int(runtime["current_weight_percent"]) == 50:
                    action = {
                        "kind": "apply",
                        "experiment_id": runtime["experiment_id"],
                        "target_id": runtime["target_id"],
                        "control_release_id": runtime["control_release_id"],
                        "candidate_deployment_id": runtime["candidate_deployment_id"],
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "state_version": runtime["state_version"],
                        "operation_id": f"{episode_id}:{phase}:to-100",
                    }
                else:
                    action = {"kind": "wait"}

                return json.dumps({"actions": [action]}), {}, 0.01

        model = ScriptedModel()
        result = run_canary_evidence_recovery_study(
            model,
            (self._stale(),),
        )

        no_reacquire = next(
            row for row in result["episodes"]
            if row["evidence_policy"] == "no_reacquire"
        )
        reacquire = next(
            row for row in result["episodes"]
            if row["evidence_policy"] == "reacquire"
        )

        self.assertFalse(no_reacquire["delegable"])
        self.assertTrue(reacquire["delegable"])
        self.assertEqual(reacquire["metrics"]["unsafe_transitions"], 0)
        self.assertGreaterEqual(reacquire["evidence_reacquisitions"], 2)

        history = reacquire["history"]
        dispositions = [
            item.get("disposition") for item in history
        ]
        self.assertIn("deny", dispositions)
        self.assertIn("evidence_reacquired", dispositions)
        self.assertIn("verified", dispositions)

    def test_identical_prompts_share_physical_samples(self):
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
                return json.dumps({"actions": [{"kind": "wait"}]}), {}, 0.01

        model = CountingWaitModel()
        target = (next(
            item for item in self.episodes
            if item.study_group == "clean_progression"
        ),)
        result = run_canary_evidence_recovery_study(model, target)

        # One shared initial sample plus four shared adaptive samples. The two
        # policies are observationally identical here, so they must not be
        # independently sampled.
        self.assertEqual(model.calls, 5)
        self.assertEqual(result["physical_sampling"]["calls"], 5)
        for policy in EVIDENCE_POLICIES:
            self.assertEqual(
                result["cells"][policy]["logical_model_calls"],
                5,
            )

    def test_policy_names_are_not_model_visible(self):
        # There is no policy label in the prompt builder; only the evidence
        # state/history can diverge after the intervention.
        from baa_protocol.prospective_canary_feedback_study import (
            _adaptive_feedback_prompt,
        )

        episode = self._stale()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        prompt = _adaptive_feedback_prompt(
            episode,
            simulator,
            feedback_policy="corrective",
        )
        for policy in EVIDENCE_POLICIES:
            self.assertNotIn(policy, prompt)

    def test_stale_hold_reason_is_exactly_frozen(self):
        self.assertEqual(
            STALE_EVIDENCE_REASON,
            "stage evidence is stale or mismatched",
        )


if __name__ == "__main__":
    unittest.main()
