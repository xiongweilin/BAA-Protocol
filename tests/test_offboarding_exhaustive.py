import itertools
import unittest

from baa_protocol.model import Decision
from baa_protocol.offboarding import (
    OffboardingKernel,
    OffboardingObligation,
    OffboardingProposal,
)


def obligation() -> OffboardingObligation:
    return OffboardingObligation(
        obligation_id="obl:1",
        case_id="case:1",
        authority_epoch=7,
        governance_basis_id="basis:1",
        subject_ref="employee:1",
        target_system="iam",
        operation="identity.disable",
        expected_postcondition=(("enabled", False),),
    )


class ExhaustiveAdmissionTests(unittest.TestCase):
    def test_all_boolean_fault_combinations_fail_closed(self):
        flags = (
            "before_effective",
            "stale_epoch",
            "wrong_subject",
            "wrong_operation",
            "verification_unavailable",
            "bridge_invalid",
            "protected_target",
        )
        for bits in itertools.product((False, True), repeat=len(flags)):
            case = dict(zip(flags, bits))
            with self.subTest(**case):
                item = obligation()
                kernel = OffboardingKernel(
                    case_id="case:1",
                    authority_epoch=7,
                    state_version=3,
                    obligations=(item,),
                    unresolved_limit=1,
                )
                proposal = OffboardingProposal(
                    proposal_id="p1",
                    obligation_id=item.obligation_id,
                    case_id=item.case_id,
                    authority_epoch=6 if case["stale_epoch"] else item.authority_epoch,
                    governance_basis_id=item.governance_basis_id,
                    subject_ref="employee:2" if case["wrong_subject"] else item.subject_ref,
                    target_system=item.target_system,
                    operation="identity.delete" if case["wrong_operation"] else item.operation,
                    state_version=3,
                    effective_at=100,
                    expires_at=200,
                    request_identity="request:p1",
                    verification_available=not case["verification_unavailable"],
                    bridge_valid=not case["bridge_invalid"],
                    protected_source_target=case["protected_target"],
                )
                now = 99 if case["before_effective"] else 100

                result = kernel.admit(proposal, now=now)

                any_fault = any(case.values())
                if any_fault:
                    self.assertIn(result.decision, {Decision.DENY, Decision.HOLD})
                    self.assertIsNone(result.capability)
                else:
                    self.assertEqual(result.decision, Decision.ADMIT)
                    self.assertIsNotNone(result.capability)

    def test_execution_binding_mutations_are_rejected(self):
        item = obligation()
        mutations = (
            {"case_id": "case:2"},
            {"authority_epoch": 8},
            {"state_version": 4},
            {"subject_ref": "employee:2"},
            {"target_system": "hris"},
            {"operation": "sessions.revoke"},
            {"request_identity": "request:other"},
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=mutation):
                kernel = OffboardingKernel(
                    case_id="case:1",
                    authority_epoch=7,
                    state_version=3,
                    obligations=(item,),
                )
                proposal = OffboardingProposal(
                    proposal_id=f"p{index}",
                    obligation_id=item.obligation_id,
                    case_id=item.case_id,
                    authority_epoch=item.authority_epoch,
                    governance_basis_id=item.governance_basis_id,
                    subject_ref=item.subject_ref,
                    target_system=item.target_system,
                    operation=item.operation,
                    state_version=3,
                    effective_at=100,
                    expires_at=200,
                    request_identity=f"request:p{index}",
                )
                admitted = kernel.admit(proposal, now=100)
                capability = admitted.capability
                assert capability is not None
                call = dict(
                    now=101,
                    case_id="case:1",
                    authority_epoch=7,
                    state_version=3,
                    subject_ref="employee:1",
                    target_system="iam",
                    operation="identity.disable",
                    request_identity=f"request:p{index}",
                )
                call.update(mutation)

                with self.assertRaises(PermissionError):
                    kernel.execute(capability, **call)


if __name__ == "__main__":
    unittest.main()
