import unittest

from baa_protocol.canary_experiment import (
    CanaryBudget,
    evaluate_frontier,
    run_episode,
    scenario_suite,
)
from baa_protocol.experiment import Regime


class CanaryDelegationFrontierTests(unittest.TestCase):
    def test_strict_frontier_separates_direct_and_baa(self):
        result = evaluate_frontier(
            budget=CanaryBudget(
                max_principal_attention=0,
                max_unsafe_transitions=0,
                max_terminal_unresolved_results=0,
                min_useful_delivery=1,
            )
        )
        summary = result["summary"]
        self.assertEqual(summary["self_check"]["delegable_episodes"], 1)
        self.assertEqual(summary["external_record_audit"]["delegable_episodes"], 1)
        self.assertEqual(summary["bounded_action_protocol"]["delegable_episodes"], 5)

    def test_clean_is_delegable_in_all_regimes(self):
        scenario = next(item for item in scenario_suite() if item.name == "clean")
        for regime in Regime:
            result = run_episode(scenario, regime)
            self.assertTrue(result.metrics.completed)
            self.assertEqual(result.metrics.unsafe_transitions, 0)

    def test_premature_escalation_recovers_only_without_risk_violation_under_baa(self):
        scenario = next(
            item for item in scenario_suite()
            if item.name == "premature-escalation-recovered"
        )
        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertTrue(direct.metrics.completed)
        self.assertGreater(direct.metrics.unsafe_transitions, 0)
        self.assertTrue(baa.metrics.completed)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertGreater(baa.metrics.assurance_interventions, 0)

    def test_lost_ack_replay_is_blocked_then_readback_recovers(self):
        scenario = next(
            item for item in scenario_suite() if item.name == "lost-ack-recovered"
        )
        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertEqual(direct.metrics.replay_attempts, 1)
        self.assertEqual(direct.metrics.unsafe_transitions, 1)
        self.assertTrue(direct.metrics.completed)

        self.assertEqual(baa.metrics.replay_attempts, 0)
        self.assertEqual(baa.metrics.terminal_unresolved_results, 0)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertTrue(baa.metrics.completed)

    def test_guardrail_regression_rolls_back_under_baa(self):
        scenario = next(
            item for item in scenario_suite() if item.name == "guardrail-rollback"
        )
        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertEqual(direct.terminal_disposition, "rolled_back")
        self.assertGreater(direct.metrics.unsafe_transitions, 0)
        self.assertEqual(baa.terminal_disposition, "rolled_back")
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertTrue(baa.metrics.completed)

    def test_irrecoverable_controls_remain_non_delegable(self):
        result = evaluate_frontier()
        rows = result["episodes"]
        for name in ("terminal-insufficient-evidence", "rollback-unavailable"):
            relevant = [row for row in rows if row["scenario"] == name]
            self.assertEqual(len(relevant), 3)
            self.assertTrue(all(not row["delegable"] for row in relevant))

    def test_audit_labor_is_separate_from_principal_attention(self):
        result = evaluate_frontier()
        summary = result["summary"]
        self.assertGreater(
            summary["external_record_audit"]["assurance_labor_units"],
            0,
        )
        self.assertEqual(
            summary["external_record_audit"]["principal_attention"],
            summary["self_check"]["principal_attention"],
        )


if __name__ == "__main__":
    unittest.main()
