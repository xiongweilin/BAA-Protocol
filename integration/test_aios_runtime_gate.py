import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from administrative_orchestrator.authority import (
    ApprovalSatisfaction,
    AuthorityRepository,
    IdentityBinding,
)
from administrative_orchestrator.domain import (
    AdministrativeCase,
    AdministrativeRequest,
    CaseStatus,
    Decision,
    DecisionDisposition,
    Delegation,
    FactAssertion,
    FactAuthority,
    FactSnapshot,
    Principal,
    PrincipalKind,
    RoleAssignment,
)
from administrative_orchestrator.effect_provider import (
    ObservationAvailability,
    ObservationFreshness,
    ObservationPresence,
    ProviderExecutionResult,
    ProviderExecutionStatus,
    RealityObservation,
)
from administrative_orchestrator.governance import GovernanceRepository
from administrative_orchestrator.offboarding_execution import OffboardingExecutionEngine
from administrative_orchestrator.persistence import (
    DecisionRow,
    PolicyEvaluationRow,
    SqlStore,
    utcnow,
)
from administrative_orchestrator.policy import OffboardingFacts
from administrative_orchestrator.policy_plane import (
    PolicyRepository,
    compile_offboarding_policy,
    default_offboarding_policy_version,
)

from aios_gate import BAAGatedAIOSProvider
from aios_refinement import (
    AbstractPhase,
    assert_refines_protocol,
    phase_by_effect,
)


_NOW = datetime(2026, 9, 11, 9, 0, tzinfo=UTC)
_EFFECTIVE = _NOW + timedelta(hours=2)
_AFTER = _EFFECTIVE + timedelta(seconds=1)


class Provider:
    def __init__(
        self,
        *,
        unknown_first: bool = False,
        lost_ack_first: bool = False,
    ) -> None:
        self.unknown_first = unknown_first
        self.lost_ack_first = lost_ack_first
        self.execute_calls = 0
        self.operations: list[str] = []
        self.observations: dict[str, RealityObservation] = {}

    def execute(self, effect, payload):
        self.execute_calls += 1
        self.operations.append(effect.operation)
        ambiguous_first = (
            (self.unknown_first or self.lost_ack_first)
            and self.execute_calls == 1
        )

        expected_payload = {
            key: payload[key]
            for key in (
                "employee_ref",
                "employment_episode_ref",
                "termination_status",
                "termination_effective_at",
            )
            if payload.get(key) is not None
        }
        state = {
            "target_system": effect.target_system,
            "operation": effect.operation,
            "subject_ref": effect.subject_ref,
            "payload": expected_payload,
        }
        if effect.operation == "employee.deactivate":
            state["active"] = False
        elif effect.operation == "identity.disable":
            state["enabled"] = False
        elif effect.operation == "sessions.revoke":
            state["active_sessions"] = 0
        observation = RealityObservation(
            availability=ObservationAvailability.AVAILABLE,
            presence=ObservationPresence.PRESENT,
            freshness=ObservationFreshness.CURRENT,
            target_system=effect.target_system,
            operation=effect.operation,
            subject_ref=effect.subject_ref,
            provider_ref=f"provider:{effect.effect_id}",
            state=state,
            digest=f"digest:{effect.effect_id}",
            observed_at=_AFTER,
        )
        if not (self.unknown_first and ambiguous_first):
            # lost_ack_first models a reality write whose acknowledgement is
            # lost; unknown_first models ambiguity with no independent readback.
            self.observations[str(effect.effect_id)] = observation
        if ambiguous_first:
            return ProviderExecutionResult(
                status=ProviderExecutionStatus.OUTCOME_UNKNOWN,
                provider_ref=observation.provider_ref if self.lost_ack_first else None,
                error="simulated lost confirmation",
                retryable=False,
            )
        return ProviderExecutionResult(
            status=ProviderExecutionStatus.SUCCEEDED,
            provider_ref=observation.provider_ref,
        )

    def observe(self, effect):
        existing = self.observations.get(str(effect.effect_id))
        if existing is not None:
            return existing
        return RealityObservation(
            availability=ObservationAvailability.UNAVAILABLE,
            presence=ObservationPresence.UNKNOWN,
            freshness=ObservationFreshness.UNKNOWN,
            target_system=effect.target_system,
            operation=effect.operation,
            subject_ref=effect.subject_ref,
            error_class="simulated_unavailable",
        )


def authorized_case():
    store = SqlStore("sqlite+pysqlite:///:memory:")
    store.init_schema()
    authority = AuthorityRepository(store)

    for principal_id in (
        "person:departing",
        "person:successor",
        "person:approver",
    ):
        authority.put_principal(
            Principal(
                principal_id=principal_id,
                kind=PrincipalKind.PERSON,
                display_name=principal_id,
            )
        )

    for principal_id, role in (
        ("person:departing", "manager"),
        ("person:departing", "hr_approver"),
        ("person:successor", "hr_approver"),
        ("person:approver", "hr_approver"),
    ):
        authority.put_role_assignment(
            RoleAssignment(
                principal_id=principal_id,
                role=role,
                organization_scope="org:finance",
                valid_from=_NOW - timedelta(days=30),
            )
        )

    authority.put_identity_binding(
        IdentityBinding(
            provider="keycloak",
            external_subject="kc:departing",
            principal_id="person:departing",
            valid_from=_NOW - timedelta(days=30),
        )
    )
    authority.put_delegation(
        Delegation(
            from_principal_id="person:departing",
            to_principal_id="person:successor",
            role="hr_approver",
            organization_scope="org:finance",
            valid_from=_NOW - timedelta(days=5),
            valid_until=_EFFECTIVE + timedelta(days=30),
        )
    )

    record = default_offboarding_policy_version()
    PolicyRepository(store).put_version(record)
    typed_facts = OffboardingFacts(
        employee_ref="odoo:hr.employee:42",
        termination_status="termination_scheduled",
        termination_effective_at=_EFFECTIVE.isoformat(),
        employment_episode_ref="episode:1",
        departing_principal_id="person:departing",
        successor_principal_id="person:successor",
    )
    fact_values = {**typed_facts.model_dump(mode="json"), "active": True}
    assertions = {
        key: FactAssertion(
            value=value,
            authority=FactAuthority.AUTHORITATIVE,
            source="odoo",
            owner="hris",
            source_ref="odoo:hr.employee:42",
            source_version="source:v1",
            observed_at=_NOW,
        )
        for key, value in fact_values.items()
        if value is not None
    }

    request = AdministrativeRequest(
        requester_principal_id="person:requester",
        channel="integration",
        intent="offboard employee 42",
    )
    case = AdministrativeCase(
        case_kind="employee-offboarding",
        requester_principal_id=request.requester_principal_id,
        subject_ref="odoo:hr.employee:42",
        status=CaseStatus.AUTHORIZED,
        version=4,
        policy_ref=record.policy_ref,
        fact_snapshot=FactSnapshot(
            source="odoo",
            owner="hris",
            authority=FactAuthority.AUTHORITATIVE,
            observed_at=_NOW,
            facts=fact_values,
            assertions=assertions,
        ),
    )
    store.create_case(request, case)

    evaluation = compile_offboarding_policy(record).evaluate(typed_facts)
    decision = Decision(
        case_id=case.case_id,
        case_version=case.version - 1,
        authority_epoch=case.authority_epoch,
        principal_id="person:approver",
        decision_role="hr_approver",
        disposition=DecisionDisposition.APPROVE,
        rationale="approved",
        policy_ref=record.policy_ref,
        decided_at=_NOW,
    )
    with store.sessions.begin() as db:
        db.add(
            PolicyEvaluationRow(
                case_id=case.case_id,
                case_version=case.version,
                authority_epoch=case.authority_epoch,
                policy_json=evaluation.policy_ref.model_dump(mode="json"),
                evaluation_json=evaluation.model_dump(mode="json"),
                created_at=utcnow(),
            )
        )
        db.add(
            DecisionRow(
                decision_id=decision.decision_id,
                case_id=decision.case_id,
                case_version=decision.case_version,
                authority_epoch=decision.authority_epoch,
                principal_id=decision.principal_id,
                decision_role=decision.decision_role,
                disposition=decision.disposition.value,
                rationale=decision.rationale,
                policy_json=decision.policy_ref.model_dump(mode="json"),
                decided_at=decision.decided_at,
            )
        )

    authority.put_decision_binding(decision, organization_scope="org:finance")
    satisfaction = authority.put_approval_satisfaction(
        ApprovalSatisfaction(
            satisfaction_id=uuid4(),
            case_id=case.case_id,
            authority_epoch=case.authority_epoch,
            policy_ref=record.policy_ref,
            decision_ids=(decision.decision_id,),
            satisfied_roles=("hr_approver",),
            assessed_at=_NOW,
        )
    )
    GovernanceRepository(store).create_for_approval(
        case,
        satisfaction,
        organization_scope="org:finance",
        fact_dependency_keys=(
            "employee_ref",
            "termination_status",
            "termination_effective_at",
            "employment_episode_ref",
        ),
        expected_change_keys=("active",),
    )
    return store, case


class BAARuntimeGateTests(unittest.TestCase):
    def test_real_aios_offboarding_completes_through_baa_gate(self):
        store, case = authorized_case()
        provider = Provider()
        gate = BAAGatedAIOSProvider(
            store,
            provider,
            now=lambda: _AFTER,
            unresolved_limit=1,
        )
        engine = OffboardingExecutionEngine(
            store,
            gate,
            clock=lambda: _AFTER,
        )

        completed = engine.run(case.case_id)

        self.assertEqual(completed.status, CaseStatus.COMPLETED)
        self.assertEqual(
            provider.operations,
            ["identity.disable", "sessions.revoke", "employee.deactivate"],
        )
        self.assertEqual(provider.execute_calls, 3)
        assert_refines_protocol(gate.refinement_trace)
        self.assertEqual(len(gate.refinement_trace), 9)
        self.assertEqual(
            set(phase_by_effect(gate.refinement_trace).values()),
            {AbstractPhase.SETTLED},
        )

        altered = list(gate.refinement_trace)
        altered[1] = replace(altered[1], target_system="scope:changed")
        with self.assertRaises(AssertionError):
            assert_refines_protocol(altered)

    def test_lost_ack_recovers_then_releases_remaining_effects(self):
        store, case = authorized_case()
        provider = Provider(lost_ack_first=True)
        gate = BAAGatedAIOSProvider(
            store,
            provider,
            now=lambda: _AFTER,
            unresolved_limit=1,
        )
        engine = OffboardingExecutionEngine(
            store,
            gate,
            clock=lambda: _AFTER,
        )

        first = engine.run(case.case_id)
        # Independent read-back can resolve the lost acknowledgement in the
        # same engine turn. The key invariant is that only the first external
        # effect was attempted before the gate released further execution.
        self.assertEqual(first.status, CaseStatus.EXECUTING)
        self.assertEqual(provider.execute_calls, 1)
        self.assertEqual(provider.operations, ["identity.disable"])

        completed = engine.run(case.case_id)
        self.assertEqual(completed.status, CaseStatus.COMPLETED)
        self.assertEqual(
            provider.operations,
            ["identity.disable", "sessions.revoke", "employee.deactivate"],
        )
        self.assertEqual(provider.execute_calls, 3)
        assert_refines_protocol(gate.refinement_trace)
        self.assertEqual(
            set(phase_by_effect(gate.refinement_trace).values()),
            {AbstractPhase.SETTLED},
        )
        first_effect_events = [
            event
            for event in gate.refinement_trace
            if event.effect_id == gate.refinement_trace[0].effect_id
        ]
        self.assertEqual(
            [event.next for event in first_effect_events[:3]],
            [
                AbstractPhase.RESERVED,
                AbstractPhase.PENDING,
                AbstractPhase.SETTLED,
            ],
        )
        self.assertEqual(first_effect_events[2].event, "independent-readback")

    def test_unmet_readback_remains_pending_and_fences_repeated_dispatch(self):
        store, case = authorized_case()

        class UnmetReadbackProvider(Provider):
            def observe(self, effect):
                result = super().observe(effect)
                if effect.operation == "identity.disable":
                    return result.model_copy(
                        update={"state": {**result.state, "enabled": True}}
                    )
                return result

        provider = UnmetReadbackProvider()
        gate = BAAGatedAIOSProvider(
            store,
            provider,
            now=lambda: _AFTER,
            unresolved_limit=1,
        )
        engine = OffboardingExecutionEngine(
            store,
            gate,
            clock=lambda: _AFTER,
        )
        current = engine.run(case.case_id)

        self.assertEqual(current.status, CaseStatus.RECONCILING)
        self.assertEqual(provider.execute_calls, 1)
        self.assertEqual(provider.operations, ["identity.disable"])
        kernel = next(iter(gate._kernels.values()))
        first_obligation = next(
            key for key, value in kernel.obligations.items()
            if value.operation == "identity.disable"
        )
        from baa_protocol.offboarding import EffectKnowledge

        self.assertEqual(
            kernel.effects[first_obligation].knowledge,
            EffectKnowledge.POSSIBLY_EFFECTED,
        )
        self.assertEqual(
            phase_by_effect(gate.refinement_trace)[gate.refinement_trace[0].effect_id],
            AbstractPhase.PENDING,
        )

        again = engine.run(case.case_id)
        self.assertEqual(again.status, CaseStatus.RECONCILING)
        self.assertEqual(provider.execute_calls, 1)
        assert_refines_protocol(gate.refinement_trace)

    def test_unknown_first_effect_prevents_additional_provider_dispatch(self):
        store, case = authorized_case()
        provider = Provider(unknown_first=True)
        gate = BAAGatedAIOSProvider(
            store,
            provider,
            now=lambda: _AFTER,
            unresolved_limit=1,
        )
        engine = OffboardingExecutionEngine(
            store,
            gate,
            clock=lambda: _AFTER,
        )

        current = engine.run(case.case_id)

        self.assertEqual(current.status, CaseStatus.RECONCILING)
        self.assertEqual(provider.execute_calls, 1)
        self.assertEqual(provider.operations, ["identity.disable"])

        # A retry remains reconciliation-only while the original effect cannot
        # be independently resolved; no second provider invocation is allowed.
        again = engine.run(case.case_id)
        self.assertEqual(again.status, CaseStatus.RECONCILING)
        self.assertEqual(provider.execute_calls, 1)

        assert_refines_protocol(gate.refinement_trace)
        phases = phase_by_effect(gate.refinement_trace)
        self.assertEqual(len(phases), 1)
        self.assertEqual(next(iter(phases.values())), AbstractPhase.PENDING)
        self.assertEqual(
            [event.next for event in gate.refinement_trace[:2]],
            [AbstractPhase.RESERVED, AbstractPhase.PENDING],
        )
        self.assertTrue(
            all(
                event.next is AbstractPhase.PENDING
                for event in gate.refinement_trace[2:]
            )
        )


if __name__ == "__main__":
    unittest.main()
