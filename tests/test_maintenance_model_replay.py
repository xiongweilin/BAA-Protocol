"""P2 archived maintenance replay: immutable evidence, privacy and regime checks."""
import json
from pathlib import Path
import unittest

from baa_protocol.experiment import Regime
from baa_protocol.maintenance_model_replay import (
    HORIZONS,
    REGIMES,
    admissible_disposition,
    decision_tool_schema,
    load_maintenance_windows,
    maintenance_prompt,
    parse_maintenance_decision,
    replay_regime,
    run_maintenance_model_replay,
)

WORKLOAD = (
    Path(__file__).resolve().parents[1]
    / "experiments/p2_readonly_maintenance_replay_v1.json"
)


class UniformModel:
    model_id = "offline-fake-model"
    interface_mode = "function_tool"

    def __init__(self, disposition="verified_stable"):
        self.disposition = disposition
        self.calls = []

    def generate(self, prompt, *, episode_id, capability_level, phase, regime):
        self.calls.append({
            "prompt": prompt,
            "episode_id": episode_id,
            "capability_level": capability_level,
            "phase": phase,
            "regime": regime,
        })
        return json.dumps({"decision": self.disposition}), {
            "input_tokens": 8, "output_tokens": 3
        }, 0.005


class MaintenanceModelReplayTests(unittest.TestCase):
    def setUp(self):
        self.windows = load_maintenance_windows(WORKLOAD)

    def test_frozen_evidence_four_cases_and_provenance(self):
        self.assertEqual([x.episode_id for x in self.windows], ["M01", "M02", "M03", "M04"])
        self.assertEqual(len({x.archive_sha256 for x in self.windows}), 2)
        self.assertEqual(len({x.artifact_id for x in self.windows}), 2)
        self.assertEqual([x.expected_final for x in self.windows], [
            "verified_stable", "verified_recovered_evidence",
            "escalate_contract_or_authority", "verified_recovered_evidence",
        ])

    def test_real_pause_vs_observer_gap_is_indistinguishable_to_planner(self):
        a, b = self.windows[1], self.windows[3]
        self.assertNotEqual(a.hidden_cause, b.hidden_cause)
        self.assertNotEqual(a.artifact_id, b.artifact_id)
        for horizon in HORIZONS:
            self.assertEqual(maintenance_prompt(a, horizon), maintenance_prompt(b, horizon))
            self.assertNotIn(a.hidden_cause, maintenance_prompt(a, horizon))
            self.assertNotIn(b.hidden_cause, maintenance_prompt(b, horizon))
        for w in self.windows:
            for h in HORIZONS:
                p = maintenance_prompt(w, h)
                self.assertNotIn(str(w.artifact_id), p)
                self.assertNotIn(w.archive_sha256, p)
                self.assertNotIn(w.expected_final, p)

    def test_external_gate_cannot_use_future_samples(self):
        for horizon in (2, 3):
            prefix = self.windows[1].observations[:horizon]
            self.assertFalse(admissible_disposition(prefix, "verified_recovered_evidence"))
            self.assertFalse(admissible_disposition(prefix, "verified_stable"))
            self.assertTrue(admissible_disposition(prefix, "unresolved_observation"))
        self.assertTrue(admissible_disposition(
            self.windows[1].observations, "verified_recovered_evidence"
        ))
        self.assertTrue(admissible_disposition(
            self.windows[3].observations, "verified_recovered_evidence"
        ))

    def test_sticky_contract_escalation_cannot_be_self_certified_recovered(self):
        for h in HORIZONS:
            prefix = self.windows[2].observations[:h]
            self.assertTrue(admissible_disposition(prefix, "escalate_contract_or_authority"))
            self.assertFalse(admissible_disposition(prefix, "verified_stable"))
            self.assertFalse(admissible_disposition(prefix, "verified_recovered_evidence"))

    def test_architectural_gate_blocks_unsafe_publication_but_charges_hold(self):
        a = self.windows[1]
        self_check = replay_regime(a, 2, "verified_stable", Regime.SELF_CHECK)
        audit = replay_regime(a, 2, "verified_stable", Regime.AUDIT)
        baa = replay_regime(a, 2, "verified_stable", Regime.BAA)
        self.assertTrue(self_check["published"])
        self.assertEqual(self_check["wrong_published_disposition"], 1)
        self.assertEqual(self_check["unsupported_published_certificate"], 1)
        self.assertTrue(audit["published"])
        self.assertEqual(audit["simulated_posthoc_audit_labor"], 1)
        self.assertEqual(audit["attention_demand_proxy"], 1)
        self.assertFalse(baa["published"])
        self.assertEqual(baa["held_by_external_gate"], 1)
        self.assertEqual(baa["terminal_unresolved"], 1)
        self.assertEqual(baa["attention_demand_proxy"], 1)
        self.assertEqual(baa["automated_gate_interventions"], 1)

    def test_verified_recovery_delivers_only_after_two_clean_rounds(self):
        a = self.windows[3]
        self.assertEqual(replay_regime(
            a, 3, "verified_recovered_evidence", Regime.SELF_CHECK
        )["useful_diagnostic_delivery"], 0)
        self.assertEqual(replay_regime(
            a, 4, "verified_recovered_evidence", Regime.BAA
        )["useful_diagnostic_delivery"], 1)

    def test_unresolved_has_no_useful_delivery_and_costs_attention_proxy(self):
        for regime in REGIMES:
            outcome = replay_regime(self.windows[0], 4, "unresolved_observation", regime)
            self.assertEqual(outcome["useful_diagnostic_delivery"], 0)
            self.assertEqual(outcome["terminal_unresolved"], 1)
            self.assertEqual(outcome["attention_demand_proxy"], 1)
            self.assertEqual(outcome["actual_business_effects"], 0)

    def test_forced_schema_and_parser_are_restrictive(self):
        schema = decision_tool_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["required"], ["decision"])
        self.assertEqual(parse_maintenance_decision(
            '{"decision":"verified_stable"}'
        ), "verified_stable")
        for bad in (
            '{"decision":"repair_keycloak"}',
            '{"decision":"verified_stable","hidden":"override"}',
            '{"decision":4}', '{"decision":null}', '{"actions":[]}',
            "not a tool response",
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_maintenance_decision(bad)

    def test_single_model_sample_shared_across_all_three_regimes(self):
        client = UniformModel("verified_stable")
        result = run_maintenance_model_replay(client, self.windows)
        self.assertEqual(result["physical_model_samples"], 12)
        self.assertEqual(result["replayed_regime_rows"], 36)
        self.assertEqual(len(client.calls), 12)
        self.assertTrue(all(c["regime"] is None for c in client.calls))
        self.assertEqual([x["episodes"] for x in result["summary"]], [4] * 9)
        self.assertEqual(result["physical_sampling"]["model_input_tokens"], 96)
        self.assertEqual(result["physical_sampling"]["model_output_tokens"], 36)
        self.assertFalse(result["eligible_for_P2_causal_delegation_claim"])
        self.assertFalse(result["real_principal_attention_measured"])
        self.assertFalse(result["real_assurance_cost_measured"])
        self.assertEqual(result["nonidentifiable_cause_pair"], ["M02", "M04"])
        self.assertEqual(len({(r["episode_id"],r["horizon_rounds"],r["regime"]) for r in result["regime_rows"]}),36)

    def test_different_model_outputs_different_regime_scores_without_resampling(self):
        result = run_maintenance_model_replay(
            UniformModel("verified_recovered_evidence"), self.windows
        )
        c0_baa = next(r for r in result["summary"] if r["horizon_rounds"] == 2 and r["regime"] == Regime.BAA.value)
        self.assertEqual(c0_baa["useful_diagnostic_delivery"], 0)
        self.assertEqual(c0_baa["terminal_unresolved"], 4)
        c4_baa = next(r for r in result["summary"] if r["horizon_rounds"] == 4 and r["regime"] == Regime.BAA.value)
        self.assertEqual(c4_baa["useful_diagnostic_delivery"], 2)

    def test_bad_model_output_is_not_retried_as_a_success(self):
        class Invalid(UniformModel):
            def generate(self, *args, **kwargs):
                self.calls.append(kwargs)
                return '{"decision":"forged"}', {}, 0.1
        client = Invalid()
        with self.assertRaises(ValueError):
            run_maintenance_model_replay(client, self.windows)
        self.assertEqual(len(client.calls), 1)

    def test_altered_archived_truth_or_pair_is_rejected(self):
        data = json.loads(WORKLOAD.read_text())
        data["episodes"][3]["observations"][1]["keycloak_realm"] = "ok"
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            file = Path(tmp) / "workload.json"
            file.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                load_maintenance_windows(file)


if __name__ == "__main__":
    unittest.main()
