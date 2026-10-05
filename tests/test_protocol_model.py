import unittest

from baa_protocol.model import (
    AdmissionKernel,
    Decision,
    Proposal,
    ProposalState,
)


def proposal(
    proposal_id: str,
    *,
    object_id: str = "account:1",
    operation: str = "transfer",
    quota: int = 10,
    exposure_bound: int = 10,
    risk_factor: str = "counterparty:A",
    expires_at: int = 100,
    state_version: int = 1,
    verification_available: bool = True,
    bridge_valid: bool = True,
    fallback_viable: bool = True,
    composition_bounded: bool = True,
) -> Proposal:
    return Proposal(
        proposal_id=proposal_id,
        object_id=object_id,
        operation=operation,
        quota=quota,
        exposure_bound=exposure_bound,
        risk_factor=risk_factor,
        expires_at=expires_at,
        state_version=state_version,
        verification_available=verification_available,
        bridge_valid=bridge_valid,
        fallback_viable=fallback_viable,
        composition_bounded=composition_bounded,
    )


class AdmissionKernelTests(unittest.TestCase):
    def test_single_action_can_be_admitted(self):
        kernel = AdmissionKernel(risk_budget=50)
        result = kernel.evaluate(proposal("p1", exposure_bound=20))

        self.assertEqual(result.decision, Decision.ADMIT)
        self.assertIsNotNone(result.capability)
        self.assertEqual(kernel.current_risk, 20)
        self.assertEqual(kernel.states["p1"], ProposalState.ADMITTED)

    def test_composition_changes_second_action_admissibility(self):
        kernel = AdmissionKernel(risk_budget=80, interaction_penalty=1)

        first = kernel.evaluate(
            proposal("p1", exposure_bound=30, risk_factor="shared")
        )
        second = kernel.evaluate(
            proposal("p2", exposure_bound=30, risk_factor="shared")
        )

        self.assertEqual(first.decision, Decision.ADMIT)
        # Base exposure would be 60, but the toy joint interaction adds 30.
        self.assertEqual(second.decision, Decision.DENY)
        self.assertEqual(kernel.current_risk, 30)

    def test_unbounded_composition_holds_instead_of_assuming_zero(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(
            proposal("p1", composition_bounded=False)
        )

        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(kernel.current_risk, 0)

    def test_missing_verification_path_holds(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(
            proposal("p1", verification_available=False)
        )

        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIsNone(result.capability)

    def test_missing_semantic_bridge_holds(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", bridge_valid=False))

        self.assertEqual(result.decision, Decision.HOLD)

    def test_nonviable_fallback_holds(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", fallback_viable=False))

        self.assertEqual(result.decision, Decision.HOLD)

    def test_protected_guarantee_source_is_unreachable(self):
        kernel = AdmissionKernel(
            risk_budget=100,
            protected_sources={"observer:trusted"},
        )
        result = kernel.evaluate(
            proposal("p1", object_id="observer:trusted", operation="write")
        )

        self.assertEqual(result.decision, Decision.DENY)
        self.assertIsNone(result.capability)

    def test_executor_rejects_capability_rebinding(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1"))
        capability = result.capability
        assert capability is not None

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                object_id="account:other",
                operation="transfer",
                amount=5,
                now=1,
                state_version=1,
            )

    def test_executor_rejects_expired_capability(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", expires_at=5))
        capability = result.capability
        assert capability is not None

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                object_id="account:1",
                operation="transfer",
                amount=5,
                now=6,
                state_version=1,
            )

    def test_executor_rejects_stale_state_version(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", state_version=2))
        capability = result.capability
        assert capability is not None

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                object_id="account:1",
                operation="transfer",
                amount=5,
                now=1,
                state_version=3,
            )

    def test_attempt_moves_exposure_without_double_counting(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", exposure_bound=25))
        capability = result.capability
        assert capability is not None

        before = kernel.current_risk
        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=5,
            now=1,
            state_version=1,
        )

        self.assertEqual(before, 25)
        self.assertEqual(kernel.current_risk, 25)
        self.assertNotIn("p1", kernel.ledger.reserved)
        self.assertIn("p1", kernel.ledger.pending)

    def test_pending_action_cannot_be_replayed(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1"))
        capability = result.capability
        assert capability is not None

        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=5,
            now=1,
            state_version=1,
        )

        with self.assertRaises(PermissionError):
            kernel.execute(
                capability,
                object_id="account:1",
                operation="transfer",
                amount=5,
                now=2,
                state_version=1,
            )

    def test_lost_confirmation_keeps_declared_bound(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", exposure_bound=40))
        capability = result.capability
        assert capability is not None

        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=5,
            now=1,
            state_version=1,
        )
        kernel.conservative_timeout_settlement("p1")

        self.assertEqual(kernel.states["p1"], ProposalState.SETTLED)
        self.assertEqual(kernel.current_risk, 40)
        self.assertNotIn("p1", kernel.ledger.pending)
        self.assertEqual(kernel.ledger.settled["p1"].bound, 40)

    def test_verified_no_effect_can_release_exposure(self):
        kernel = AdmissionKernel(risk_budget=100)
        result = kernel.evaluate(proposal("p1", exposure_bound=40))
        capability = result.capability
        assert capability is not None

        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=5,
            now=1,
            state_version=1,
        )
        kernel.verify("p1", realized_exposure=0)

        self.assertEqual(kernel.current_risk, 0)

    def test_settled_exposure_affects_future_admission(self):
        kernel = AdmissionKernel(risk_budget=50)

        first = kernel.evaluate(proposal("p1", exposure_bound=40))
        capability = first.capability
        assert capability is not None
        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=5,
            now=1,
            state_version=1,
        )
        kernel.verify("p1", realized_exposure=40)

        second = kernel.evaluate(
            proposal("p2", exposure_bound=20, risk_factor="other")
        )
        self.assertEqual(second.decision, Decision.DENY)


if __name__ == "__main__":
    unittest.main()
