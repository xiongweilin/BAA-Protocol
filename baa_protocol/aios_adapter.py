"""Thin compatibility adapter from AIOS Administrative obligations to BAA.

The module intentionally avoids importing AIOS. It consumes objects exposing
the documented Administrative obligation attributes, so BAA's core remains
independent from the source repository.
"""

from __future__ import annotations

from typing import Any

from .offboarding import OffboardingObligation


AIOS_RUNTIME_CAPABILITY_BY_EFFECT = {
    ("hris", "employee.deactivate"): "administrative.hris.employee.deactivate.v1",
    ("iam", "identity.disable"): "administrative.iam.identity.disable.v1",
    ("iam", "sessions.revoke"): "administrative.iam.sessions.revoke.v1",
}

# Fields expected from AIOS's reality-side verification result for the first
# offboarding experiment. Payload provenance is deliberately not collapsed
# into the postcondition because BAA treats it as separate evidence.
_VERIFICATION_FIELDS = frozenset(
    {
        "target_system",
        "operation",
        "subject_ref",
        "active",
        "enabled",
        "active_sessions",
    }
)


def project_aios_external_obligation(item: Any) -> OffboardingObligation:
    """Project one AIOS external-effect obligation into BAA's narrow model.

    The caller is responsible for passing only external-effect-verified
    obligations. The function validates the covered effect pair and retains
    only fields that belong to the first experiment's verification interface.
    """
    target_system = str(item.target_system)
    operation = str(item.required_operation)
    pair = (target_system, operation)
    if pair not in AIOS_RUNTIME_CAPABILITY_BY_EFFECT:
        raise ValueError(f"AIOS effect is outside the BAA offboarding domain: {pair!r}")

    expected = dict(item.expected_postcondition)
    postcondition = tuple(
        sorted(
            (key, value)
            for key, value in expected.items()
            if key in _VERIFICATION_FIELDS
        )
    )
    if not postcondition:
        raise ValueError("AIOS obligation has no covered verification postcondition")

    return OffboardingObligation(
        obligation_id=str(item.obligation_id),
        case_id=str(item.case_id),
        authority_epoch=int(item.authority_epoch),
        governance_basis_id=str(item.governance_basis_id),
        subject_ref=str(item.subject_ref),
        target_system=target_system,
        operation=operation,
        expected_postcondition=postcondition,
    )


def runtime_capability_for(obligation: OffboardingObligation) -> str:
    try:
        return AIOS_RUNTIME_CAPABILITY_BY_EFFECT[
            (obligation.target_system, obligation.operation)
        ]
    except KeyError as exc:
        raise ValueError("obligation is outside the AIOS runtime capability map") from exc
