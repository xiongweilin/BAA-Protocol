import unittest

from baa_protocol.model import Decision
from baa_protocol.offboarding import (
    EffectKnowledge,
    OffboardingKernel,
    OffboardingObligation,
    OffboardingProposal,
)


def obligations() -> tuple[OffboardingObligation, ...]:
    common = dict(
        case_id="case:1",
        authority_epoch=7,
        governance_basis_id="basis:1",
        subject_ref="employee:1",
    )
    return (
        OffboardingObligation(
            obligation_id="obl:hris",
            target_system="hris",
            operation="employee.deactivate",
            expected_postcondition=(("active", False),),
            **common,
        ),
        OffboardingObligation(
            obligation_id="obl:identity",
            target_system="iam",
            operation="identity.disable",
            expected_postcondition=(("enabled", False),),
            **common,
        ),
        OffboardingObligation(
            obligation_id="obl:sessions",
            target_system="iam",
            operation="sessions.revoke",
            expected_postcondition=(("active_sessions", 0),),
            **common,
        ),
    )


def proposal(
    proposal_id: str,
    obligation: OffboardingObligation,
    **overrides,
) -> OffboardingProposal:
    values = dict(
        proposal_id=proposal_id,
        obligation_id=obligation.obligation_id,
        case_id=obligation.case_id,
        authority_epoch=obligation.authority_epoch,
        governance_basis_id=obligation.governance_basis_id,
        subject_ref=obligation.subject_ref,
        target_system=obligation.target_system,
        operation=obligation.operation,
        state_version=3,
        effective_at=100,
        expires_at=200,
        request_identity=f"request:{proposal_id}",
        verification_available=True,
        bridge_valid=True,
        protected_source_target=False,
    )
    values.update(overrides)
    return OffboardingProposal(**values)


class OffboardingDomainTests(unittest.TestCase):
    def kernel(self, *, unresolved_limit: int = 1) -> OffboardingKernel:
        return OffboardingKernel(
            case_id="case:1",
            authority_epoch=7,
            state_version=3,
            obligations=obligations(),
            unresolved_limit=unresolved_limit,
        )

    def test_before_effective_time_holds(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0])

        result = kernel.admit(p, now=99)

        self.assertEqual(result.decision, Decision.HOLD)

    def test_exact_scope_admission(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0])

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.ADMIT)
        self.assertEqual(result.capability.subject_ref, "employee:1")
        self.assertEqual(result.capability.operation, "employee.deactivate")

    def test_wrong_employee_is_denied(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0], subject_ref="employee:2")

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.DENY)

    def test_wrong_operation_is_denied(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0], operation="employee.delete")

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.DENY)

    def test_stale_authority_epoch_is_denied_at_admission(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0], authority_epoch=6)

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.DENY)

    def test_authority_change_invalidates_previously_issued_capability(self):
        kernel = self.kernel()
        result = kernel.admit(proposal("p1", obligations()[0]), now=100)
        capability = result.capability
        assert capability is not None

        kernel.update_authority_epoch(8)

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                now=101,
                case_id="case:1",
                authority_epoch=7,
                state_version=3,
                subject_ref="employee:1",
                target_system="hris",
                operation="employee.deactivate",
                request_identity="request:p1",
            )

    def test_state_version_change_invalidates_capability(self):
        kernel = self.kernel()
        result = kernel.admit(proposal("p1", obligations()[0]), now=100)
        capability = result.capability
        assert capability is not None

        kernel.update_state_version(4)

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                now=101,
                case_id="case:1",
                authority_epoch=7,
                state_version=3,
                subject_ref="employee:1",
                target_system="hris",
                operation="employee.deactivate",
                request_identity="request:p1",
            )

    def test_protected_observation_source_target_is_denied(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0], protected_source_target=True)

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.DENY)

    def test_missing_verification_holds(self):
        kernel = self.kernel()
        p = proposal("p1", obligations()[0], verification_available=False)

        result = kernel.admit(p, now=100)

        self.assertEqual(result.decision, Decision.HOLD)

    def test_unknown_effect_is_not_replayed(self):
        kernel = self.kernel()
        obligation = obligations()[1]
        result = kernel.admit(proposal("p1", obligation), now=100)
        capability = result.capability
        assert capability is not None

        kernel.execute(
            capability,
            now=101,
            case_id="case:1",
            authority_epoch=7,
            state_version=3,
            subject_ref="employee:1",
            target_system="iam",
            operation="identity.disable",
            request_identity="request:p1",
        )
        kernel.observation_unavailable(obligation.obligation_id)

        retry = kernel.admit(proposal("p2", obligation), now=102)

        self.assertEqual(retry.decision, Decision.HOLD)
        self.assertEqual(
            kernel.effects[obligation.obligation_id].knowledge,
            EffectKnowledge.POSSIBLY_EFFECTED,
        )

    def test_unresolved_limit_serializes_external_effects(self):
        kernel = self.kernel(unresolved_limit=1)
        first_obligation, second_obligation = obligations()[:2]

        first = kernel.admit(proposal("p1", first_obligation), now=100)
        capability = first.capability
        assert capability is not None
        kernel.execute(
            capability,
            now=101,
            case_id="case:1",
            authority_epoch=7,
            state_version=3,
            subject_ref="employee:1",
            target_system="hris",
            operation="employee.deactivate",
            request_identity="request:p1",
        )

        second = kernel.admit(proposal("p2", second_obligation), now=102)

        self.assertEqual(second.decision, Decision.HOLD)

    def test_verified_postcondition_allows_progress(self):
        kernel = self.kernel(unresolved_limit=1)
        first_obligation, second_obligation = obligations()[:2]

        first = kernel.admit(proposal("p1", first_obligation), now=100)
        capability = first.capability
        assert capability is not None
        kernel.execute(
            capability,
            now=101,
            case_id="case:1",
            authority_epoch=7,
            state_version=3,
            subject_ref="employee:1",
            target_system="hris",
            operation="employee.deactivate",
            request_identity="request:p1",
        )
        self.assertTrue(
            kernel.verify(
                first_obligation.obligation_id,
                observed_postcondition={"active": False},
            )
        )

        second = kernel.admit(proposal("p2", second_obligation), now=102)

        self.assertEqual(second.decision, Decision.ADMIT)

    def test_provider_success_is_not_completion_without_readback(self):
        kernel = self.kernel()
        obligation = obligations()[2]
        result = kernel.admit(proposal("p1", obligation), now=100)
        capability = result.capability
        assert capability is not None
        kernel.execute(
            capability,
            now=101,
            case_id="case:1",
            authority_epoch=7,
            state_version=3,
            subject_ref="employee:1",
            target_system="iam",
            operation="sessions.revoke",
            request_identity="request:p1",
        )

        self.assertFalse(kernel.externally_complete())
        self.assertEqual(
            kernel.effects[obligation.obligation_id].knowledge,
            EffectKnowledge.POSSIBLY_EFFECTED,
        )

    def test_external_completion_requires_all_three_verified_effects(self):
        kernel = self.kernel(unresolved_limit=1)
        for index, obligation in enumerate(obligations(), start=1):
            result = kernel.admit(proposal(f"p{index}", obligation), now=100 + index)
            capability = result.capability
            assert capability is not None
            kernel.execute(
                capability,
                now=110 + index,
                case_id="case:1",
                authority_epoch=7,
                state_version=3,
                subject_ref="employee:1",
                target_system=obligation.target_system,
                operation=obligation.operation,
                request_identity=f"request:p{index}",
            )
            kernel.verify(
                obligation.obligation_id,
                observed_postcondition=dict(obligation.expected_postcondition),
            )

        self.assertTrue(kernel.externally_complete())


if __name__ == "__main__":
    unittest.main()
