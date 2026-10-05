import unittest

from baa_protocol.delegation_frontier import (
    DelegationBudget,
    capability_sweep,
    evaluate_capability_sweep,
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

    def test_unrecovered_unknown_consumes_attention_and_stays_outside_frontier(self):
        scenario = EpisodeScenario(
            "unknown",
            post_execution_observation_outage=True,
        )
        result = evaluate_delegation_frontier(
            (scenario,),
            budget=DelegationBudget(),
        )

        for episode in result["episodes"]:
            self.assertFalse(episode["completed"])
            self.assertEqual(episode["terminal_unresolved_results"], 1)
            self.assertEqual(episode["principal_attention"], 1)
            self.assertFalse(episode["delegable"])

        baa_episode = next(
            episode
            for episode in result["episodes"]
            if episode["regime"] == Regime.BAA.value
        )
        self.assertEqual(baa_episode["unsafe_transitions"], 0)

    def test_automatic_assurance_interventions_are_not_principal_attention_or_manual_labor(self):
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
        self.assertEqual(baa_episode["assurance_labor_units"], 0)

    def test_post_hoc_audit_exposes_synthetic_assurance_labor_separately(self):
        scenario = EpisodeScenario("normal")

        self_check = run_episode(scenario, Regime.SELF_CHECK)
        audit = run_episode(scenario, Regime.AUDIT)
        baa = run_episode(scenario, Regime.BAA)

        self.assertEqual(self_check.metrics.assurance_labor_units, 0)
        self.assertEqual(audit.metrics.assurance_labor_units, 3)
        self.assertEqual(baa.metrics.assurance_labor_units, 0)
        self.assertEqual(audit.metrics.principal_attention, 0)

    def test_wrong_subject_is_not_counted_as_useful_delivery(self):
        direct = run_episode(
            EpisodeScenario("wrong-subject", wrong_subject=True),
            Regime.SELF_CHECK,
        )

        self.assertEqual(direct.metrics.unsafe_transitions, 1)
        self.assertEqual(direct.metrics.useful_delivery, 2)
        self.assertFalse(direct.metrics.completed)

    def test_capability_sweep_uses_same_logical_workload_at_each_level(self):
        sweep = evaluate_capability_sweep()
        levels = sweep["levels"]

        self.assertEqual(
            [level["capability"]["level"] for level in levels],
            [item.level for item in capability_sweep()],
        )
        scenario_sets = {
            tuple(
                sorted(
                    episode["scenario"]
                    for episode in level["episodes"]
                    if episode["regime"] == Regime.BAA.value
                )
            )
            for level in levels
        }
        self.assertEqual(len(scenario_sets), 1)

    def test_current_fixture_advantage_persists_as_adaptive_resources_increase(self):
        sweep = evaluate_capability_sweep()
        by_level = {
            level["capability"]["level"]: level["summary"]
            for level in sweep["levels"]
        }

        for regime in Regime:
            self.assertEqual(
                by_level[0][regime.value]["delegable_episodes"],
                4,
            )

        for capability_level in (1, 2):
            self.assertEqual(
                by_level[capability_level][Regime.SELF_CHECK.value][
                    "delegable_episodes"
                ],
                2,
            )
            self.assertEqual(
                by_level[capability_level][Regime.AUDIT.value][
                    "delegable_episodes"
                ],
                2,
            )
            self.assertEqual(
                by_level[capability_level][Regime.BAA.value][
                    "delegable_episodes"
                ],
                4,
            )
            self.assertEqual(
                by_level[capability_level][Regime.BAA.value][
                    "unsafe_transitions"
                ],
                0,
            )

        self.assertGreater(
            by_level[2][Regime.SELF_CHECK.value]["unsafe_transitions"],
            by_level[1][Regime.SELF_CHECK.value]["unsafe_transitions"],
        )
        self.assertGreater(
            by_level[2][Regime.BAA.value]["assurance_interventions"],
            by_level[1][Regime.BAA.value]["assurance_interventions"],
        )

    def test_optional_assurance_labor_budget_can_make_audit_infeasible(self):
        result = evaluate_delegation_frontier(
            (EpisodeScenario("normal"),),
            budget=DelegationBudget(max_assurance_labor_units=0),
        )

        audit = result["summary"][Regime.AUDIT.value]
        self_check = result["summary"][Regime.SELF_CHECK.value]
        baa = result["summary"][Regime.BAA.value]

        self.assertEqual(audit["delegable_episodes"], 0)
        self.assertEqual(self_check["delegable_episodes"], 1)
        self.assertEqual(baa["delegable_episodes"], 1)


if __name__ == "__main__":
    unittest.main()
