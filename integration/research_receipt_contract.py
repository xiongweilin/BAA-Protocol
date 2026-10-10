"""Model-relative BAA -> receipt-enforced AIOS staging contract.

Uses a FIXTURE receipt verifier, not protected product evidence. No provider
writes, production permissions, long-running observer or real outcome claim.
"""
from __future__ import annotations

from dataclasses import replace

from administrative_orchestrator.contingent_execution import (
    CaseBinding,
    ContingentPolicyCursor,
    ContingentPolicyViolation,
    EvidenceReceipt,
)
from baa_protocol.contingent_policy import (
    Effect,
    Probe,
    assert_structurally_safe,
    synthesize,
)

BIND = CaseBinding("fixture:no-runtime-dispatch", 2, 3)
SOURCE = "fixture:independent-receipt-store"


def receipt(kind: str, step: str, disposition: str, identity: str = ""):
    return EvidenceReceipt(
        binding=BIND, kind=kind, step_name=step,
        disposition=disposition, evidence_ref=f"receipt:{kind}:{step}:{disposition}",
        source_ref=SOURCE, effect_identity=identity,
    )


def verified(r: EvidenceReceipt) -> bool:
    # An independently protected source would be required in production.
    return (
        r.source_ref == SOURCE
        and r.evidence_ref == f"receipt:{r.kind}:{r.step_name}:{r.disposition}"
        and r.binding == BIND
    )


def make_cursor(plan: dict, identities: dict[str, str]) -> ContingentPolicyCursor:
    return ContingentPolicyCursor(
        plan, BIND,
        authorize_effect=lambda _binding, name: name in identities,
        qualify_probe=lambda _binding, name: name in {"probe.subject", "probe.readback"},
        verify_receipt=verified, effect_identities=identities,
    )


def main() -> None:
    states = frozenset({"left", "right"})
    safe = states | frozenset({"goal"})
    effects = (
        Effect("iam.a", (("left", ("goal",)),), authorized=True),
        Effect("iam.b", (("right", ("goal",)),), authorized=True),
    )
    probes = (
        Probe("probe.subject", (("left", "a"), ("right", "b")), trusted=True),
    )
    inputs = dict(
        possible_states=states, goal_states=frozenset({"goal"}),
        safe_states=safe, effects=effects, probes=probes, max_steps=2,
    )
    policy = synthesize(**inputs)
    assert policy is not None and policy.kind == "probe"
    assert_structurally_safe(policy, **inputs)

    identities = {"iam.a": "durable:iam.a:v1", "iam.b": "durable:iam.b:v1"}
    for observed, effect in (("a", "iam.a"), ("b", "iam.b")):
        cursor = make_cursor(policy.as_dict(), identities)
        assert cursor.next_step(BIND).name == "probe.subject"
        cursor.observe_with_receipt(
            BIND, probe_name="probe.subject",
            receipt=receipt("probe", "probe.subject", observed),
        )
        assert cursor.next_step(BIND).name == effect
        cursor.resolve_effect_with_receipt(
            BIND, effect_name=effect,
            receipt=receipt("effect", effect, "verified", identities[effect]),
        )
        assert cursor.next_step(BIND).kind == "done"

    # Caller-controlled "independent" booleans cannot bypass strict mode.
    forged = make_cursor(policy.as_dict(), identities)
    forged.next_step(BIND)
    try:
        forged.observe(
            BIND, probe_name="probe.subject", observed_label="a",
            independent_readback=True,
        )
    except ContingentPolicyViolation:
        assert forged.next_step(BIND).kind == "blocked"
    else:
        raise AssertionError("caller boolean bypassed receipt enforcement")

    # Correctly formatted but effect-rebound receipt cannot advance.
    forged = make_cursor(
        {"kind": "effect", "name": "iam.a", "next": {"kind": "done"}},
        identities,
    )
    forged.next_step(BIND)
    try:
        forged.resolve_effect_with_receipt(
            BIND, effect_name="iam.a",
            receipt=replace(
                receipt("effect", "iam.a", "verified", identities["iam.a"]),
                effect_identity="durable:wrong-effect",
            ),
        )
    except ContingentPolicyViolation:
        assert forged.next_step(BIND).kind == "blocked"
    else:
        raise AssertionError("rebound durable effect identity was accepted")

    print("Synthetic BAA->AIOS receipt contract: 2 branches, no bool bypass, no rebound effect, NO provider writes")


if __name__ == "__main__":
    main()
