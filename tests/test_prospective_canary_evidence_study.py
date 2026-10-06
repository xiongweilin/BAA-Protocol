import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_canary_evidence_study import (
    EVIDENCE_POLICIES,
    HORIZONS,
    STALE_EVIDENCE_REASON,
    _observer_templates,
    _reacquire_current_stage_evidence,
    run_canary_evidence_study,
)
from baa_protocol.prospective_canary_feedback_study import (
    _adaptive_feedback_prompt,
)
from baa_protocol.prospective_canary_study import (
    CanarySimulator,
    load_canary_workload,
)


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryEvidenceStudyTests(unittest.TestCase):
    def setUp(self):
        version, self.episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")

    def stale_episode(self):
        return next(
            episode
            for episode in self.episodes
            if episode.logical_name == "stale-route-refresh-b"
        )

    def test_v3_reuses_frozen_v1_workload_and_h4(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(
            EVIDENCE_POLICIES,
            ("no_reacquire", "reacquire"),
        )
        self.assertEqual(HORIZONS, (4,))

    def test_observer_templates_come_only_from_frozen_runtime_events(self):
        episode = self.stale_episode()
        state_version = episode.control_context["state_version"]
        self.assertEqual(
            _observer_templates(episode, through_turn=0),
            {},
        )
        turn1 = _observer_templates(episode, through_turn=1)
        self.assertEqual(
            set(turn1),
            {
                (episode.control_context["experiment_id"], 0, 10, state_version),
                (episode.control_context["experiment_id"], 2, 100, state_version),
            },
        )
        turn2 = _observer_templates(episode, through_turn=2)
        self.assertEqual(
            set(turn2),
            {
                (episode.control_context["experiment_id"], 0, 10, state_version),
                (episode.control_context["experiment_id"], 1, 50, state_version),
                (episode.control_context["experiment_id"], 2, 100, state_version),
            },
        )

        clean = next(
            episode
            for episode in self.episodes
            if episode.study_group == "clean_progression"
        )
        self.assertEqual(
            _observer_templates(clean, through_turn=4),
            {},
        )

    def test_reacquisition_changes_observation_not_hidden_truth(self):
        episode = self.stale_episode()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator.apply_events(1)
        simulator.apply_events(2)

        self.assertEqual(
            (
                simulator.context["current_stage_index"],
                simulator.context["current_weight_percent"],
            ),
            (0, 10),
        )
        self.assertEqual(
            simulator.visible["stage_evidence"]["stage_index"],
            1,
        )

        hidden_before = json.loads(json.dumps(simulator.context))
        self.assertTrue(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=2,
            )
        )
        self.assertEqual(simulator.context, hidden_before)
        self.assertEqual(
            simulator.visible["stage_evidence"]["stage_index"],
            0,
        )
        self.assertEqual(
            simulator.visible["stage_evidence"]["weight_percent"],
            10,
        )
        self.assertEqual(
            simulator.history[-1]["disposition"],
            "evidence_reacquired",
        )

    def test_reacquisition_refuses_route_visibility_mismatch(self):
        episode = self.stale_episode()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        # Initial public route is intentionally stale relative to hidden
        # realized route in this stratum.
        self.assertNotEqual(
            (
                simulator.visible["current_stage_index"],
                simulator.visible["current_weight_percent"],
            ),
            (
                simulator.context["current_stage_index"],
                simulator.context["current_weight_percent"],
            ),
        )
        self.assertFalse(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=0,
            )
        )


    def test_reacquisition_cannot_use_future_stage_template(self):
        episode = self.stale_episode()
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator.apply_events(1)
        simulator.visible["current_stage_index"] = 1
        simulator.visible["current_weight_percent"] = 50
        simulator.context["current_stage_index"] = 1
        simulator.context["current_weight_percent"] = 50

        self.assertFalse(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=1,
            )
        )
        self.assertTrue(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=2,
            )
        )
        self.assertEqual(
            simulator.history[-1]["state_version"],
            episode.control_context["state_version"],
        )

    def test_scripted_reacquisition_recovers_sequential_completion(self):
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

                if phase in {"initial-shared", "adaptive-1"}:
                    action = {"kind": "wait"}
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
                elif phase == "adaptive-2":
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:skip",
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

                return (
                    json.dumps({"actions": [action]}),
                    {},
                    0.01,
                )

        result = run_canary_evidence_study(
            ScriptedModel(),
            (self.stale_episode(),),
        )

        no_reacquire = next(
            row
            for row in result["episodes"]
            if row["evidence_policy"] == "no_reacquire"
        )
        reacquire = next(
            row
            for row in result["episodes"]
            if row["evidence_policy"] == "reacquire"
        )

        self.assertFalse(no_reacquire["delegable"])
        self.assertTrue(reacquire["delegable"])
        self.assertEqual(
            reacquire["metrics"]["unsafe_transitions"],
            0,
        )
        self.assertGreaterEqual(
            reacquire["evidence_reacquisitions"],
            2,
        )

        dispositions = [
            item.get("disposition")
            for item in reacquire["history"]
        ]
        self.assertIn("deny", dispositions)
        self.assertIn("hold", dispositions)
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
                return (
                    json.dumps(
                        {"actions": [{"kind": "wait"}]}
                    ),
                    {},
                    0.0,
                )

        clean = (
            next(
                episode
                for episode in self.episodes
                if episode.study_group == "clean_progression"
            ),
        )
        model = CountingWaitModel()
        result = run_canary_evidence_study(
            model,
            clean,
        )

        self.assertEqual(model.calls, 5)
        self.assertEqual(
            result["physical_sampling"]["calls"],
            5,
        )
        for policy in EVIDENCE_POLICIES:
            self.assertEqual(
                result["cells"][policy][
                    "logical_model_calls"
                ],
                5,
            )

    def test_treatment_names_are_not_model_visible(self):
        episode = self.stale_episode()
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

    def test_stale_hold_reason_is_exact(self):
        self.assertEqual(
            STALE_EVIDENCE_REASON,
            "stage evidence is stale or mismatched",
        )


if __name__ == "__main__":
    unittest.main()
