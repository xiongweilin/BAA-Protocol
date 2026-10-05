import unittest
from datetime import UTC, datetime
from uuid import uuid4

from administrative_orchestrator.authority import AuthorityRepository
from administrative_orchestrator.domain import AdministrativeCase, FactAuthority, FactSnapshot
from administrative_orchestrator.integrations.runtime_capabilities import (
    WORLD_RUNTIME_EFFECT_CAPABILITIES,
)
from administrative_orchestrator.obligations import ObligationFulfillmentKind
from administrative_orchestrator.offboarding_obligations import derive_offboarding_obligations
from administrative_orchestrator.persistence import SqlStore
from administrative_orchestrator.policy import OffboardingFacts
from administrative_orchestrator.policy_plane import (
    compile_offboarding_policy,
    default_offboarding_policy_version,
)

from baa_protocol.aios_adapter import (
    AIOS_RUNTIME_CAPABILITY_BY_EFFECT,
    project_aios_external_obligation,
    runtime_capability_for,
)
from baa_protocol.model import Decision
from baa_protocol.offboarding import OffboardingKernel, OffboardingProposal


class AIOSOffboardingCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.record = default_offboarding_policy_version()
        self.policy = compile_offboarding_policy(self.record)
        self.facts = OffboardingFacts(
            employee_ref="employee:1",
            termination_status="termination_scheduled",
            termination_effective_at=datetime(2026, 10, 6, tzinfo=UTC).isoformat(),
            departing_principal_id="person:departing",
        )
        self.evaluation = self.policy.evaluate(self.facts)
        self.case = AdministrativeCase(
            case_kind="employee-offboarding",
            requester_principal_id="person:operator",
            subject_ref="employee:1",
            policy_ref=self.record.policy_ref,
            fact_snapshot=FactSnapshot(
                source="integration-fixture",
                owner="hris",
                authority=FactAuthority.AUTHORITATIVE,
                facts=self.facts.model_dump(mode="json"),
            ),
        )
        self.governance_basis_id = uuid4()
        store = SqlStore("sqlite+pysqlite:///:memory:")
        store.init_schema()
        authority = AuthorityRepository(store)
        self.obligation_set = derive_offboarding_obligations(
            self.case,
            self.evaluation,
            self.policy,
            authority,
            governance_basis_id=self.governance_basis_id,
            transfer_requirements=(),
        )
        self.external = tuple(
            item
            for item in self.obligation_set.obligations
            if item.fulfillment_kind is ObligationFulfillmentKind.EXTERNAL_EFFECT_VERIFIED
        )

    def test_aios_policy_effect_set_matches_baa_hard_domain(self):
        policy_pairs = {
            (item.target_system, item.operation)
            for item in self.evaluation.allowed_effects
        }
        self.assertEqual(
            policy_pairs,
            set(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS),
        )

    def test_aios_derived_external_obligations_project_without_loss_of_scope(self):
        projected = tuple(project_aios_external_obligation(item) for item in self.external)

        self.assertEqual(len(projected), 3)
        self.assertEqual(
            {(item.target_system, item.operation) for item in projected},
            set(OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS),
        )
        self.assertTrue(all(item.subject_ref == "employee:1" for item in projected))
        self.assertTrue(
            all(item.authority_epoch == self.case.authority_epoch for item in projected)
        )
        self.assertTrue(
            all(item.governance_basis_id == str(self.governance_basis_id) for item in projected)
        )

    def test_aios_postconditions_retain_covered_reality_state(self):
        projected = {
            item.operation: project_aios_external_obligation(item)
            for item in self.external
        }

        self.assertEqual(
            dict(projected["employee.deactivate"].expected_postcondition)["active"],
            False,
        )
        self.assertEqual(
            dict(projected["identity.disable"].expected_postcondition)["enabled"],
            False,
        )
        self.assertEqual(
            dict(projected["sessions.revoke"].expected_postcondition)["active_sessions"],
            0,
        )

    def test_runtime_capability_mapping_exists_in_pinned_aios(self):
        projected = tuple(project_aios_external_obligation(item) for item in self.external)
        mapped = {runtime_capability_for(item) for item in projected}

        self.assertEqual(mapped, set(AIOS_RUNTIME_CAPABILITY_BY_EFFECT.values()))
        self.assertTrue(mapped <= set(WORLD_RUNTIME_EFFECT_CAPABILITIES))

    def test_baa_kernel_can_execute_aios_derived_obligations(self):
        projected = tuple(project_aios_external_obligation(item) for item in self.external)
        kernel = OffboardingKernel(
            case_id=str(self.case.case_id),
            authority_epoch=self.case.authority_epoch,
            state_version=self.case.version,
            obligations=projected,
            unresolved_limit=1,
        )

        for index, item in enumerate(projected):
            proposal = OffboardingProposal(
                proposal_id=f"aios:p{index}",
                obligation_id=item.obligation_id,
                case_id=item.case_id,
                authority_epoch=item.authority_epoch,
                governance_basis_id=item.governance_basis_id,
                subject_ref=item.subject_ref,
                target_system=item.target_system,
                operation=item.operation,
                state_version=self.case.version,
                effective_at=100,
                expires_at=200,
                request_identity=f"request:aios:p{index}",
            )
            admitted = kernel.admit(proposal, now=100)
            self.assertEqual(admitted.decision, Decision.ADMIT)
            capability = admitted.capability
            assert capability is not None
            kernel.execute(
                capability,
                now=101,
                case_id=item.case_id,
                authority_epoch=item.authority_epoch,
                state_version=self.case.version,
                subject_ref=item.subject_ref,
                target_system=item.target_system,
                operation=item.operation,
                request_identity=proposal.request_identity,
            )
            observed = dict(item.expected_postcondition)
            self.assertTrue(
                kernel.verify(
                    item.obligation_id,
                    observed_postcondition=observed,
                )
            )

        self.assertTrue(kernel.externally_complete())


if __name__ == "__main__":
    unittest.main()
