import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.prospective_canary_evidence_recovery_study import (
    EVIDENCE_POLICIES,
    HORIZONS,
    EvidenceAction,
    EvidenceRecoverySimulator,
    _adaptive_prompt,
    evidence_model_client,
    evidence_recovery_schema,
    run_canary_evidence_recovery_study,
)
from baa_protocol.prospective_canary_study import load_canary_workload


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_canary_v1.json"


class CanaryEvidenceRecoveryStudyTests(unittest.TestCase):
    def setUp(self):
        version, episodes = load_canary_workload(WORKLOAD)
        self.assertEqual(version, "prospective-canary-v1")
        self.episodes = episodes

    def stale_episode(self):
        return next(
            item
            for item in self.episodes
            if item.logical_name == "stale-route-refresh-b"
        )

    def refresh_action(self, simulator, suffix="refresh"):
        c = simulator.base.context
        return EvidenceAction(
            kind="refresh_evidence",
            experiment_id=c["experiment_id"],
            target_id=c["target_id"],
            control_release_id=c["control_release_id"],
            candidate_deployment_id=c["candidate_deployment_id"],
            state_version=c["state_version"],
            operation_id=f"{c['experiment_id']}:{suffix}",
        )

    def test_v3_reuses_frozen_v1_workload(self):
        self.assertEqual(len(self.episodes), 18)
        self.assertEqual(
            sorted({item.study_group for item in self.episodes}),
            [
                "clean_progression",
                "evidence_maturation",
                "guardrail_recovery",
                "irrecoverable_control",
                "lost_ack_recovery",
                "stale_route_refresh",
            ],
        )

    def test_refresh_function_cannot_select_stage_or_weight(self):
        schema = evidence_recovery_schema()
        variants = schema["properties"]["actions"]["items"]["anyOf"]
        refresh = next(
            item
            for item in variants
            if item["properties"]["kind"].get("enum") == ["refresh_evidence"]
        )
        self.assertNotIn("stage_index", refresh["properties"])
        self.assertNotIn("candidate_weight_percent", refresh["properties"])

        client = evidence_model_client()
        payload = client._request_payload("hello")
        self.assertEqual(
            payload["tool_choice"],
            {
                "type": "function",
                "name": "submit_canary_evidence_proposal",
            },
        )
        self.assertTrue(payload["tools"][0]["strict"])

    def test_versioned_refresh_recovers_current_route_evidence_without_changing_route(self):
        episode = self.stale_episode()
        latest = EvidenceRecoverySimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="latest_only",
        )
        versioned = EvidenceRecoverySimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="versioned_current_stage",
        )

        for simulator in (latest, versioned):
            simulator.apply_events(1)
            self.assertEqual(
                simulator.base.visible["stage_evidence"]["stage_index"],
                0,
            )
            simulator.apply_events(2)
            self.assertEqual(
                simulator.base.visible["stage_evidence"]["stage_index"],
                1,
            )
            self.assertEqual(simulator.base.context["current_stage_index"], 0)
            self.assertEqual(simulator.base.context["current_weight_percent"], 10)

        self.assertEqual(
            latest.execute(self.refresh_action(latest, "latest")),
            "hold",
        )
        self.assertEqual(
            latest.base.visible["stage_evidence"]["stage_index"],
            1,
        )
        self.assertEqual(latest.base.context["current_stage_index"], 0)

        self.assertEqual(
            versioned.execute(self.refresh_action(versioned, "versioned")),
            "refreshed",
        )
        self.assertEqual(
            versioned.base.visible["stage_evidence"]["stage_index"],
            0,
        )
        self.assertEqual(
            versioned.base.visible["stage_evidence"]["weight_percent"],
            10,
        )
        self.assertEqual(versioned.base.context["current_stage_index"], 0)
        self.assertEqual(versioned.base.context["current_weight_percent"], 10)

    def test_refresh_scope_mismatch_is_denied(self):
        episode = self.stale_episode()
        simulator = EvidenceRecoverySimulator(
            episode,
            DelegationBudget(min_useful_delivery=1),
            evidence_policy="versioned_current_stage",
        )
        action = self.refresh_action(simulator)
        action = EvidenceAction(
            **{
                **action.__dict__,
                "target_id": "target:wrong",
            }
        )
        self.assertEqual(simulator.execute(action), "deny")
        self.assertEqual(simulator.evidence_refresh_successes, 0)

    def test_policy_name_is_not_model_visible(self):
        episode = self.stale_episode()
        for policy in EVIDENCE_POLICIES:
            simulator = EvidenceRecoverySimulator(
                episode,
                DelegationBudget(min_useful_delivery=1),
                evidence_policy=policy,
            )
            prompt = _adaptive_prompt(episode, simulator)
            self.assertNotIn(policy, prompt)
            self.assertNotIn("latest_only", prompt)
            self.assertNotIn("versioned_current_stage", prompt)

    def test_scripted_model_recovers_only_with_versioned_current_stage(self):
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
                marker = (
                    "Episode state:\n"
                    if "Episode state:\n" in prompt
                    else "Episode:\n"
                )
                value = json.loads(prompt.split(marker, 1)[1])
                if marker == "Episode:\n":
                    runtime = value["evidence"]["runtime_state"]
                    action = {"kind": "wait"}
                    return json.dumps({"actions": [action]}), {}, 0.01

                runtime = value["runtime_state"]
                feedback = value.get("assurance_feedback") or {}
                safe = feedback.get("safe_next_action")
                ids = {
                    "experiment_id": runtime["experiment_id"],
                    "target_id": runtime["target_id"],
                    "control_release_id": runtime["control_release_id"],
                    "candidate_deployment_id": runtime["candidate_deployment_id"],
                    "state_version": runtime["state_version"],
                }

                if isinstance(safe, dict):
                    kind = safe.get("kind")
                    if kind == "refresh_evidence":
                        action = {
                            "kind": "refresh_evidence",
                            **ids,
                            "operation_id": f"{episode_id}:{phase}:refresh",
                        }
                        return json.dumps({"actions": [action]}), {}, 0.01
                    if kind == "apply":
                        action = {
                            "kind": "apply",
                            **ids,
                            "stage_index": safe["stage_index"],
                            "candidate_weight_percent": safe[
                                "candidate_weight_percent"
                            ],
                            "operation_id": f"{episode_id}:{phase}:corrected",
                        }
                        return json.dumps({"actions": [action]}), {}, 0.01
                    if kind == "restore":
                        action = {
                            "kind": "restore",
                            **ids,
                            "operation_id": f"{episode_id}:{phase}:restore",
                        }
                        return json.dumps({"actions": [action]}), {}, 0.01

                current_stage = int(runtime["current_stage_index"])
                current_weight = int(runtime["current_weight_percent"])
                evidence = runtime.get("stage_evidence")
                evidence_matches = (
                    isinstance(evidence, dict)
                    and int(evidence.get("stage_index", -1)) == current_stage
                    and int(evidence.get("weight_percent", -1)) == current_weight
                )

                if phase == "adaptive-1":
                    action = {"kind": "wait"}
                elif current_weight == 10 and phase.startswith("adaptive-2"):
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 2,
                        "candidate_weight_percent": 100,
                        "operation_id": f"{episode_id}:{phase}:skip",
                    }
                elif not evidence_matches:
                    action = {
                        "kind": "refresh_evidence",
                        **ids,
                        "operation_id": f"{episode_id}:{phase}:refresh",
                    }
                elif current_weight == 10:
                    action = {
                        "kind": "apply",
                        **ids,
                        "stage_index": 1,
                        "candidate_weight_percent": 50,
                        "operation_id": f"{episode_id}:{phase}:to-50",
                    }
                elif current_weight == 50:
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

        result = run_canary_evidence_recovery_study(
            ScriptedModel(),
            (self.stale_episode(),),
            horizons=(4, 8),
        )

        latest = result["cells"]["latest_only"]["8"]["stale_route"]
        versioned = result["cells"]["versioned_current_stage"]["8"]["stale_route"]

        self.assertEqual(latest["delegable_episodes"], 0)
        self.assertEqual(latest["evidence_refresh_successes"], 0)
        self.assertEqual(versioned["delegable_episodes"], 1)
        self.assertGreaterEqual(versioned["evidence_refresh_successes"], 1)
        self.assertEqual(versioned["unsafe_transitions"], 0)

    def test_frozen_horizons(self):
        self.assertEqual(HORIZONS, (4, 8, 12))


if __name__ == "__main__":
    unittest.main()
