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


MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1 = "managed-subject-state-change-count-v1"


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



@dataclass(frozen=True)
class ExposureMetricDeclaration:
    """Proposal-side declaration of the concrete metric behind an abstract bound."""

    proposal_id: str
    metric_id: str
    declared_subject_ref: str
    exposure_bound: int


@dataclass(frozen=True)
class ManagedSubjectStateChangeMeasurement:
    """Closed-world measurement for the frozen managed-subject projection."""

    proposal_id: str
    metric_id: str
    declared_subject_ref: str
    observed_postcondition: Mapping[str, object]
    managed_subject_count_before: int
    managed_subject_count_after: int
    changed_subject_refs: tuple[str, ...]
    scope_complete: bool


def assess_metric_bound(
    declaration: ExposureMetricDeclaration,
    measurement: ManagedSubjectStateChangeMeasurement,
) -> ExposureAssessment:
    """Bind a concrete acceptance measurement to one declared exposure bound.

    This function does not decide that the metric is the correct real-world risk
    quantity. It only prevents a concrete measurement from being used for
    settlement under a different proposal, metric, subject, or bound semantics.
    """

    if declaration.exposure_bound < 0:
        raise ValueError("exposure_bound must be non-negative")
    proposal_id = declaration.proposal_id.strip()
    metric_id = declaration.metric_id.strip()
    subject_ref = declaration.declared_subject_ref.strip()
    if not proposal_id:
        raise ValueError("proposal_id must be non-empty")
    if not metric_id:
        raise ValueError("metric_id must be non-empty")
    if not subject_ref:
        raise ValueError("declared_subject_ref must be non-empty")

    if measurement.proposal_id != proposal_id:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="measurement proposal identity does not match declaration",
        )
    if measurement.metric_id != metric_id:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="measurement metric identity does not match declaration",
        )
    if metric_id != MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="measurement metric is not supported by this bridge version",
        )
    if measurement.declared_subject_ref != subject_ref:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="measurement subject identity does not match declaration",
        )
    if (
        measurement.managed_subject_count_before < 0
        or measurement.managed_subject_count_after < 0
    ):
        raise ValueError("managed subject counts must be non-negative")
    observed_subject = measurement.observed_postcondition.get("subject_ref")
    if observed_subject is not None and str(observed_subject) != subject_ref:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="measurement read-back subject does not match declaration",
        )
    if not measurement.scope_complete:
        return ExposureAssessment(
            established=False,
            realized_exposure=None,
            reason="managed-subject measurement is not scope-complete",
        )

    changed = {
        str(item).strip()
        for item in measurement.changed_subject_refs
        if str(item).strip()
    }
    realized = len(changed)

    if realized > declaration.exposure_bound:
        return ExposureAssessment(
            established=False,
            realized_exposure=realized,
            reason=(
                f"realized metric exposure {realized} exceeds declared "
                f"bound {declaration.exposure_bound}"
            ),
        )

    outside = changed - {subject_ref}
    if outside:
        return ExposureAssessment(
            established=False,
            realized_exposure=realized,
            reason="managed-subject measurement changed subjects outside declared scope",
        )

    return ExposureAssessment(
        established=True,
        realized_exposure=realized,
        reason="exact metric/subject binding established within declared bound",
    )

def realized_exposure_for_settlement(assessment: ExposureAssessment) -> int:
    """Return a settlement value only for an established bridge."""

    if not assessment.established or assessment.realized_exposure is None:
        raise ValueError("exposure bridge is not established")
    return assessment.realized_exposure


__all__ = [
    "MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1",
    "ExposureAssessment",
    "ExposureMetricDeclaration",
    "ManagedSubjectStateChangeMeasurement",
    "SubjectScopeEvidence",
    "assess_metric_bound",
    "assess_subject_scope_exposure",
    "evidence_from_target_readback",
    "realized_exposure_for_settlement",
]
