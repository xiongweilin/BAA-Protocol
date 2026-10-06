import unittest

from baa_protocol.prospective_cost_frontier_study import (
    ARCH_ATTENTION,
    ARCH_AUTO_INTERVENTIONS,
    ARCH_HUMAN_LABOR,
    ARCH_UNRESOLVED,
    ARCH_UNSAFE,
    EVIDENCE_AUTO_INTERVENTIONS,
    EVIDENCE_HORIZONS,
    EVIDENCE_REACQUISITIONS,
    architecture_strict_safe,
    evidence_endpoints,
)


def arch_cell(capability, labor, interventions, self_count, audit_count, baa_count):
    return {
        "capability_level": capability,
        "ceiling": {
            "max_principal_attention": 0,
            "max_unsafe_transitions": 0,
            "max_terminal_unresolved_results": 0,
            "min_useful_delivery": 1,
            "max_assurance_labor_units": labor,
            "max_assurance_interventions": interventions,
            "max_evidence_reacquisitions": None,
            "require_completed": True,
        },
        "regimes": {
            "self_check": {"delegable_episodes": self_count},
            "external_record_audit": {"delegable_episodes": audit_count},
            "bounded_action_protocol": {"delegable_episodes": baa_count},
        },
    }


def evidence_cell(horizon, no_count, yes_count, target_no, target_yes, control=1):
    groups_no = {
        "stale_evidence_recovery": {"delegable_episodes": target_no},
        "clean_control": {"delegable_episodes": control},
        "guardrail_control": {"delegable_episodes": 0},
        "missing_observer_control": {"delegable_episodes": 0},
        "lost_ack_recovery": {"delegable_episodes": control},
        "rollback_unavailable_control": {"delegable_episodes": 0},
    }
    groups_yes = {key: dict(value) for key, value in groups_no.items()}
    groups_yes["stale_evidence_recovery"] = {
        "delegable_episodes": target_yes
    }
    return {
        "horizon": horizon,
        "ceiling": {},
        "policies": {
            "no_reacquire": {"delegable_episodes": no_count},
            "reacquire": {"delegable_episodes": yes_count},
        },
        "groups": {
            "no_reacquire": groups_no,
            "reacquire": groups_yes,
        },
    }


class ProspectiveCostFrontierStudyTests(unittest.TestCase):
    def test_preregistered_cost_grids_are_frozen(self):
        self.assertEqual(ARCH_ATTENTION, (0, 1))
        self.assertEqual(ARCH_UNSAFE, (0, 1, 2, 4))
        self.assertEqual(ARCH_UNRESOLVED, (0, 1))
        self.assertEqual(ARCH_HUMAN_LABOR, (0, 1, 2, 3, 5))
        self.assertEqual(ARCH_AUTO_INTERVENTIONS, (0, 1, 2, 3, 4, 5))
        self.assertEqual(EVIDENCE_HORIZONS, (4, 8))
        self.assertEqual(
            EVIDENCE_AUTO_INTERVENTIONS,
            (0, 2, 4, 6, 8, 12, 16, 20),
        )
        self.assertEqual(EVIDENCE_REACQUISITIONS, (0, 1, 2))

    def test_architecture_persistence_is_defined_over_strict_safe_cells(self):
        cells = [
            arch_cell(0, 0, 0, 2, 2, 2),
            arch_cell(1, 0, 0, 2, 2, 3),
            arch_cell(2, 0, 0, 2, 2, 3),
            arch_cell(2, 1, 1, 2, 2, 4),
        ]
        endpoint = architecture_strict_safe(cells)
        self.assertEqual(endpoint["0"]["positive_cells"], 0)
        self.assertEqual(endpoint["1"]["positive_cells"], 1)
        self.assertEqual(endpoint["2"]["positive_cells"], 2)
        self.assertTrue(endpoint["persistence"]["met"])

    def test_evidence_target_and_controls_are_separate(self):
        cells = [
            evidence_cell(4, 2, 3, 0, 1),
            evidence_cell(8, 2, 4, 0, 2),
        ]
        endpoint = evidence_endpoints(cells)
        self.assertEqual(
            endpoint["by_horizon"]["4"]["target_recovery_positive_cells"],
            1,
        )
        self.assertEqual(
            endpoint["by_horizon"]["8"]["target_recovery_positive_cells"],
            1,
        )
        self.assertTrue(endpoint["target_persistence"]["met"])
        self.assertTrue(endpoint["control_invariance"]["met"])

    def test_control_policy_difference_fails_invariance(self):
        cell = evidence_cell(8, 2, 3, 0, 1)
        cell["groups"]["reacquire"]["clean_control"][
            "delegable_episodes"
        ] = 0
        endpoint = evidence_endpoints([cell])
        self.assertFalse(endpoint["control_invariance"]["met"])
        self.assertEqual(endpoint["control_invariance"]["mismatch_cells"], 1)


if __name__ == "__main__":
    unittest.main()
