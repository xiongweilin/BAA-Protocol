import unittest

from baa_protocol.experiment import (
    EpisodeScenario,
    Regime,
    run_episode,
    run_suite,
    scenario_suite,
    summarize,
)


class OffboardingExperimentTests(unittest.TestCase):
    def test_normal_episode_delivers_all_external_obligations_in_all_regimes(self):
        scenario = EpisodeScenario("normal")

        results = {
            regime: run_episode(scenario, regime)
            for regime in Regime
        }

        for result in results.values():
            self.assertTrue(result.metrics.completed)
            self.assertEqual(result.metrics.useful_delivery, 3)
            self.assertEqual(result.metrics.unsafe_transitions, 0)

    def test_scope_and_timing_faults_are_blocked_by_baa(self):
        scenarios = (
            EpisodeScenario("before", before_effective=True),
            EpisodeScenario("stale", stale_authority_epoch=True),
            EpisodeScenario("subject", wrong_subject=True),
            EpisodeScenario("operation", wrong_operation=True),
            EpisodeScenario("protected", protected_source_target=True),
        )

        for scenario in scenarios:
            with self.subTest(scenario=scenario.name):
                direct = run_episode(scenario, Regime.SELF_CHECK)
                baa = run_episode(scenario, Regime.BAA)

                self.assertGreaterEqual(direct.metrics.unsafe_transitions, 1)
                self.assertEqual(baa.metrics.unsafe_transitions, 0)
                self.assertGreaterEqual(
                    baa.metrics.denied + baa.metrics.held,
                    1,
                )

    def test_post_hoc_audit_records_but_does_not_prevent_fault(self):
        scenario = EpisodeScenario("wrong-subject", wrong_subject=True)

        self_check = run_episode(scenario, Regime.SELF_CHECK)
        audit = run_episode(scenario, Regime.AUDIT)
        baa = run_episode(scenario, Regime.BAA)

        self.assertEqual(self_check.metrics.unsafe_transitions, 1)
        self.assertEqual(audit.metrics.unsafe_transitions, 1)
        self.assertTrue(audit.events)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)

    def test_lost_confirmation_retry_is_not_executed_by_baa(self):
        scenario = EpisodeScenario(
            "lost-confirmation",
            lost_confirmation=True,
            adaptive_retry=True,
        )

        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertEqual(direct.metrics.replay_attempts, 1)
        self.assertGreaterEqual(direct.metrics.unsafe_transitions, 1)
        self.assertEqual(baa.metrics.replay_attempts, 1)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertEqual(baa.metrics.unknown_results, 1)
        self.assertFalse(baa.metrics.completed)

    def test_observation_outage_can_reduce_delivery_without_becoming_safety_failure(self):
        scenario = EpisodeScenario(
            "observation-outage",
            observation_outage=True,
        )

        direct = run_episode(scenario, Regime.SELF_CHECK)
        baa = run_episode(scenario, Regime.BAA)

        self.assertFalse(direct.metrics.completed)
        self.assertFalse(baa.metrics.completed)
        self.assertEqual(baa.metrics.unsafe_transitions, 0)
        self.assertGreaterEqual(baa.metrics.held, 1)

    def test_baa_vsar_keeps_denied_and_held_proposals(self):
        scenario = EpisodeScenario(
            "lost-confirmation",
            lost_confirmation=True,
            adaptive_retry=True,
        )
        result = run_episode(scenario, Regime.BAA)

        dispositions = {
            (event.phase, event.disposition)
            for event in result.events
        }
        self.assertIn(("admission", "admit"), dispositions)
        self.assertIn(("admission", "hold"), dispositions)
        self.assertIn(("execution", "unknown"), dispositions)

    def test_suite_contains_all_scenarios_and_regimes(self):
        results = run_suite()
        self.assertEqual(
            len(results),
            len(scenario_suite()) * len(Regime),
        )

        observed = {
            (result.scenario, result.regime)
            for result in results
        }
        expected = {
            (scenario.name, regime)
            for scenario in scenario_suite()
            for regime in Regime
        }
        self.assertEqual(observed, expected)

    def test_summary_does_not_merge_safety_and_delivery(self):
        summary = summarize(run_suite())

        baa = summary[Regime.BAA.value]
        direct = summary[Regime.SELF_CHECK.value]

        self.assertEqual(baa["unsafe_transitions"], 0)
        self.assertGreater(direct["unsafe_transitions"], 0)
        # The conservative BAA fixture is allowed to deliver less work while
        # holding unsafe or unverifiable transitions. This prevents a test
        # suite from equating "safer" with "completed more".
        self.assertLessEqual(
            baa["useful_delivery"],
            direct["useful_delivery"],
        )


if __name__ == "__main__":
    unittest.main()
