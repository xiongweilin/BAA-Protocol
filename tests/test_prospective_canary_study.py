import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_canary_study import (
    CanaryAction,
    CanarySimulator,
    canary_model_client,
    canary_proposal_schema,
    load_canary_workload,
    run_canary_study,
)
from baa_protocol.prospective_types import AdaptiveResource, ResponsesGatewayClient


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class ProspectiveCanaryStudyTests(unittest.TestCase):
    def test_workload_is_frozen_18_episode_six_strata(self):
        version, episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")
        self.assertEqual(len(episodes), 18)
        counts = {}
        for episode in episodes:
            counts[episode.study_group] = counts.get(episode.study_group, 0) + 1
        self.assertEqual(
            counts,
            {
                "clean_progression": 3,
                "evidence_maturation": 3,
                "guardrail_recovery": 3,
                "lost_ack_recovery": 3,
                "stale_route_refresh": 3,
                "irrecoverable_control": 3,
            },
        )
        self.assertEqual(len({episode.episode_id for episode in episodes}), 18)

    def test_canary_tool_uses_distinct_forced_function_schema(self):
        client = canary_model_client()
        payload = client._request_payload("hello")
        self.assertEqual(client.interface_mode, "function_tool")
        self.assertEqual(
            payload["tool_choice"],
            {"type": "function", "name": "submit_canary_proposal"},
        )
        self.assertFalse(payload["parallel_tool_calls"])
        self.assertEqual(payload["tools"][0]["name"], "submit_canary_proposal")
        self.assertEqual(payload["tools"][0]["parameters"], canary_proposal_schema())
        self.assertTrue(payload["tools"][0]["strict"])

    def test_generalized_gateway_preserves_offboarding_default_tool(self):
        client = ResponsesGatewayClient(proposal_tool=True)
        payload = client._request_payload("hello")
        self.assertEqual(
            payload["tool_choice"],
            {"type": "function", "name": "submit_baa_proposal"},
        )

    def test_evidence_maturation_does_not_change_hidden_route(self):
        _, episodes = load_canary_workload(WORKLOAD)
        episode = next(item for item in episodes if item.study_group == "evidence_maturation")
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        before = (
            simulator.context["current_stage_index"],
            simulator.context["current_weight_percent"],
        )
        simulator.apply_events(1)
        after = (
            simulator.context["current_stage_index"],
            simulator.context["current_weight_percent"],
        )
        self.assertEqual(before, after)
        self.assertGreaterEqual(
            simulator.visible["stage_evidence"]["observed_duration_seconds"],
            60,
        )

    def test_stale_route_refresh_follows_realized_hidden_route(self):
        _, episodes = load_canary_workload(WORKLOAD)
        episode = next(item for item in episodes if item.study_group == "stale_route_refresh")
        simulator = CanarySimulator(
            episode,
            Regime.SELF_CHECK,
            DelegationBudget(min_useful_delivery=1),
        )
        action = CanaryAction(
            kind="apply",
            experiment_id=simulator.context["experiment_id"],
            target_id=simulator.context["target_id"],
            control_release_id=simulator.context["control_release_id"],
            candidate_deployment_id=simulator.context["candidate_deployment_id"],
            stage_index=2,
            candidate_weight_percent=100,
            state_version=simulator.context["state_version"],
            operation_id="unsafe:skip-to-100",
        )
        self.assertEqual(simulator.execute(action), "verified")
        self.assertEqual(simulator.context["current_weight_percent"], 100)
        self.assertGreater(simulator.metrics.unsafe_transitions, 0)

        simulator.apply_events(1)

        self.assertEqual(simulator.visible["current_stage_index"], 2)
        self.assertEqual(simulator.visible["current_weight_percent"], 100)
        self.assertEqual(
            simulator.visible["stage_evidence"]["stage_index"],
            2,
        )

    def test_lost_ack_is_unresolved_until_scheduled_readback(self):
        _, episodes = load_canary_workload(WORKLOAD)
        episode = next(item for item in episodes if item.study_group == "lost_ack_recovery")
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        action = CanaryAction(
            kind="apply",
            experiment_id=simulator.context["experiment_id"],
            target_id=simulator.context["target_id"],
            control_release_id=simulator.context["control_release_id"],
            candidate_deployment_id=simulator.context["candidate_deployment_id"],
            stage_index=0,
            candidate_weight_percent=10,
            state_version=simulator.context["state_version"],
            operation_id="apply:first",
        )
        self.assertEqual(simulator.execute(action), "unknown")
        self.assertIsNotNone(simulator.pending)

        simulator.apply_events(1)
        self.assertIsNotNone(simulator.pending)

        replay = CanaryAction(
            **{**action.__dict__, "operation_id": "apply:retry"}
        )
        self.assertEqual(simulator.execute(replay), "hold")
        self.assertEqual(simulator.metrics.unsafe_transitions, 0)

        simulator.apply_events(2)
        self.assertIsNone(simulator.pending)
        self.assertEqual(simulator.metrics.useful_delivery, 1)

    def test_unsafe_direct_goal_does_not_count_as_useful_delivery(self):
        _, episodes = load_canary_workload(WORKLOAD)
        episode = next(item for item in episodes if item.study_group == "stale_route_refresh")
        simulator = CanarySimulator(
            episode,
            Regime.SELF_CHECK,
            DelegationBudget(min_useful_delivery=1),
        )
        action = CanaryAction(
            kind="apply",
            experiment_id=simulator.context["experiment_id"],
            target_id=simulator.context["target_id"],
            control_release_id=simulator.context["control_release_id"],
            candidate_deployment_id=simulator.context["candidate_deployment_id"],
            stage_index=2,
            candidate_weight_percent=100,
            state_version=simulator.context["state_version"],
            operation_id="unsafe:goal",
        )
        simulator.execute(action)
        result = simulator.finalize(
            capability_level=0,
            model_calls=1,
            input_tokens=0,
            output_tokens=0,
        )
        self.assertTrue(result.completed)
        self.assertEqual(result.metrics.unsafe_transitions, 1)
        self.assertEqual(result.metrics.useful_delivery, 0)
        self.assertFalse(result.delegable)

    def test_stale_route_fixture_can_create_baa_only_c2_delegation(self):
        class ScriptedModel:
            model_id = "scripted-canary"

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
                state = json.loads(prompt.split(marker, 1)[1])
                if marker == "Episode:\n":
                    runtime = state["evidence"]["runtime_state"]
                else:
                    runtime = state["runtime_state"]

                current_weight = int(runtime["current_weight_percent"])
                current_stage = int(runtime["current_stage_index"])
                ids = {
                    "experiment_id": runtime["experiment_id"],
                    "target_id": runtime["target_id"],
                    "control_release_id": runtime["control_release_id"],
                    "candidate_deployment_id": runtime["candidate_deployment_id"],
                    "state_version": runtime["state_version"],
                }
                if current_weight == 50:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:to-100",
                    }
                elif current_weight == 10:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 1,
                        "candidate_weight_percent": 50,
                        "operation_id": f"{episode_id}:to-50",
                    }
                elif current_weight == 100:
                    action = {"kind": "complete"}
                else:
                    action = {"kind": "wait"}
                return json.dumps({"actions": [action]}), {}, 0.01

        _, episodes = load_canary_workload(WORKLOAD)
        target = tuple(
            item for item in episodes if item.study_group == "stale_route_refresh"
        )[:1]
        result = run_canary_study(
            ScriptedModel(),
            target,
            capabilities=(AdaptiveResource(level=2, extra_turns=4),),
        )
        rows = {
            row["regime"]: row
            for row in result["levels"][0]["episodes"]
        }

        self.assertTrue(rows[Regime.BAA.value]["delegable"])
        self.assertEqual(rows[Regime.BAA.value]["metrics"]["unsafe_transitions"], 0)
        self.assertGreaterEqual(
            rows[Regime.BAA.value]["metrics"]["assurance_interventions"],
            1,
        )
        self.assertFalse(rows[Regime.SELF_CHECK.value]["delegable"])
        self.assertGreater(
            rows[Regime.SELF_CHECK.value]["metrics"]["unsafe_transitions"],
            0,
        )

    def test_canary_prompts_do_not_receive_regime_name(self):
        from baa_protocol.prospective_canary_study import _adaptive_prompt

        _, episodes = load_canary_workload(WORKLOAD)
        episode = episodes[0]
        prompt = _adaptive_prompt(
            episode,
            [{"phase": "admission", "disposition": "hold"}],
            episode.public_context["runtime_state"],
        )
        self.assertNotIn("bounded_action_protocol", prompt)
        self.assertNotIn("external_record_audit", prompt)
        self.assertNotIn("self_check", prompt)


if __name__ == "__main__":
    unittest.main()
