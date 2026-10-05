"""Integration-only BAA gate for the pinned AIOS Administrative EffectProvider.

This module imports AIOS intentionally. Core baa_protocol modules remain
independent. The gate demonstrates where BAA can sit on the real execution
boundary: AIOS EffectRecord -> BAA admission -> provider -> read-back.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from administrative_orchestrator.effect_provider import (
    EffectProvider,
    ProviderExecutionResult,
    ProviderExecutionStatus,
    RealityObservation,
)
from administrative_orchestrator.obligations import (
    ObligationFulfillmentKind,
    ObligationRepository,
)
from administrative_orchestrator.service import authoritative_effective_time

from baa_protocol.aios_adapter import project_aios_external_obligation
from baa_protocol.model import Decision
from baa_protocol.offboarding import (
    EffectKnowledge,
    OffboardingKernel,
    OffboardingProposal,
)


class BAAGatedAIOSProvider:
    """Non-bypassable provider wrapper for the covered offboarding effects.

    The wrapper intentionally performs a reality read-back after a successful
    provider call before it releases the next effect under the default
    unresolved_limit=1 policy.
    """

    def __init__(
        self,
        store,
        provider: EffectProvider,
        *,
        now: Callable[[], datetime],
        unresolved_limit: int = 1,
    ) -> None:
        self.store = store
        self.provider = provider
        self.now = now
        self.unresolved_limit = unresolved_limit
        self._kernels: dict[tuple[str, int], OffboardingKernel] = {}
        self._proposal_for_effect: dict[str, str] = {}

    def _kernel(self, effect) -> OffboardingKernel:
        key = (str(effect.case_id), int(effect.authority_epoch))
        case = self.store.get_case(effect.case_id)
        if case is None:
            raise ValueError("administrative case is unavailable")

        existing = self._kernels.get(key)
        if existing is not None:
            # AIOS may advance its local lifecycle version while preserving the
            # same authority epoch and immutable obligation set. Once every
            # ambiguous external effect has been independently resolved, allow
            # the BAA kernel to monotonically follow that controlled progress.
            if (
                case.version > existing.state_version
                and existing.unresolved_count == 0
                and case.status.value == "executing"
            ):
                existing.update_state_version(case.version)
            return existing

        obligation_set = ObligationRepository(self.store).get_current(
            effect.case_id,
            effect.authority_epoch,
        )
        if obligation_set is None:
            raise ValueError("current offboarding obligation set is unavailable")
        external = tuple(
            project_aios_external_obligation(item)
            for item in obligation_set.obligations
            if item.fulfillment_kind
            is ObligationFulfillmentKind.EXTERNAL_EFFECT_VERIFIED
        )
        kernel = OffboardingKernel(
            case_id=str(effect.case_id),
            authority_epoch=effect.authority_epoch,
            state_version=case.version,
            obligations=external,
            unresolved_limit=self.unresolved_limit,
        )
        self._kernels[key] = kernel
        return kernel

    @staticmethod
    def _verification_state(observation: RealityObservation) -> dict[str, object]:
        return dict(observation.state)

    def execute(self, effect, payload: dict[str, Any]) -> ProviderExecutionResult:
        case = self.store.get_case(effect.case_id)
        if case is None:
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.FAILED,
                error="BAA case unavailable",
                retryable=False,
            )
        effective_at = authoritative_effective_time(case)
        if effective_at is None:
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.FAILED,
                error="BAA authoritative effective time unavailable",
                retryable=False,
            )

        kernel = self._kernel(effect)
        # The kernel is created against the current EXECUTING version. If the
        # case advances independently, the capability becomes stale.
        if kernel.state_version != case.version:
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.FAILED,
                error="BAA state version changed",
                retryable=False,
            )

        proposal_id = f"effect:{effect.effect_id}"
        proposal = OffboardingProposal(
            proposal_id=proposal_id,
            obligation_id=str(effect.obligation_id),
            case_id=str(effect.case_id),
            authority_epoch=effect.authority_epoch,
            governance_basis_id=str(effect.governance_basis_id),
            subject_ref=effect.subject_ref,
            target_system=effect.target_system,
            operation=effect.operation,
            state_version=case.version,
            effective_at=int(effective_at.timestamp()),
            expires_at=int((effective_at + timedelta(days=1)).timestamp()),
            request_identity=f"aios-effect:{effect.effect_id}",
            verification_available=True,
            bridge_valid=True,
        )
        now = int(self.now().timestamp())
        admission = kernel.admit(proposal, now=now)
        if admission.decision is not Decision.ADMIT:
            # HOLD certifies that BAA did not release a capability, so no
            # external attempt occurred. Keep it distinct from transport-
            # ambiguous OUTCOME_UNKNOWN.
            status = (
                ProviderExecutionStatus.DEFERRED
                if admission.decision is Decision.HOLD
                else ProviderExecutionStatus.FAILED
            )
            return ProviderExecutionResult(
                status=status,
                error=f"BAA {admission.decision.value}: {admission.reason}",
                retryable=False,
            )

        capability = admission.capability
        assert capability is not None
        kernel.execute(
            capability,
            now=now,
            case_id=str(effect.case_id),
            authority_epoch=effect.authority_epoch,
            state_version=case.version,
            subject_ref=effect.subject_ref,
            target_system=effect.target_system,
            operation=effect.operation,
            request_identity=proposal.request_identity,
        )
        self._proposal_for_effect[str(effect.effect_id)] = proposal_id

        result = self.provider.execute(effect, payload)
        if result.status is not ProviderExecutionStatus.SUCCEEDED:
            # A transport-ambiguous result remains POSSIBLY_EFFECTED. A
            # definitive provider failure is still conservatively unresolved
            # here because the gate itself has not established no effect.
            return result

        observation = self.provider.observe(effect)
        if (
            observation.availability.value != "available"
            or observation.freshness.value != "current"
            or observation.presence.value != "present"
        ):
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.OUTCOME_UNKNOWN,
                provider_ref=result.provider_ref,
                error="BAA post-dispatch read-back unavailable",
                retryable=False,
            )

        verified = kernel.verify(
            str(effect.obligation_id),
            observed_postcondition=self._verification_state(observation),
        )
        if not verified:
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.OUTCOME_UNKNOWN,
                provider_ref=result.provider_ref,
                error="BAA post-dispatch postcondition not verified",
                retryable=False,
            )
        return result

    def observe(self, effect) -> RealityObservation:
        observation = self.provider.observe(effect)
        key = (str(effect.case_id), int(effect.authority_epoch))
        kernel = self._kernels.get(key)
        if kernel is None or effect.obligation_id is None:
            return observation
        state = kernel.effects.get(str(effect.obligation_id))
        if (
            state is not None
            and state.knowledge is EffectKnowledge.POSSIBLY_EFFECTED
            and observation.availability.value == "available"
            and observation.freshness.value == "current"
            and observation.presence.value == "present"
        ):
            kernel.verify(
                str(effect.obligation_id),
                observed_postcondition=self._verification_state(observation),
            )
        return observation
