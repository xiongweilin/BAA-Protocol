import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

from baa_protocol.delegation_frontier import DelegationBudget
from baa_protocol.experiment import Regime
from baa_protocol.prospective_canary_evidence_study import (
    _observer_templates,
    _reacquire_current_stage_evidence,
)
from baa_protocol.prospective_canary_robustness_study import (
    CONTROL_GROUPS,
    RECOVERY_GROUPS,
    _interaction,
)
from baa_protocol.prospective_canary_study import (
    CanarySimulator,
    load_canary_workload,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_prospective_canary_v5_robustness.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("canary_v5_generator", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_generated_episodes():
    gen = load_generator()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "workload.json"
        path.write_bytes(gen.canonical_bytes())
        version, episodes = load_canary_workload(path)
    return version, episodes


class CanaryV5RobustnessStudyTests(unittest.TestCase):
    def test_observer_only_evidence_is_not_injected_into_visible_state(self):
        version, episodes = load_generated_episodes()
        self.assertEqual(version, "prospective-canary-v5-robustness")
        episode = next(
            ep for ep in episodes
            if ep.logical_name == "recoverable_lag_early-1"
        )
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        initial_evidence = copy.deepcopy(simulator.visible["stage_evidence"])
        hidden_before = copy.deepcopy(simulator.context)

        simulator.apply_events(1)

        # Route readback is public, but observer-only evidence stays out of the
        # model-visible evidence field until the assurance read is invoked.
        self.assertEqual(
            (
                simulator.visible["current_stage_index"],
                simulator.visible["current_weight_percent"],
            ),
            (
                simulator.context["current_stage_index"],
                simulator.context["current_weight_percent"],
            ),
        )
        self.assertEqual(simulator.visible["stage_evidence"], initial_evidence)
        self.assertEqual(simulator.context, hidden_before)

        templates = _observer_templates(episode, through_turn=1)
        key = (
            episode.control_context["experiment_id"],
            0,
            10,
            episode.control_context["state_version"],
        )
        self.assertIn(key, templates)

        self.assertTrue(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=1,
            )
        )
        self.assertEqual(simulator.context, hidden_before)
        self.assertEqual(simulator.visible["stage_evidence"]["stage_index"], 0)
        self.assertEqual(simulator.visible["stage_evidence"]["weight_percent"], 10)

    def test_missing_observer_control_cannot_reacquire_current_route(self):
        _, episodes = load_generated_episodes()
        episode = next(
            ep for ep in episodes
            if ep.logical_name == "missing-observer-1"
        )
        simulator = CanarySimulator(
            episode,
            Regime.BAA,
            DelegationBudget(min_useful_delivery=1),
        )
        simulator.apply_events(1)
        simulator.apply_events(3)
        hidden_before = copy.deepcopy(simulator.context)
        visible_before = copy.deepcopy(simulator.visible)

        self.assertFalse(
            _reacquire_current_stage_evidence(
                episode,
                simulator,
                through_turn=3,
            )
        )
        self.assertEqual(simulator.context, hidden_before)
        self.assertEqual(simulator.visible, visible_before)

    def test_interaction_is_difference_in_differences_over_fixed_groups(self):
        rows = []
        all_groups = RECOVERY_GROUPS + CONTROL_GROUPS
        for group in all_groups:
            for policy in ("no_reacquire", "reacquire"):
                for horizon in (4, 8):
                    delegable = False
                    if group == "recoverable_lag_early":
                        delegable = policy == "reacquire" and horizon == 8
                    elif group == "recoverable_lag_mid":
                        delegable = policy == "reacquire" and horizon == 8
                    elif group == "recoverable_lag_late":
                        delegable = False
                    rows.append(
                        {
                            "study_group": group,
                            "evidence_policy": policy,
                            "horizon": horizon,
                            "delegable": delegable,
                        }
                    )

        aggregate = _interaction(rows, RECOVERY_GROUPS)
        self.assertEqual(
            aggregate,
            {
                "contrast_h4": 0,
                "contrast_h8": 2,
                "interaction": 2,
            },
        )
        per_group = {
            group: _interaction(rows, (group,))
            for group in RECOVERY_GROUPS
        }
        self.assertEqual(per_group["recoverable_lag_early"]["interaction"], 1)
        self.assertEqual(per_group["recoverable_lag_mid"]["interaction"], 1)
        self.assertEqual(per_group["recoverable_lag_late"]["interaction"], 0)
        self.assertEqual(
            sum(int(v["interaction"] > 0) for v in per_group.values()),
            2,
        )

    def test_all_six_groups_have_four_episodes(self):
        _, episodes = load_generated_episodes()
        for group in RECOVERY_GROUPS + CONTROL_GROUPS:
            self.assertEqual(
                sum(int(ep.study_group == group) for ep in episodes),
                4,
            )


if __name__ == "__main__":
    unittest.main()
