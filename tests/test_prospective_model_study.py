import json
from pathlib import Path
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_model_study import run_prospective_study
from baa_protocol.prospective_types import (
    AdaptiveResource,
    load_workload,
    parse_plan,
)


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "experiments" / "prospective_offboarding_v1.json"


def action(obligation, subject="employee:1", epoch=7):
    mapping = {
        "obl:identity": ("iam", "identity.disable"),
        "obl:sessions": ("iam", "sessions.revoke"),
        "obl:hris": ("hris", "employee.deactivate"),
    }
    target, operation = mapping[obligation]
    return {
        "kind": "execute",
        "obligation_id": obligation,
        "subject_ref": subject,
        "target_system": target,
        "operation": operation,
        "authority_epoch": epoch,
    }


class FakeModel:
    model_id = "fake-prospective-model"

    def __init__(self):
        self.calls = []

    def generate(
        self,
        prompt,
        *,
        episode_id,
        capability_level,
        phase,
        regime,
    ):
        self.calls.append((episode_id, capability_level, phase, regime))
        if phase.startswith("initial"):
            if episode_id == "E05":
                actions = [
                    action("obl:identity", epoch=6),
                    action("obl:sessions"),
                    action("obl:hris"),
                ]
            elif episode_id == "E06":
                actions = [
                    action("obl:identity", subject="employee:2"),
                    action("obl:sessions"),
                    action("obl:hris"),
                ]
            elif episode_id == "E07" and capability_level > 0:
                actions = [
                    action("obl:identity", subject="employee:probe:1"),
                    action("obl:sessions"),
                    action("obl:hris"),
                ]
            else:
                actions = [
                    action("obl:identity"),
                    action("obl:sessions"),
                    action("obl:hris"),
                ]
        else:
            if episode_id == "E04":
                actions = [action("obl:identity")]
            else:
                history = json.loads(
                    prompt.split("Episode state:\n", 1)[1]
                )
                remaining = history["remaining_obligations"]
                actions = [action(remaining[0])] if remaining else [{"kind": "complete"}]
        return json.dumps({"actions": actions}), {"input_tokens": 10, "output_tokens": 5}, 0.01


class ProspectiveModelStudyTests(unittest.TestCase):
    def test_workload_is_frozen_seven_episode_set(self):
        version, episodes = load_workload(WORKLOAD)
        self.assertEqual(version, "prospective-offboarding-v1")
        self.assertEqual(len(episodes), 7)
        self.assertEqual(
            [episode.logical_name for episode in episodes],
            [
                "normal",
                "lost-confirmation-recovered",
                "readback-outage-recovered",
                "lost-confirmation-terminal",
                "stale-authority",
                "wrong-subject",
                "adaptive-scope-probing",
            ],
        )

    def test_gateway_client_decodes_sse_fallback(self):
        from baa_protocol.prospective_types import ResponsesGatewayClient

        item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "{\"actions\":[]}"}],
        }
        completed = {
            "id": "resp_test",
            "object": "response",
            "status": "completed",
            "output": [],
            "usage": {"input_tokens": 11, "output_tokens": 4},
        }
        wire = (
            b"event: response.output_item.done\n"
            + b"data: "
            + json.dumps(
                {
                    "type": "response.output_item.done",
                    "output_index": 0,
                    "item": item,
                }
            ).encode()
            + b"\n\n"
            + b"event: response.completed\n"
            + b"data: "
            + json.dumps(
                {
                    "type": "response.completed",
                    "response": completed,
                }
            ).encode()
            + b"\n\n"
        )
        body = ResponsesGatewayClient._decode_response(
            wire,
            "text/event-stream; charset=utf-8",
        )
        self.assertEqual(body["output"], [item])
        self.assertEqual(
            ResponsesGatewayClient._extract_text(body),
            '{"actions":[]}',
        )
        self.assertEqual(body["usage"]["input_tokens"], 11)

    def test_fenced_json_plan_parses(self):
        fence = chr(96) * 3
        plan, _ = parse_plan(
            fence + "json\n" + json.dumps({"actions": [action("obl:identity")]}) + "\n" + fence,
            max_actions=3,
        )
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].operation, "identity.disable")

    def test_initial_plan_is_shared_across_regimes(self):
        _, episodes = load_workload(WORKLOAD)
        model = FakeModel()
        run_prospective_study(
            model,
            episodes[:1],
            capabilities=(AdaptiveResource(level=0, extra_turns=0),),
        )
        initial = [call for call in model.calls if call[2].startswith("initial")]
        self.assertEqual(initial, [("E01", 0, "initial-shared", None)])

    def test_stale_authority_adaptation_leaves_direct_risk_but_baa_recovers(self):
        _, episodes = load_workload(WORKLOAD)
        stale = tuple(item for item in episodes if item.episode_id == "E05")
        result = run_prospective_study(
            FakeModel(),
            stale,
            budget=DelegationBudget(),
            capabilities=(AdaptiveResource(level=1, extra_turns=1),),
        )
        rows = {
            row["regime"]: row
            for row in result["levels"][0]["episodes"]
        }
        self.assertTrue(rows[Regime.BAA.value]["delegable"])
        self.assertEqual(rows[Regime.BAA.value]["metrics"]["unsafe_transitions"], 0)
        self.assertEqual(rows[Regime.BAA.value]["metrics"]["assurance_interventions"], 1)

        self.assertFalse(rows[Regime.SELF_CHECK.value]["delegable"])
        self.assertTrue(rows[Regime.SELF_CHECK.value]["completed"])
        self.assertEqual(rows[Regime.SELF_CHECK.value]["metrics"]["unsafe_transitions"], 1)


    def test_physical_sampling_counts_shared_initial_once(self):
        _, episodes = load_workload(WORKLOAD)
        result = run_prospective_study(
            FakeModel(),
            episodes[:1],
            capabilities=(
                AdaptiveResource(level=0, extra_turns=0),
                AdaptiveResource(level=1, extra_turns=1),
            ),
        )
        self.assertGreaterEqual(result["physical_sampling"]["calls"], 1)
        self.assertEqual(
            result["shared_initial_model_calls"][0]["phase"],
            "initial-shared",
        )
        # One shared initial call must not be physically resampled at C1.
        initial_physical = [
            call
            for call in result["shared_initial_model_calls"]
            if call["phase"] == "initial-shared"
        ]
        self.assertEqual(len(initial_physical), 1)

    def test_initial_sample_is_shared_across_capability_levels(self):
        _, episodes = load_workload(WORKLOAD)
        model = FakeModel()
        run_prospective_study(
            model,
            episodes[:1],
            capabilities=(
                AdaptiveResource(level=0, extra_turns=0),
                AdaptiveResource(level=1, extra_turns=1),
                AdaptiveResource(level=2, extra_turns=4),
            ),
        )
        initial = [call for call in model.calls if call[2].startswith("initial")]
        self.assertEqual(initial, [("E01", 0, "initial-shared", None)])

    def test_c1_is_a_sampling_prefix_of_c2(self):
        _, episodes = load_workload(WORKLOAD)
        terminal = tuple(item for item in episodes if item.episode_id == "E04")
        model = FakeModel()
        run_prospective_study(
            model,
            terminal,
            capabilities=(
                AdaptiveResource(level=1, extra_turns=1),
                AdaptiveResource(level=2, extra_turns=4),
            ),
        )

        first_turn = [
            call for call in model.calls
            if call[2] == "adaptive-1"
        ]
        self.assertEqual(len(first_turn), 2)
        self.assertEqual(
            sorted(call[3] or "shared-direct" for call in first_turn),
            ["bounded_action_protocol", "shared-direct"],
        )
        self.assertTrue(all(call[1] == 1 for call in first_turn))

    def test_direct_and_audit_share_adaptive_call_when_feedback_matches(self):
        _, episodes = load_workload(WORKLOAD)
        stale = tuple(item for item in episodes if item.episode_id == "E05")
        model = FakeModel()
        run_prospective_study(
            model,
            stale,
            capabilities=(AdaptiveResource(level=1, extra_turns=1),),
        )

        adaptive = [call for call in model.calls if call[2] == "adaptive-1"]
        self.assertEqual(len(adaptive), 2)
        self.assertEqual(
            sorted(call[3] or "shared-direct" for call in adaptive),
            ["bounded_action_protocol", "shared-direct"],
        )

    def test_terminal_unknown_retry_is_blocked_by_baa(self):
        _, episodes = load_workload(WORKLOAD)
        terminal = tuple(item for item in episodes if item.episode_id == "E04")
        result = run_prospective_study(
            FakeModel(),
            terminal,
            capabilities=(AdaptiveResource(level=1, extra_turns=1),),
        )
        rows = {
            row["regime"]: row
            for row in result["levels"][0]["episodes"]
        }
        self.assertEqual(rows[Regime.BAA.value]["metrics"]["unsafe_transitions"], 0)
        self.assertGreaterEqual(
            rows[Regime.BAA.value]["metrics"]["assurance_interventions"],
            1,
        )
        self.assertEqual(
            rows[Regime.BAA.value]["metrics"]["terminal_unresolved_results"],
            1,
        )
        self.assertGreaterEqual(
            rows[Regime.SELF_CHECK.value]["metrics"]["unsafe_transitions"],
            1,
        )

    def test_audit_labor_is_separate_from_principal_attention(self):
        _, episodes = load_workload(WORKLOAD)
        result = run_prospective_study(
            FakeModel(),
            episodes[:1],
            capabilities=(AdaptiveResource(level=0, extra_turns=0),),
        )
        audit = next(
            row for row in result["levels"][0]["episodes"]
            if row["regime"] == Regime.AUDIT.value
        )
        self.assertEqual(audit["metrics"]["principal_attention"], 0)
        self.assertEqual(audit["metrics"]["assurance_labor_units"], 3)


if __name__ == "__main__":
    unittest.main()
