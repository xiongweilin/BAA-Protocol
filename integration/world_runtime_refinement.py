"""Finite World Runtime boundary refinement checks.

These helpers make the second concrete refinement layer explicit without
importing AIOS into BAA core modules. Integration tests pass pinned AIOS
objects/views into these functions.

The checks are deliberately narrower than a complete-mediation proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class RuntimeScopeBinding:
    capability: str
    resource: str
    subject_version_refs: tuple[str, ...]
    idempotency_key: str
    authorization_id: str
    principal: str
    actor_ref: str
    effect_class: str

    @classmethod
    def from_request(cls, request: Any) -> "RuntimeScopeBinding":
        resource = str(
            getattr(request, "resource", None)
            or getattr(request, "resource_ref", None)
            or ""
        )
        return cls(
            capability=str(getattr(request, "capability", "") or ""),
            resource=resource,
            subject_version_refs=tuple(
                str(item)
                for item in (getattr(request, "subject_version_refs", ()) or ())
            ),
            idempotency_key=str(
                getattr(request, "idempotency_key", "") or ""
            ),
            authorization_id=str(
                getattr(request, "authorization_id", "") or ""
            ),
            principal=str(
                getattr(request, "principal", None)
                or getattr(request, "actor_ref", None)
                or ""
            ),
            actor_ref=str(getattr(request, "actor_ref", "") or ""),
            effect_class=str(getattr(request, "effect_class", "") or ""),
        )


def assert_strict_effect_rule(rule: Any) -> None:
    """Require the Runtime rule needed to refine a narrow BAA capability."""
    if not bool(getattr(rule, "authorization_required", False)):
        raise AssertionError("runtime effect rule does not require authorization")
    if not bool(getattr(rule, "resource_required", False)):
        raise AssertionError("runtime effect rule does not require an explicit resource")
    if not bool(getattr(rule, "version_required", False)):
        raise AssertionError("runtime effect rule does not require subject version refs")


def assert_scope_binding(
    binding: RuntimeScopeBinding,
    *,
    capability: str,
    resource: str,
    subject_version_refs: Iterable[str],
    idempotency_key: str,
) -> None:
    """Check one effectful Runtime request against the projected BAA scope."""
    if binding.effect_class in {"", "read", "read-only"}:
        raise AssertionError("runtime projection is not reality-changing")
    if not binding.authorization_id:
        raise AssertionError("runtime projection has no authorization binding")
    if not binding.principal:
        raise AssertionError("runtime projection has no principal")
    if not binding.actor_ref:
        raise AssertionError("runtime projection has no actor identity")

    expected_versions = tuple(str(item) for item in subject_version_refs)
    observed = (
        binding.capability,
        binding.resource,
        binding.subject_version_refs,
        binding.idempotency_key,
    )
    expected = (
        capability,
        resource,
        expected_versions,
        idempotency_key,
    )
    if observed != expected:
        raise AssertionError(
            f"runtime scope does not refine projected BAA scope: "
            f"observed={observed!r} expected={expected!r}"
        )


def assert_ambiguous_effect_fenced(view: Mapping[str, Any]) -> None:
    """An effect-unknown Runtime record must not authorize a fresh dispatch."""
    if str(view.get("status", "")) != "ambiguous":
        raise AssertionError("runtime effect is not in ambiguous state")
    if bool(view.get("dispatch_allowed", True)):
        raise AssertionError("ambiguous runtime effect still permits dispatch")
    if bool(view.get("start_allowed", True)):
        raise AssertionError("ambiguous runtime effect still permits a fresh start")
    if int(view.get("dispatch_generation", 0)) <= 0:
        raise AssertionError("ambiguous runtime effect lacks a recorded dispatch generation")


def assert_writer_verifier_separated(
    capability: str,
    providers: Iterable[Any],
) -> None:
    """Require exactly one writer and verifier with distinct credential domains."""
    values = tuple(providers)
    writers = [
        item
        for item in values
        if capability in tuple(getattr(item, "capabilities", ()) or ())
    ]
    verifiers = [
        item
        for item in values
        if f"{capability}.verify"
        in tuple(getattr(item, "capabilities", ()) or ())
    ]
    if len(writers) != 1 or len(verifiers) != 1:
        raise AssertionError(
            "covered runtime capability must have one writer and one verifier"
        )
    writer_domain = str(getattr(writers[0], "credential_domain", "") or "")
    verifier_domain = str(getattr(verifiers[0], "credential_domain", "") or "")
    if not writer_domain or not verifier_domain:
        raise AssertionError("writer/verifier credential domains must be explicit")
    if writer_domain == verifier_domain:
        raise AssertionError("writer and verifier credential domains are not separated")
