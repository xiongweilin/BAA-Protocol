"""Concrete BAA reference model for the employee-offboarding domain.

This module is an executable specification aid derived from the AIOS
Administrative offboarding semantics. It is not an implementation or
certification of AIOS.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .exposure_bridge import (
    MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
    ExposureMetricDeclaration,
)
from .model import Decision
from .risk_bridge import RiskFactorDeclaration


class EffectKnowledge(str, Enum):
    RESERVED = "reserved"
    POSSIBLY_EFFECTED = "possibly_effected"
    VERIFIED_EFFECTED = "verified_effected"
    VERIFIED_NO_EFFECT = "verified_no_effect"


@dataclass(frozen=True)
class OffboardingObligation:
    obligation_id: str
    case_id: str
    authority_epoch: int
    governance_basis_id: str
    subject_ref: str
    target_system: str
    operation: str
    expected_postcondition: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class OffboardingProposal:
    proposal_id: str
    obligation_id: str
    case_id: str
    authority_epoch: int
    governance_basis_id: str
    subject_ref: str
    target_system: str
    operation: str
    state_version: int
    effective_at: int
    expires_at: int
    request_identity: str
    verification_available: bool = True
    bridge_valid: bool = True
    protected_source_target: bool = False


OFFBOARDING_EXPOSURE_BOUNDS_V1 = {
    ("hris", "employee.deactivate"): (
        MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
        1,
    ),
    ("iam", "identity.disable"): (
        MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
        1,
    ),
    ("iam", "sessions.revoke"): (
        MANAGED_SUBJECT_STATE_CHANGE_METRIC_V1,
        1,
    ),
}


def exposure_declaration_for_proposal(
    proposal: OffboardingProposal,
) -> ExposureMetricDeclaration:
    """Return the frozen v1 exposure declaration for one offboarding proposal.

    This is a declaration of the metric consumed by the reference structural
    accounting layer. It is not evidence that a reality-side measurement
    source has established the metric for this proposal.
    """

    key = (proposal.target_system, proposal.operation)
    try:
        metric_id, exposure_bound = OFFBOARDING_EXPOSURE_BOUNDS_V1[key]
    except KeyError as exc:
        raise ValueError(
            "offboarding proposal has no frozen exposure declaration"
        ) from exc
    subject_ref = proposal.subject_ref.strip()
    if not subject_ref:
        raise ValueError("offboarding exposure declaration requires a subject")
    return ExposureMetricDeclaration(
        proposal_id=proposal.proposal_id,
        metric_id=metric_id,
        declared_subject_ref=subject_ref,
        exposure_bound=exposure_bound,
    )


OFFBOARDING_RISK_FACTOR_IDS_V1: dict[tuple[str, str], str] = {}


def risk_factor_declaration_for_proposal(
    proposal: OffboardingProposal,
) -> RiskFactorDeclaration:
    """Return a calibrated risk-factor declaration when one exists.

    v1 intentionally has no offboarding risk-factor calibration. Exposure
    metric declarations therefore cannot yet be projected into the structural
    joint-risk functional.
    """

    key = (proposal.target_system, proposal.operation)
    risk_factor_id = OFFBOARDING_RISK_FACTOR_IDS_V1.get(key)
    if risk_factor_id is None:
        raise ValueError(
            "offboarding proposal has no calibrated risk-factor declaration"
        )
    exposure = exposure_declaration_for_proposal(proposal)
    return RiskFactorDeclaration(
        proposal_id=proposal.proposal_id,
        exposure_metric_id=exposure.metric_id,
        risk_factor_id=risk_factor_id,
    )


@dataclass(frozen=True)
class OffboardingCapability:
    capability_id: str
    proposal_id: str
    obligation_id: str
    case_id: str
    authority_epoch: int
    subject_ref: str
    target_system: str
    operation: str
    state_version: int
    not_before: int
    expires_at: int
    request_identity: str


@dataclass(frozen=True)
class OffboardingAdmission:
    decision: Decision
    reason: str
    capability: Optional[OffboardingCapability] = None


@dataclass
class EffectState:
    obligation_id: str
    knowledge: EffectKnowledge


class OffboardingKernel:
    """Minimal exact-scope offboarding admission and execution kernel."""

    ALLOWED_EXTERNAL_OPERATIONS = frozenset(
        {
            ("hris", "employee.deactivate"),
            ("iam", "identity.disable"),
            ("iam", "sessions.revoke"),
        }
    )

    def __init__(
        self,
        *,
        case_id: str,
        authority_epoch: int,
        state_version: int,
        obligations: tuple[OffboardingObligation, ...],
        unresolved_limit: int = 1,
    ) -> None:
        if unresolved_limit < 0:
            raise ValueError("unresolved_limit must be non-negative")
        self.case_id = case_id
        self.authority_epoch = authority_epoch
        self.state_version = state_version
        self.unresolved_limit = unresolved_limit
        self.obligations = {item.obligation_id: item for item in obligations}
        self.capabilities: Dict[str, OffboardingCapability] = {}
        self.effects: Dict[str, EffectState] = {}

    @property
    def unresolved_count(self) -> int:
        return sum(
            state.knowledge is EffectKnowledge.POSSIBLY_EFFECTED
            for state in self.effects.values()
        )

    def _obligation(self, proposal: OffboardingProposal) -> OffboardingObligation | None:
        return self.obligations.get(proposal.obligation_id)

    def admit(self, proposal: OffboardingProposal, *, now: int) -> OffboardingAdmission:
        obligation = self._obligation(proposal)
        if obligation is None:
            return OffboardingAdmission(Decision.DENY, "unknown obligation")

        if proposal.protected_source_target:
            return OffboardingAdmission(
                Decision.DENY,
                "guarantee-channel isolation forbids the target",
            )

        if proposal.case_id != self.case_id or proposal.case_id != obligation.case_id:
            return OffboardingAdmission(Decision.DENY, "case mismatch")

        if (
            proposal.authority_epoch != self.authority_epoch
            or proposal.authority_epoch != obligation.authority_epoch
        ):
            return OffboardingAdmission(Decision.DENY, "stale authority epoch")

        if proposal.state_version != self.state_version:
            return OffboardingAdmission(Decision.DENY, "stale state version")

        if proposal.governance_basis_id != obligation.governance_basis_id:
            return OffboardingAdmission(Decision.DENY, "governance basis mismatch")

        if proposal.subject_ref != obligation.subject_ref:
            return OffboardingAdmission(Decision.DENY, "subject mismatch")

        if (
            proposal.target_system != obligation.target_system
            or proposal.operation != obligation.operation
        ):
            return OffboardingAdmission(Decision.DENY, "operation mismatch")

        if (proposal.target_system, proposal.operation) not in self.ALLOWED_EXTERNAL_OPERATIONS:
            return OffboardingAdmission(Decision.DENY, "operation outside BAA domain")

        if now < proposal.effective_at:
            return OffboardingAdmission(Decision.HOLD, "effective time not reached")

        if now > proposal.expires_at:
            return OffboardingAdmission(Decision.DENY, "proposal expired")

        if not proposal.verification_available:
            return OffboardingAdmission(Decision.HOLD, "verification unavailable")

        if not proposal.bridge_valid:
            return OffboardingAdmission(Decision.HOLD, "semantic bridge unavailable")

        existing = self.effects.get(proposal.obligation_id)
        if existing is not None:
            if existing.knowledge is EffectKnowledge.POSSIBLY_EFFECTED:
                return OffboardingAdmission(
                    Decision.HOLD,
                    "same obligation has unresolved external effect",
                )
            if existing.knowledge is EffectKnowledge.VERIFIED_EFFECTED:
                return OffboardingAdmission(
                    Decision.DENY,
                    "obligation already verified fulfilled",
                )
            if existing.knowledge is EffectKnowledge.RESERVED:
                return OffboardingAdmission(
                    Decision.DENY,
                    "obligation already has an admitted capability",
                )

        if self.unresolved_count >= self.unresolved_limit:
            return OffboardingAdmission(
                Decision.HOLD,
                "unresolved-effect limit reached",
            )

        capability = OffboardingCapability(
            capability_id=f"offboarding:{proposal.proposal_id}",
            proposal_id=proposal.proposal_id,
            obligation_id=proposal.obligation_id,
            case_id=proposal.case_id,
            authority_epoch=proposal.authority_epoch,
            subject_ref=proposal.subject_ref,
            target_system=proposal.target_system,
            operation=proposal.operation,
            state_version=proposal.state_version,
            not_before=proposal.effective_at,
            expires_at=proposal.expires_at,
            request_identity=proposal.request_identity,
        )
        self.capabilities[capability.capability_id] = capability
        self.effects[proposal.obligation_id] = EffectState(
            obligation_id=proposal.obligation_id,
            knowledge=EffectKnowledge.RESERVED,
        )
        return OffboardingAdmission(Decision.ADMIT, "admitted", capability)

    def execute(
        self,
        capability: OffboardingCapability,
        *,
        now: int,
        case_id: str,
        authority_epoch: int,
        state_version: int,
        subject_ref: str,
        target_system: str,
        operation: str,
        request_identity: str,
    ) -> None:
        known = self.capabilities.get(capability.capability_id)
        if known != capability:
            raise PermissionError("unknown or altered capability")
        if now < capability.not_before:
            raise PermissionError("effect not yet effective")
        if now > capability.expires_at:
            raise PermissionError("capability expired")
        if case_id != capability.case_id:
            raise PermissionError("case mismatch")
        if authority_epoch != self.authority_epoch or authority_epoch != capability.authority_epoch:
            raise PermissionError("stale authority epoch")
        if state_version != self.state_version or state_version != capability.state_version:
            raise PermissionError("stale state version")
        if subject_ref != capability.subject_ref:
            raise PermissionError("subject mismatch")
        if target_system != capability.target_system:
            raise PermissionError("target-system mismatch")
        if operation != capability.operation:
            raise PermissionError("operation mismatch")
        if request_identity != capability.request_identity:
            raise PermissionError("request identity mismatch")

        state = self.effects.get(capability.obligation_id)
        if state is None or state.knowledge is not EffectKnowledge.RESERVED:
            raise PermissionError("capability is not executable")

        state.knowledge = EffectKnowledge.POSSIBLY_EFFECTED

    def verify(
        self,
        obligation_id: str,
        *,
        observed_postcondition: dict[str, object],
    ) -> bool:
        obligation = self.obligations[obligation_id]
        state = self.effects.get(obligation_id)
        if state is None or state.knowledge is not EffectKnowledge.POSSIBLY_EFFECTED:
            raise ValueError("obligation is not awaiting verification")

        expected = dict(obligation.expected_postcondition)
        satisfied = all(observed_postcondition.get(key) == value for key, value in expected.items())
        state.knowledge = (
            EffectKnowledge.VERIFIED_EFFECTED
            if satisfied
            else EffectKnowledge.VERIFIED_NO_EFFECT
        )
        return satisfied

    def observation_unavailable(self, obligation_id: str) -> None:
        """Preserve unresolved effect knowledge when read-back is unavailable."""
        state = self.effects.get(obligation_id)
        if state is None or state.knowledge is not EffectKnowledge.POSSIBLY_EFFECTED:
            raise ValueError("obligation is not awaiting verification")
        # Deliberately no state collapse.

    def update_authority_epoch(self, new_epoch: int) -> None:
        if new_epoch <= self.authority_epoch:
            raise ValueError("authority epoch must advance")
        self.authority_epoch = new_epoch

    def update_state_version(self, new_version: int) -> None:
        if new_version <= self.state_version:
            raise ValueError("state version must advance")
        self.state_version = new_version

    def externally_complete(self) -> bool:
        required_ids = set(self.obligations)
        return bool(required_ids) and all(
            self.effects.get(obligation_id) is not None
            and self.effects[obligation_id].knowledge is EffectKnowledge.VERIFIED_EFFECTED
            for obligation_id in required_ids
        )
