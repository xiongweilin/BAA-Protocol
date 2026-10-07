"""Exact binding contract for concrete exposure declarations and joint-risk terms.

Structural v1 composes exposure bounds by risk-factor identity using a frozen
pairwise interaction rule. Concrete exposure metrics do not imply a risk-factor
assignment. This module keeps those obligations separate and fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .exposure_bridge import ExposureMetricDeclaration


PAIRWISE_SHARED_FACTOR_MIN_V1 = "pairwise-shared-factor-min-v1"


@dataclass(frozen=True)
class RiskFactorDeclaration:
    proposal_id: str
    exposure_metric_id: str
    risk_factor_id: str
    joint_risk_functional_id: str = PAIRWISE_SHARED_FACTOR_MIN_V1


@dataclass(frozen=True)
class BoundRiskTerm:
    proposal_id: str
    exposure_metric_id: str
    exposure_bound: int
    risk_factor_id: str
    joint_risk_functional_id: str


@dataclass(frozen=True)
class RiskBindingAssessment:
    established: bool
    term: BoundRiskTerm | None
    reason: str


def bind_risk_term(
    exposure: ExposureMetricDeclaration,
    risk: RiskFactorDeclaration,
) -> RiskBindingAssessment:
    """Bind one concrete exposure declaration to one joint-risk term."""

    if exposure.exposure_bound < 0:
        raise ValueError("exposure_bound must be non-negative")
    if exposure.proposal_id != risk.proposal_id:
        return RiskBindingAssessment(
            False,
            None,
            "risk-factor proposal identity does not match exposure declaration",
        )
    if exposure.metric_id != risk.exposure_metric_id:
        return RiskBindingAssessment(
            False,
            None,
            "risk-factor metric identity does not match exposure declaration",
        )
    factor = risk.risk_factor_id.strip()
    if not factor:
        return RiskBindingAssessment(False, None, "risk factor is empty")
    if risk.joint_risk_functional_id != PAIRWISE_SHARED_FACTOR_MIN_V1:
        return RiskBindingAssessment(
            False,
            None,
            "joint-risk functional identity is not supported by this bridge version",
        )

    return RiskBindingAssessment(
        True,
        BoundRiskTerm(
            proposal_id=exposure.proposal_id,
            exposure_metric_id=exposure.metric_id,
            exposure_bound=exposure.exposure_bound,
            risk_factor_id=factor,
            joint_risk_functional_id=risk.joint_risk_functional_id,
        ),
        "exact exposure/risk-factor binding established",
    )


def declared_joint_risk(
    terms: Iterable[BoundRiskTerm],
    *,
    interaction_penalty: int,
) -> int:
    """Evaluate the same pairwise shared-factor rule used by structural v1.

    This function reproduces the declared functional after exact term binding.
    It does not establish that the functional is calibrated to real-world harm.
    """

    if interaction_penalty < 0:
        raise ValueError("interaction_penalty must be non-negative")
    chosen = list(terms)
    seen_proposals: set[str] = set()
    metric_ids: set[str] = set()
    for term in chosen:
        if not term.proposal_id.strip():
            raise ValueError("risk term proposal identity must be non-empty")
        if term.proposal_id in seen_proposals:
            raise ValueError("duplicate proposal identity in joint-risk terms")
        seen_proposals.add(term.proposal_id)
        if not term.exposure_metric_id.strip():
            raise ValueError("risk term exposure metric must be non-empty")
        metric_ids.add(term.exposure_metric_id)
        if term.exposure_bound < 0:
            raise ValueError("exposure_bound must be non-negative")
        if term.joint_risk_functional_id != PAIRWISE_SHARED_FACTOR_MIN_V1:
            raise ValueError("unsupported joint-risk functional")
        if not term.risk_factor_id.strip():
            raise ValueError("risk factor must be non-empty")
    if len(metric_ids) > 1:
        raise ValueError(
            "incompatible exposure metrics cannot share one joint-risk sum"
        )

    total = sum(term.exposure_bound for term in chosen)
    for index, left in enumerate(chosen):
        for right in chosen[index + 1 :]:
            if left.risk_factor_id == right.risk_factor_id:
                total += interaction_penalty * min(
                    left.exposure_bound,
                    right.exposure_bound,
                )
    return total


__all__ = [
    "PAIRWISE_SHARED_FACTOR_MIN_V1",
    "BoundRiskTerm",
    "RiskBindingAssessment",
    "RiskFactorDeclaration",
    "bind_risk_term",
    "declared_joint_risk",
]
