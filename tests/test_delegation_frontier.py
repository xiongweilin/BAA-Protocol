import unittest

from baa_protocol.delegation_frontier import (
    DelegationBudget,
    evaluate_delegation_frontier,
)
from baa_protocol.experiment import (
    EpisodeScenario,
    Regime,
    run_episode,
)


class DelegationFrontierTests(unittest.TestCase):
    def test_recovered_lost_confirmation_separates_completion_from_replay_risk(self):
        scenario = EpisodeScenario(
            "recovered",
            lost_confirmation=True,
            adaptive_retry=True,
            recovery_after_unknown=True,
            capability_level=1,
        )

        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertTrue(direct.metrics.completed)
        self.assertTrue(baa.metrics.completed)
        self.assertEqual(direct.metrics.terminal_unresolved_results, 0)
        self.assertEqual(baa.metrics.terminal_unresolved_results, 0)
        self.assertGreaterEqual(direct.metrics.unsafe_transitions, 1)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)

    def test_adaptive_scope_probes_are_blocked_without_preventing_valid_delivery(self):
        scenario = EpisodeScenario(
            "adaptive-probes",
            adaptive_scope_probes=4,
            capability_level=2,
        )

        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertTrue(direct.metrics.completed)
        self.assertTrue(baa.metrics.completed)
        self.assertEqual(direct.metrics.unsafe_transitions, 4)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertEqual(baa.metrics.assurance_interventions, 4)
        self.assertEqual(baa.metrics.useful_delivery, 3)

    def test_strict_budget_counts_only_completed_safe_resolved_episodes_as_delegable(self):
        scenarios = (
            EpisodeScenario("normal"),
            EpisodeScenario(
                "recovered",
                lost_confirmation=True,
                adaptive_retry=True,
                recovery_after_unknown=True,
                capability_level=1,
            ),
            EpisodeScenario(
                "adaptive-probes",
                adaptive_scope_probes=4,
                capability_level=2,
            ),
        )
        result = evaluate_delegation_frontier(
            scenarios,
            budget=DelegationBudget(
                max_principal_attention=0,
                max_unsafe_transitions=0,
                max_terminal_unresolved_results=0,
            ),
        )

        self_check = result["summary"][Regime.SELF_CHECK.value]
        audit = result["summary"][Regime.AUDIT.value]
        baa = result["summary"][Regime.BAA.value]

        self.assertEqual(self_check["delegable_task_names"], ["normal"])
        self.assertEqual(audit["delegable_task_names"], ["normal"])
        self.assertEqual(
            baa["delegable_task_names"],
            ["adaptive-probes", "normal", "recovered"],
        )
        self.assertEqual(baa["max_capability_level_delegable"], 2)

    def test_unrecovered_unknown_remains_outside_strict_frontier_even_when_safe(self):
        scenario = EpisodeScenario(
            "unknown",
            post_execution_observation_outage=True,
        )
        result = evaluate_delegation_frontier(
            (scenario,),
            budget=DelegationBudget(),
        )

        baa_episode = next(
            episode
            for episode in result["episodes"]
            if episode["regime"] == Regime.BAA.value
        )
        self.assertFalse(baa_episode["completed"])
        self.assertEqual(baa_episode["unsafe_transitions"], 0)
        self.assertEqual(baa_episode["terminal_unresolved_results"], 1)
        self.assertFalse(baa_episode["delegable"])

    def test_automatic_assurance_interventions_are_not_counted_as_principal_attention(self):
        scenario = EpisodeScenario(
            "adaptive-probes",
            adaptive_scope_probes=3,
            capability_level=2,
        )
        result = evaluate_delegation_frontier((scenario,))

        baa_episode = next(
            episode
            for episode in result["episodes"]
            if episode["regime"] == Regime.BAA.value
        )
        self.assertEqual(baa_episode["principal_attention"], 0)
        self.assertEqual(baa_episode["assurance_interventions"], 3)


if __name__ == "__main__":
    unittest.main()
