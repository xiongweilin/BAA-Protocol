"""Predeclared synthetic bridge-ablation checks; NOT a real-model advantage study.

Each case starts with a locally valid BAA policy and then changes exactly one
external assumption. If the independent checker still accepts the old policy
under the adversarial model, this script FAILS. It does not assert the changed
model is an empirical description of reality.
"""
from __future__ import annotations

import json
from dataclasses import replace

from baa_protocol.contingent_policy import (
    Effect, Probe, assert_structurally_safe, synthesize,
)


def _case_inputs() -> list[tuple[str, dict, dict]]:
    common = dict(
        possible_states=frozenset({"ready"}),
        goal_states=frozenset({"done"}),
        safe_states=frozenset({"ready", "done"}),
        effects=(Effect("commit", (("ready", ("done",)),), authorized=True),),
        probes=(),
        max_steps=1,
    )
    # A formerly omitted possible actual world can invalidate the plan.
    omitted = {
        **common, "possible_states": frozenset({"ready", "hidden"}),
        "safe_states": common["safe_states"] | {"hidden"},
    }
    # Declared effects can underapproximate provider outcomes.
    unsafe = {
        **common, "effects": (
            replace(common["effects"][0], outcomes=(("ready", ("done", "unsafe")),)),
        ),
    }
    # Authorization can change between compilation and runtime admission.
    revoked = {
        **common, "effects": (
            replace(common["effects"][0], authorized=False),
        ),
    }
    # Even an effect that remains in the safe set can leave goal status unknown.
    pending = {
        **common, "safe_states": common["safe_states"] | {"pending"},
        "effects": (
            replace(common["effects"][0], outcomes=(("ready", ("done", "pending")),)),
        ),
    }
    branch = dict(
        possible_states=frozenset({"left", "right"}),
        goal_states=frozenset({"done"}),
        safe_states=frozenset({"left", "right", "done"}),
        effects=(
            Effect("do-left", (("left", ("done",)),), authorized=True),
            Effect("do-right", (("right", ("done",)),), authorized=True),
        ),
        probes=(Probe("inspect", (("left", "l"), ("right", "r")), trusted=True),),
        max_steps=2,
    )
    untrusted = {
        **branch, "probes": (
            replace(branch["probes"][0], trusted=False),
        ),
    }
    return [
        ("unmodeled_initial_world", common, omitted),
        ("underreported_unsafe_successor", common, unsafe),
        ("revoked_effect_authority", common, revoked),
        ("unobserved_pending_effect", common, pending),
        ("unqualified_readback", branch, untrusted),
    ]


def run() -> dict[str, object]:
    rows = []
    for name, declared, adversarial in _case_inputs():
        plan = synthesize(**declared)
        if plan is None:
            raise AssertionError(f"{name}: no initial declared-world solution")
        assert_structurally_safe(plan, **declared)
        try:
            assert_structurally_safe(plan, **adversarial)
        except ValueError as exc:
            rows.append({
                "case": name, "declared_model_accepts": True,
                "adversarial_model_accepts": False,
                "rejection": str(exc),
            })
        else:
            raise AssertionError(f"{name}: changed assumption incorrectly accepted")
    return {
        "evidence_class": "synthetic_model_perturbation_only",
        "not_established": [
            "external model completeness", "deployed authorization integrity",
            "human time savings", "comparative real-model performance",
        ],
        "expected_negative_cases": len(rows),
        "caught_model_perturbations": len(rows),
        "cases": rows,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
