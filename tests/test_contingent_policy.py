"""Finite adversarial-belief regression cases; no claim about real-model benefit."""
import unittest
from dataclasses import replace

from baa_protocol.contingent_policy import (
    Effect, Policy, Probe, assert_structurally_safe, synthesize,
)


SAFE = frozenset({"unknown_a", "unknown_b", "ready_a", "ready_b", "done", "pending"})


def approval_effect():
    return Effect("complete", (
        ("ready_a", ("done",)), ("ready_b", ("done",)),
    ), authorized=True)


class ContingentPolicyTests(unittest.TestCase):
    def compile(self, belief, effects, probes=(), *, steps=3, safe=SAFE):
        return synthesize(
            possible_states=frozenset(belief), goal_states=frozenset({"done"}),
            safe_states=safe, effects=tuple(effects), probes=tuple(probes),
            max_steps=steps,
        )

    def verify(self, policy, belief, effects, probes=(), *, steps=3, safe=SAFE):
        assert_structurally_safe(
            policy, possible_states=frozenset(belief),
            goal_states=frozenset({"done"}), safe_states=safe,
            effects=tuple(effects), probes=tuple(probes), max_steps=steps,
        )

    def test_common_safe_step_needs_no_extra_evidence(self):
        effect = approval_effect()
        policy = self.compile({"ready_a", "ready_b"}, (effect,), steps=1)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.kind, "effect")
        self.assertEqual(policy.next.kind, "done")
        self.verify(policy, {"ready_a", "ready_b"}, (effect,), steps=1)

    def test_one_observation_synthesizes_branch_specific_safe_actions(self):
        left = Effect("left", (("unknown_a", ("done",)),), authorized=True)
        right = Effect("right", (("unknown_b", ("done",)),), authorized=True)
        probe = Probe("observe", (("unknown_a", "a"), ("unknown_b", "b")), trusted=True)
        policy = self.compile({"unknown_a", "unknown_b"}, (left, right), (probe,), steps=2)
        self.assertEqual(policy.kind, "probe")
        self.assertEqual({name for name, _ in policy.branches}, {"a", "b"})
        self.assertEqual({child.name for _, child in policy.branches}, {"left", "right"})
        self.verify(policy, {"unknown_a", "unknown_b"}, (left, right), (probe,), steps=2)
        self.assertIsNone(self.compile({"unknown_a", "unknown_b"}, (left, right), (probe,), steps=1))

    def test_missing_or_untrusted_evidence_fails_closed(self):
        effect = Effect("left", (("unknown_a", ("done",)),), authorized=True)
        probe = Probe("observe", (("unknown_a", "a"), ("unknown_b", "b")), trusted=False)
        self.assertIsNone(self.compile({"unknown_a", "unknown_b"}, (effect,), (probe,)))
        self.assertIsNone(self.compile({"unknown_a", "unknown_b"}, (replace(effect, authorized=False),)))

    def test_unsafe_or_nondeterministic_effect_cannot_be_laundered(self):
        dangerous = Effect("uncertain", (("ready_a", ("done", "unsafe")),), authorized=True)
        self.assertIsNone(self.compile({"ready_a"}, (dangerous,)))
        ambiguous = Effect("unknown", (("ready_a", ("done", "pending")),), authorized=True)
        policy = self.compile({"ready_a"}, (ambiguous,), steps=2)
        self.assertIsNone(policy)  # A successful branch cannot silently drop pending.

    def test_forged_policy_rejected_independently(self):
        effect = approval_effect()
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            self.verify(
                Policy("effect", "complete", next=Policy("done")),
                {"ready_a"}, (replace(effect, authorized=False),),
            )
        with self.assertRaisesRegex(ValueError, "completion"):
            self.verify(Policy("done"), {"ready_a"}, (effect,))
        with self.assertRaisesRegex(ValueError, "envelope"):
            self.verify(
                Policy("effect", "complete", next=Policy("done")),
                {"ready_a"}, (effect,), safe=frozenset({"ready_a"}),
            )

    def test_incomplete_branch_and_fake_observation_are_rejected(self):
        probe = Probe("see", (("unknown_a", "a"), ("unknown_b", "b")), trusted=True)
        fake = Policy("probe", "see", branches=(("a", Policy("done")),))
        with self.assertRaisesRegex(ValueError, "branch"):
            self.verify(fake, {"unknown_a", "unknown_b"}, (), (probe,))

    def test_invalid_model_definition_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.compile(
                {"ready_a"}, (Effect("effect", (("ready_a", ("done",)),
                    ("ready_a", ("done",))), authorized=True),),
            )
        with self.assertRaisesRegex(ValueError, "positive"):
            self.compile({"ready_a"}, (replace(approval_effect(), cost=0),))

    def test_minimum_worst_cost_not_arbitrary_hold(self):
        direct = approval_effect()
        probe = Probe("read", (("ready_a", "a"), ("ready_b", "b")), trusted=True)
        plan = self.compile({"ready_a", "ready_b"}, (direct,), (probe,), steps=3)
        self.assertEqual(plan.kind, "effect")
        self.assertEqual(plan.worst_cost, 1)


if __name__ == "__main__":
    unittest.main()
