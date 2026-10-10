"""Cross-repo experimental contract check. Never sends external provider effects.

Run with BAA root and the experimental AIOS checkout on PYTHONPATH.
This only verifies that *policy proposals* survive lowering through the
AIOS version-bound staging cursor, not production effect authority.
"""
from __future__ import annotations

from administrative_orchestrator.contingent_execution import (
    CaseBinding,
    ContingentPolicyCursor,
    ContingentPolicyViolation,
)
from baa_protocol.contingent_policy import (
    Effect,
    Probe,
    assert_structurally_safe,
    synthesize,
)


def main() -> None:
    states = frozenset({"candidate-a", "candidate-b"})
    safe = states | frozenset({"qualified"})
    effects = (
        Effect("iam.disable.a", (("candidate-a", ("qualified",)),), authorized=True),
        Effect("iam.disable.b", (("candidate-b", ("qualified",)),), authorized=True),
    )
    probe = Probe(
        "qualified.subject.readback",
        (("candidate-a", "a"), ("candidate-b", "b")),
        trusted=True,
    )
    plan = synthesize(
        possible_states=states,
        goal_states=frozenset({"qualified"}),
        safe_states=safe,
        effects=effects,
        probes=(probe,),
        max_steps=2,
    )
    if plan is None or plan.kind != "probe":
        raise AssertionError("expected a genuinely conditional safe strategy")
    assert_structurally_safe(
        plan, possible_states=states, goal_states=frozenset({"qualified"}),
        safe_states=safe, effects=effects, probes=(probe,), max_steps=2,
    )
    binding = CaseBinding("fixture-only-not-authorized", 2, 3)
    planned = plan.as_dict()
    assert set(planned["branches"]) == {"a", "b"}
    for label in ("a", "b"):
        effect_name = f"iam.disable.{label}"
        cursor = ContingentPolicyCursor(
            planned, binding,
            authorize_effect=lambda _binding, name, expected=effect_name: name == expected,
            qualify_probe=lambda _binding, name: name == "qualified.subject.readback",
        )
        assert cursor.next_step(binding).kind == "probe"
        cursor.observe(
            binding, probe_name="qualified.subject.readback",
            observed_label=label, independent_readback=True,
        )
        request = cursor.next_step(binding)
        assert (request.kind, request.name) == ("effect", effect_name)
        assert cursor.next_step(binding).kind == "blocked"  # no double dispatch
        cursor.resolve_effect(
            binding, effect_name=effect_name,
            result="verified", independent_readback=True,
        )
        assert cursor.next_step(binding).kind == "done"

    denied = ContingentPolicyCursor(
        planned, binding,
        authorize_effect=lambda _binding, name: False,
        qualify_probe=lambda _binding, name: True,
    )
    denied.next_step(binding)
    denied.observe(
        binding, probe_name="qualified.subject.readback",
        observed_label="a", independent_readback=True,
    )
    try:
        denied.next_step(binding)
    except ContingentPolicyViolation:
        pass
    else:
        raise AssertionError("unapproved compiled policy must never dispatch")

    # A critical multi-repo contract: a possibly effected write can be
    # reconciled by a precompiled qualified observation, without a new LLM
    # proposal or a blind replay of that effect.
    uncertain = Effect("send", (("ready", ("done", "pending")),), authorized=True)
    reconcile = Effect(
        "reconcile", (("pending", ("done",)),), authorized=True,
    )
    readback = Probe(
        "trusted.readback",
        (("done", "done"), ("pending", "pending")),
        trusted=True,
    )
    recovery_kwargs = dict(
        possible_states=frozenset({"ready"}),
        goal_states=frozenset({"done"}),
        safe_states=frozenset({"ready", "done", "pending"}),
        effects=(uncertain, reconcile),
        probes=(readback,), max_steps=3,
    )
    recovery_plan = synthesize(**recovery_kwargs)
    assert recovery_plan is not None
    assert_structurally_safe(recovery_plan, **recovery_kwargs)
    for observed in ("done", "pending"):
        recovery_cursor = ContingentPolicyCursor(
            recovery_plan.as_dict(), binding,
            authorize_effect=lambda _binding, name: name in {"send", "reconcile"},
            qualify_probe=lambda _binding, name: name == "trusted.readback",
        )
        assert recovery_cursor.next_step(binding).name == "send"
        recovery_cursor.resolve_effect(
            binding, effect_name="send", result="unknown",
            independent_readback=False,
        )
        assert recovery_cursor.next_step(binding).name == "trusted.readback"
        recovery_cursor.observe(
            binding, probe_name="trusted.readback",
            observed_label=observed, independent_readback=True,
        )
        if observed == "pending":
            assert recovery_cursor.next_step(binding).name == "reconcile"
            assert recovery_cursor.next_step(binding).kind == "blocked"
            recovery_cursor.resolve_effect(
                binding, effect_name="reconcile", result="verified",
                independent_readback=True,
            )
        assert recovery_cursor.next_step(binding).kind == "done"

    print("Experimental BAA->AIOS contract: two action branches, unknown-effect readback/recovery, no blind replay, live authority OK")


if __name__ == "__main__":
    main()
