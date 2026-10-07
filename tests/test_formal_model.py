import unittest

from baa_protocol.formal_model import (
    Action,
    INVARIANTS_FORMAL_V1,
    OMEGA_FORMAL_V1,
    Phase,
    FormalState,
    reference_model_v1,
)
from baa_protocol.model import AdmissionKernel, Proposal


class FiniteFormalModelTests(unittest.TestCase):
    def test_exhaustive_finite_model_satisfies_declared_invariants(self):
        report = reference_model_v1().check()
        self.assertGreater(report.reachable_states, 1)
        self.assertGreater(report.explored_transitions, report.reachable_states)
        self.assertEqual(report.invariants, INVARIANTS_FORMAL_V1)
        self.assertEqual(report.omega, OMEGA_FORMAL_V1)

    def test_protected_source_never_receives_capability(self):
        model = reference_model_v1()
        initial = FormalState.initial(len(model.proposals))
        transition = model.step(initial, Action("evaluate", 3))
        self.assertTrue(transition.accepted)
        self.assertFalse(transition.capability_issued)
        self.assertEqual(transition.after.phases[3], Phase.DENIED)

    def test_composition_is_checked_against_current_joint_state(self):
        model = reference_model_v1()
        state = FormalState.initial(len(model.proposals))

        first = model.step(state, Action("evaluate", 0))
        self.assertTrue(first.capability_issued)
        second = model.step(first.after, Action("evaluate", 2))
        self.assertTrue(second.capability_issued)
        # shared-a + other consumes risk 2. Adding shared-b would create
        # base 3 plus a shared-factor interaction of 1, exceeding budget 3.
        third = model.step(second.after, Action("evaluate", 1))
        self.assertFalse(third.capability_issued)
        self.assertEqual(third.after.phases[1], Phase.DENIED)
        self.assertEqual(model.current_risk(third.after), 2)

    def test_pending_exact_replay_is_rejected(self):
        model = reference_model_v1()
        state = FormalState.initial(len(model.proposals))
        admitted = model.step(state, Action("evaluate", 0))
        execute = Action(
            "execute",
            0,
            object_id="account:a",
            operation="transfer",
            amount=1,
            now=1,
            state_version=1,
        )
        pending = model.step(admitted.after, execute)
        self.assertTrue(pending.accepted)
        replay = model.step(pending.after, execute)
        self.assertFalse(replay.accepted)
        self.assertEqual(replay.after.phases[0], Phase.PENDING)

    def test_capability_rebinding_is_rejected_without_state_change(self):
        model = reference_model_v1()
        state = FormalState.initial(len(model.proposals))
        admitted = model.step(state, Action("evaluate", 0))
        rebound = model.step(
            admitted.after,
            Action(
                "execute",
                0,
                object_id="account:other",
                operation="transfer",
                amount=1,
                now=1,
                state_version=1,
            ),
        )
        self.assertFalse(rebound.accepted)
        self.assertEqual(rebound.after, admitted.after)

    def test_timeout_charges_declared_bound(self):
        model = reference_model_v1()
        state = FormalState.initial(len(model.proposals))
        state = model.step(state, Action("evaluate", 0)).after
        state = model.step(
            state,
            Action(
                "execute",
                0,
                object_id="account:a",
                operation="transfer",
                amount=1,
                now=1,
                state_version=1,
            ),
        ).after
        settled = model.step(state, Action("timeout", 0))
        self.assertTrue(settled.accepted)
        self.assertEqual(settled.after.phases[0], Phase.SETTLED)
        self.assertEqual(settled.after.settled_exposure[0], 1)

    def test_out_of_omega_realized_exposure_can_break_budget_in_reference_kernel(self):
        # This is deliberately not "fixed" by clamping. It demonstrates why
        # realized <= declared bound must remain an explicit bridge/risk-model
        # assumption of the structural guarantee.
        kernel = AdmissionKernel(risk_budget=5)
        proposal = Proposal(
            proposal_id="p",
            object_id="account:1",
            operation="transfer",
            quota=1,
            exposure_bound=5,
            risk_factor="x",
            expires_at=2,
            state_version=1,
        )
        admission = kernel.evaluate(proposal)
        capability = admission.capability
        assert capability is not None
        kernel.execute(
            capability,
            object_id="account:1",
            operation="transfer",
            amount=1,
            now=1,
            state_version=1,
        )
        kernel.verify("p", realized_exposure=6)
        self.assertEqual(kernel.current_risk, 6)
        self.assertGreater(kernel.current_risk, kernel.risk_budget)


if __name__ == "__main__":
    unittest.main()
