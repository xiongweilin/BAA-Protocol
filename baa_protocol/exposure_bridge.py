"""Falsifiable exposure-bound bridge contract for reality-side evidence.

Structural v1 assumes that realized exposure used for settlement does not
exceed the declared admission bound. Target postcondition read-back alone
cannot establish that assumption because it does not rule out collateral
effects on other subjects.

This module defines the minimum evidence shape needed to turn a target-scoped
observation into a subject-scope exposure measurement. It intentionally fails
closed when coverage is incomplete.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SubjectScopeEvidence:
    """Evidence for the set of subjects affected by one logical effect.

    scope_complete means the producer attests that affected_subject_refs is
    complete for the declared exposure metric, not merely a sample of the
    intended target.
    """

    declared_subject_ref: str
    observed_postcondition: Mapping[str, object]
    affected_subject_refs: tuple[str, ...] | None = None
    scope_complete: bool = False


@dataclass(frozen=True)
class ExposureAssessment:
    established: bool
    realized_exposure: int | None
    reason: str


def evidence_from_target_readback(
    *,
    declared_subject_ref: str,
    observed_postcondition: Mapping[str, object],
) -> SubjectScopeEvidence:
    """Represent today's target-only product read-back honestly."""

    return SubjectScopeEvidence(
        declared_subject_ref=declared_subject_ref,
        observed_postcondition=dict(observed_postcondition),
        affected_subject_refs=None,
        scope_complete=False,
    )


def assess_subject_scope_exposure(
    evidence: SubjectScopeEvidence,
    *,
    exposure_bound: int,
) -> ExposureAssessment:
    """Assess a concrete subject-count exposure bound.

    The metric is the number of distinct product subjects affected by the
    logical effect. A complete evidence producer may report zero or one
    declared subject for a bound of one. Any extra subject is an explicit
    falsification, not something to clamp away.
    """

    if exposure_bound < 0:
        raise ValueError("exposure_bound must be non-negative")
    declared = evidence.declared_subject_ref.strip()
    if not declared:
        raise ValueError("declared_subject_ref must be non-empty")

    observed_subject = evidence.observed_postcondition.get("subject_ref")
    if observed_subject is not None and str(observed_subject) != declared:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="target read-back subject does not match declared subject",
        )

    if not evidence.scope_complete or evidence.affected_subject_refs is None:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason=(
                "target read-back is scope-incomplete; collateral subject "
                "effects are not measured"
            ),
        )

    affected = {
        str(item).strip()
        for item in evidence.affected_subject_refs
        if str(item).strip()
    }
    realized = len(affected)

    if realized > exposure_bound:
        return ExposureAssessment(
            established=False,
            realized_exposure=realized,
            reason=(
                f"realized subject exposure {realized} exceeds declared "
                f"bound {exposure_bound}"
            ),
        )

    outside = affected - {declared}
    if outside:
        return ExposureAssessment(
            established=False,
            realized_exposure=realized,
            reason=(
                "complete exposure evidence includes subjects outside the "
                "declared target"
            ),
        )

    return ExposureAssessment(
        established=True,
        realized_exposure=realized,
        reason="complete subject-scope exposure evidence is within bound",
    )


def realized_exposure_for_settlement(assessment: ExposureAssessment) -> int:
    """Return a settlement value only for an established bridge."""

    if not assessment.established or assessment.realized_exposure is None:
        raise ValueError("exposure bridge is not established")
    return assessment.realized_exposure


__all__ = [
    "ExposureAssessment",
    "SubjectScopeEvidence",
    "assess_subject_scope_exposure",
    "evidence_from_target_readback",
    "realized_exposure_for_settlement",
]
