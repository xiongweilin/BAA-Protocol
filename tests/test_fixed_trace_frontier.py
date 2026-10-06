import unittest

from baa_protocol.fixed_trace_frontier import (
    CostVector,
    TraceOutcome,
    analyze_fixed_trace_results,
    fixed_trace_envelope,
    outcomes_from_result,
)


def outcome(
    name: str,
    *,
    attention: int = 0,
    risk: int = 0,
    labor: int = 0,
    interventions: int = 0,
    completed: bool = True,
    unresolved: int = 0,
) -> TraceOutcome:
    return TraceOutcome(
        study="study",
        capability_level=2,
        episode_id=f"episode:{name}",
        logical_name=name,
        study_group="group",
        regime="self_check",
        completed=completed,
        principal_attention=attention,
        unsafe_transitions=risk,
        terminal_unresolved_results=unresolved,
        assurance_labor_units=labor,
        assurance_interventions=interventions,
    )


class FixedTraceFrontierTests(unittest.TestCase):
    def test_cost_vector_keeps_human_and_automated_assurance_separate(self):
        left = CostVector(0, 0, 2, 0)
        right = CostVector(0, 0, 0, 3)
        total = left.add(right)
        self.assertEqual(total.assurance_labor_units, 2)
        self.assertEqual(total.assurance_interventions, 3)

    def test_exact_envelope_preserves_risk_and_intervention_tradeoff(self):
        rows = (
            outcome("free"),
            outcome("risky", risk=1),
            outcome("assured", interventions=2),
        )
        points = fixed_trace_envelope(rows)
        values = {(
            point.principal_attention,
            point.unsafe_transitions,
            point.assurance_labor_units,
            point.assurance_interventions,
            point.completed_work,
        ) for point in points}
        self.assertIn((0, 0, 0, 0, 1), values)
        self.assertIn((0, 0, 0, 2, 2), values)
        self.assertIn((0, 1, 0, 0, 2), values)
        self.assertIn((0, 1, 0, 2, 3), values)

    def test_attention_is_a_cost_axis_not_a_hard_exclusion(self):
        points = fixed_trace_envelope(
            (
                outcome("free"),
                outcome("needs-attention", attention=1),
            )
        )
        values = {(p.principal_attention, p.completed_work) for p in points}
        self.assertIn((0, 1), values)
        self.assertIn((1, 2), values)

    def test_terminally_unresolved_trace_never_contributes_work(self):
        points = fixed_trace_envelope(
            (
                outcome("resolved"),
                outcome("unresolved", unresolved=1),
            )
        )
        self.assertEqual(max(point.completed_work for point in points), 1)

    def test_incomplete_trace_never_contributes_work(self):
        points = fixed_trace_envelope(
            (
                outcome("resolved"),
                outcome("incomplete", completed=False),
            )
        )
        self.assertEqual(max(point.completed_work for point in points), 1)

    def test_parser_normalizes_accepted_result_shape(self):
        result = {
            "levels": [
                {
                    "capability": {"level": 2, "extra_turns": 4},
                    "episodes": [
                        {
                            "episode_id": "E1",
                            "logical_name": "one",
                            "study_group": "clean",
                            "regime": "bounded_action_protocol",
                            "completed": True,
                            "metrics": {
                                "principal_attention": 0,
                                "unsafe_transitions": 0,
                                "terminal_unresolved_results": 0,
                                "assurance_labor_units": 0,
                                "assurance_interventions": 2,
                            },
                            "model_calls": 4,
                            "model_input_tokens": 100,
                            "model_output_tokens": 20,
                        }
                    ],
                }
            ]
        }
        rows = outcomes_from_result("accepted", result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].study, "accepted")
        self.assertEqual(rows[0].capability_level, 2)
        self.assertEqual(rows[0].assurance_interventions, 2)
        self.assertEqual(rows[0].logical_model_calls, 4)

    def test_analysis_reports_fixed_trace_limit_and_pooled_envelope(self):
        def result(regime: str, risk: int) -> dict:
            return {
                "workload_version": "test-v1",
                "model_id": "model",
                "model_interface": "function_tool",
                "physical_sampling": {"calls": 1},
                "levels": [
                    {
                        "capability": {"level": 2, "extra_turns": 4},
                        "episodes": [
                            {
                                "episode_id": "E1",
                                "logical_name": "one",
                                "study_group": "clean",
                                "regime": regime,
                                "completed": True,
                                "metrics": {
                                    "principal_attention": 0,
                                    "unsafe_transitions": risk,
                                    "terminal_unresolved_results": 0,
                                    "assurance_labor_units": 0,
                                    "assurance_interventions": 0,
                                },
                            }
                        ],
                    }
                ],
            }

        analysis = analyze_fixed_trace_results(
            (
                ("a", result("self_check", 1)),
                ("b", result("self_check", 0)),
            )
        )
        self.assertEqual(
            analysis["analysis_kind"],
            "fixed-trace-feasible-envelope",
        )
        self.assertIn("not a budget-aware policy-optimal frontier", analysis["interpretation_limit"])
        pooled = analysis["pooled"]["C2"]["self_check"]
        self.assertEqual(pooled["observed_episode_rows"], 2)
        values = {
            (point["unsafe_transitions"], point["completed_work"])
            for point in pooled["envelope"]
        }
        self.assertIn((0, 1), values)
        self.assertIn((1, 2), values)

    def test_model_calls_are_reported_but_not_part_of_cost_vector(self):
        row = outcome("one")
        self.assertEqual(
            row.cost,
            CostVector(0, 0, 0, 0),
        )


if __name__ == "__main__":
    unittest.main()
