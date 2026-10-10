"""Independent exhaustive oracle and adversarial metamorphic tests.

No real-model performance claims: all inputs are deterministic, synthetic,
bounded worlds. The oracle does NOT call the production synthesize function.
"""
from __future__ import annotations

import random
import unittest
from dataclasses import replace

from baa_protocol.contingent_policy import (
    Effect, Probe, assert_structurally_safe, synthesize,
)


class ContingentPolicyOracleTests(unittest.TestCase):
    def _oracle(self, belief, goals, safe, effects, probes, limit):
        """Enumerate all finite AND/OR continuation choices; return min cost."""
        def solve(states, used, depth):
            if states <= goals:
                return 0
            if depth == 0:
                return None
            prices = []
            for effect in effects:
                if effect.name in used or not effect.authorized:
                    continue
                transitions = effect.as_map()
                if not states <= transitions.keys():
                    continue
                after = frozenset(
                    successor for state in states
                    for successor in transitions[state]
                )
                if not after <= safe:
                    continue
                cost = solve(after, used | {effect.name}, depth - 1)
                if cost is not None:
                    prices.append(effect.cost + cost)
            for probe in probes:
                if not probe.trusted:
                    continue
                readings = probe.as_map()
                if not states <= readings.keys():
                    continue
                partitions = [
                    frozenset(state for state in states if readings[state] == label)
                    for label in sorted({readings[state] for state in states})
                ]
                if len(partitions) < 2:
                    continue
                branch_prices = [
                    solve(part, used, depth - 1) for part in partitions
                ]
                if all(price is not None for price in branch_prices):
                    prices.append(probe.cost + max(branch_prices))
            return min(prices) if prices else None
        return solve(belief, frozenset(), limit)

    def test_300_seeded_adversarial_world_models_match_independent_oracle(self):
        rng = random.Random(20261010)
        worlds = ("s0", "s1", "s2", "goal")
        safe = frozenset(worlds)
        goal = frozenset({"goal"})
        for case in range(300):
            belief = frozenset(
                w for w in ("s0", "s1", "s2") if rng.getrandbits(1)
            ) or frozenset({"s0"})
            effects = []
            for idx in range(3):
                transitions = []
                for state in worlds:
                    if rng.getrandbits(1):
                        outcomes = tuple(rng.sample(
                            ("s0", "s1", "s2", "goal", "unsafe"),
                            rng.randint(1, 2),
                        ))
                        transitions.append((state, outcomes))
                effects.append(Effect(
                    f"e{idx}", tuple(transitions),
                    authorized=bool(rng.getrandbits(1)), cost=rng.randint(1, 4),
                ))
            probes = []
            for idx in range(2):
                readings = tuple(
                    (state, rng.choice(("a", "b", "c")))
                    for state in worlds if rng.getrandbits(1)
                )
                probes.append(Probe(
                    f"p{idx}", readings, trusted=bool(rng.getrandbits(1)),
                    cost=rng.randint(1, 3),
                ))
            horizon = rng.randint(0, 4)
            kwargs = dict(
                possible_states=belief,
                goal_states=goal,
                safe_states=safe,
                effects=tuple(effects),
                probes=tuple(probes),
                max_steps=horizon,
            )
            policy = synthesize(**kwargs)
            optimal = self._oracle(
                belief, goal, safe, tuple(effects), tuple(probes), horizon
            )
            self.assertEqual(
                policy.worst_cost if policy else None, optimal,
                f"oracle mismatch at synthetic case {case}",
            )
            if policy is not None:
                assert_structurally_safe(policy, **kwargs)
                # Independently forged costs must not pass the checker.
                forged = replace(policy, worst_cost=policy.worst_cost + 1)
                with self.assertRaises(ValueError):
                    assert_structurally_safe(forged, **kwargs)

    def test_policy_already_safe_with_no_effect_is_minimum_zero_cost(self):
        kwargs = dict(
            possible_states=frozenset({"goal"}),
            goal_states=frozenset({"goal"}),
            safe_states=frozenset({"goal"}),
            effects=(), probes=(), max_steps=0,
        )
        policy = synthesize(**kwargs)
        self.assertEqual(policy.kind, "done")
        self.assertEqual(policy.worst_cost, 0)
        assert_structurally_safe(policy, **kwargs)

    def test_more_possible_worlds_cannot_accidentally_satisfy_goal(self):
        kwargs = dict(
            possible_states=frozenset({"done", "pending"}),
            goal_states=frozenset({"done"}),
            safe_states=frozenset({"done", "pending"}),
            effects=(), probes=(), max_steps=4,
        )
        self.assertIsNone(synthesize(**kwargs))

    def test_unknown_effect_requires_distinct_qualified_observation(self):
        effect = Effect(
            "send", (("ready", ("done", "pending")),), authorized=True
        )
        kwargs = dict(
            possible_states=frozenset({"ready"}),
            goal_states=frozenset({"done"}),
            safe_states=frozenset({"ready", "done", "pending"}),
            effects=(effect,), probes=(), max_steps=4,
        )
        self.assertIsNone(synthesize(**kwargs))
        # Even with a probe, no safe reconciliation route from pending
        # means one favourable observation cannot make the plan safe.
        probe = Probe("readback", (
            ("done", "yes"), ("pending", "no"), ("ready", "no"),
        ), trusted=True)
        self.assertIsNone(synthesize(**{**kwargs, "probes": (probe,)}))

    def test_information_refinement_cannot_remove_existing_common_action(self):
        action = Effect("commit", (
            ("s0", ("goal",)), ("s1", ("goal",)),
            ("s2", ("goal",)),
        ), authorized=True)
        for mask in range(1, 8):
            states = frozenset(
                state for bit, state in enumerate(("s0", "s1", "s2"))
                if mask & (1 << bit)
            )
            p = synthesize(
                possible_states=states,
                goal_states=frozenset({"goal"}),
                safe_states=frozenset({"s0", "s1", "s2", "goal"}),
                effects=(action,), probes=(), max_steps=1,
            )
            self.assertIsNotNone(p, states)
            self.assertEqual(p.worst_cost, 1)


if __name__ == "__main__":
    unittest.main()
