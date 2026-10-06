import unittest

from baa_protocol.cost_frontier import (
    FrontierCeiling,
    architecture_slice,
    canary_slice,
    pareto_points,
    row_feasible,
    source_from_results,
)


def _row(**overrides):
    row = {
        "completed": True,
        "useful_delivery": 3,
        "principal_attention": 0,
        "unsafe_transitions": 0,
        "terminal_unresolved_results": 0,
        "assurance_labor_units": 0,
        "assurance_interventions": 0,
        "logical_model_calls": 1,
        "model_input_tokens": 10,
        "model_output_tokens": 2,
    }
    row.update(overrides)
    return row


class CostFrontierTests(unittest.TestCase):
    def test_feasibility_keeps_all_budgets_separate(self):
        ceiling = FrontierCeiling(
            max_principal_attention=0,
            max_unsafe_transitions=0,
            max_terminal_unresolved_results=0,
            min_useful_delivery=3,
            max_assurance_labor_units=2,
            max_assurance_interventions=1,
        )
        self.assertTrue(row_feasible(_row(), ceiling))
        self.assertFalse(row_feasible(_row(principal_attention=1), ceiling))
        self.assertFalse(row_feasible(_row(unsafe_transitions=1), ceiling))
        self.assertFalse(
            row_feasible(_row(terminal_unresolved_results=1), ceiling)
        )
        self.assertFalse(row_feasible(_row(assurance_labor_units=3), ceiling))
        self.assertFalse(row_feasible(_row(assurance_interventions=2), ceiling))
        self.assertFalse(row_feasible(_row(useful_delivery=2), ceiling))
        self.assertFalse(row_feasible(_row(completed=False), ceiling))

    def test_source_from_results_preserves_architecture_and_canary_costs(self):
        offboarding = {
            "levels": [
                {
                    "episodes": [
                        {
                            "episode_id": "O1",
                            "logical_name": "offboarding",
                            "study_group": "recovery",
                            "regime": "bounded_action_protocol",
                            "capability_level": 2,
                            "completed": True,
                            "model_calls": 4,
                            "model_input_tokens": 100,
                            "model_output_tokens": 10,
                            "metrics": {
                                "useful_delivery": 3,
                                "principal_attention": 0,
                                "unsafe_transitions": 0,
                                "terminal_unresolved_results": 0,
                                "assurance_labor_units": 0,
                                "assurance_interventions": 2,
                            },
                        }
                    ]
                }
            ]
        }
        canary = {
            "episodes": [
                {
                    "episode_id": "C1",
                    "logical_name": "canary",
                    "study_group": "recovery",
                    "evidence_policy": "reacquire",
                    "horizon": 8,
                    "completed": True,
                    "evidence_reacquisitions": 2,
                    "model_calls": 5,
                    "model_input_tokens": 200,
                    "model_output_tokens": 20,
                    "metrics": {
                        "useful_delivery": 1,
                        "principal_attention": 0,
                        "unsafe_transitions": 0,
                        "terminal_unresolved_results": 0,
                        "assurance_labor_units": 0,
                        "assurance_interventions": 5,
                    },
                }
            ]
        }
        source = source_from_results(offboarding, canary)
        self.assertEqual(source["version"], "delegation-cost-frontier-v1-source")
        self.assertEqual(source["sources"][0]["rows"][0]["assurance_interventions"], 2)
        self.assertEqual(source["sources"][1]["rows"][0]["evidence_reacquisitions"], 2)

    def test_architecture_intervention_ceiling_changes_baa_not_direct(self):
        source = {
            "version": "delegation-cost-frontier-v1-source",
            "sources": [
                {
                    "study": "prospective-offboarding-v6",
                    "rows": [
                        {
                            "episode_id": "self",
                            "logical_name": "self",
                            "study_group": "g",
                            "regime": "self_check",
                            "capability_level": 2,
                            **_row(),
                        },
                        {
                            "episode_id": "baa",
                            "logical_name": "baa",
                            "study_group": "g",
                            "regime": "bounded_action_protocol",
                            "capability_level": 2,
                            **_row(assurance_interventions=2),
                        },
                    ],
                },
                {
                    "study": "prospective-canary-v5-robustness",
                    "rows": [],
                },
            ],
        }
        strict = FrontierCeiling(0, 0, 0, 3, 5, 0)
        relaxed = FrontierCeiling(0, 0, 0, 3, 5, 2)
        strict_summary = architecture_slice(
            source,
            capability_level=2,
            ceiling=strict,
        )
        relaxed_summary = architecture_slice(
            source,
            capability_level=2,
            ceiling=relaxed,
        )
        self.assertEqual(strict_summary["self_check"]["delegable_episodes"], 1)
        self.assertEqual(
            strict_summary["bounded_action_protocol"]["delegable_episodes"],
            0,
        )
        self.assertEqual(
            relaxed_summary["bounded_action_protocol"]["delegable_episodes"],
            1,
        )

    def test_canary_reacquisition_and_intervention_are_distinct_ceilings(self):
        source = {
            "version": "delegation-cost-frontier-v1-source",
            "sources": [
                {"study": "prospective-offboarding-v6", "rows": []},
                {
                    "study": "prospective-canary-v5-robustness",
                    "rows": [
                        {
                            "episode_id": "C1",
                            "logical_name": "canary",
                            "study_group": "g",
                            "evidence_policy": "reacquire",
                            "horizon": 8,
                            "evidence_reacquisitions": 2,
                            **_row(
                                useful_delivery=1,
                                assurance_interventions=5,
                            ),
                        }
                    ],
                },
            ],
        }
        blocked = FrontierCeiling(0, 0, 0, 1, 0, 5, 1)
        allowed = FrontierCeiling(0, 0, 0, 1, 0, 5, 2)
        self.assertEqual(
            canary_slice(source, horizon=8, ceiling=blocked)["reacquire"][
                "delegable_episodes"
            ],
            0,
        )
        self.assertEqual(
            canary_slice(source, horizon=8, ceiling=allowed)["reacquire"][
                "delegable_episodes"
            ],
            1,
        )

    def test_pareto_removes_more_expensive_equal_delivery_point(self):
        rows = [
            {
                "ceiling": {
                    "max_principal_attention": 0,
                    "max_unsafe_transitions": 0,
                },
                "delegable_episodes": 2,
            },
            {
                "ceiling": {
                    "max_principal_attention": 1,
                    "max_unsafe_transitions": 0,
                },
                "delegable_episodes": 2,
            },
            {
                "ceiling": {
                    "max_principal_attention": 1,
                    "max_unsafe_transitions": 1,
                },
                "delegable_episodes": 3,
            },
        ]
        selected = pareto_points(
            rows,
            resource_fields=(
                "max_principal_attention",
                "max_unsafe_transitions",
            ),
        )
        self.assertEqual(len(selected), 2)
        self.assertNotIn(rows[1], selected)


if __name__ == "__main__":
    unittest.main()
