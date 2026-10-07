import asyncio
import os
import tempfile
import unittest

from administrative_orchestrator.config import Settings
from world_runtime.execution import (
    CapabilityRequest,
    EffectIdentityReboundError,
    effect_identity_fingerprint,
)

import scripts.domains.administrative.production_world_runtime_stack as stack

from baa_protocol.aios_adapter import AIOS_RUNTIME_CAPABILITY_BY_EFFECT
from world_runtime_refinement import (
    RuntimeScopeBinding,
    assert_scope_binding,
    assert_strict_effect_rule,
    assert_writer_verifier_separated,
)


def settings() -> Settings:
    return Settings(
        _env_file=None,
        runtime_profile="staging",
        auth_mode="oidc",
        oidc_issuer="https://issuer.example.test",
        oidc_audience="administrative-orchestrator",
        world_runtime_mode="cutover",
        odoo_base_url="https://odoo.example.test",
        odoo_database="company",
        odoo_writer_username="writer",
        odoo_verifier_username="verifier",
        odoo_financial_writer_username="financial-writer",
        odoo_financial_verifier_username="financial-verifier",
        keycloak_base_url="https://keycloak.example.test",
        keycloak_realm="company",
        keycloak_writer_client_id="writer",
        keycloak_verifier_client_id="verifier",
        communication_gateway_base_url="",
    )


class AIOSWorldRuntimeSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_get_settings = stack.get_settings
        self.old_state_path = os.environ.get("WORLD_RUNTIME_ADMIN_PRODUCTION_STATE_PATH")
        stack.get_settings = settings
        os.environ["WORLD_RUNTIME_ADMIN_PRODUCTION_STATE_PATH"] = os.path.join(
            self.temp.name,
            "runtime.db",
        )
        self.runtime = stack.build()

    def tearDown(self):
        stack.get_settings = self.old_get_settings
        if self.old_state_path is None:
            os.environ.pop("WORLD_RUNTIME_ADMIN_PRODUCTION_STATE_PATH", None)
        else:
            os.environ["WORLD_RUNTIME_ADMIN_PRODUCTION_STATE_PATH"] = self.old_state_path
        self.temp.cleanup()

    def test_baa_effect_capabilities_have_strict_runtime_rules(self):
        rules = {
            rule.capability: rule
            for rule in self.runtime.contract_registry.list_effect_rules()
        }

        for capability in AIOS_RUNTIME_CAPABILITY_BY_EFFECT.values():
            with self.subTest(capability=capability):
                self.assertIn(capability, rules)
                rule = rules[capability]
                assert_strict_effect_rule(rule)

    def test_covered_effects_have_distinct_writer_and_verifier_domains(self):
        providers = self.runtime.registry.list()

        for capability in AIOS_RUNTIME_CAPABILITY_BY_EFFECT.values():
            with self.subTest(capability=capability):
                assert_writer_verifier_separated(capability, providers)

    def test_runtime_rejects_covered_effect_without_authorization_before_provider(self):
        capability = AIOS_RUNTIME_CAPABILITY_BY_EFFECT[
            ("iam", "identity.disable")
        ]
        responsibility = self.runtime.responsibility.create(
            __import__(
                "world_runtime.responsibility",
                fromlist=["Responsibility"],
            ).Responsibility(
                id="responsibility:baa-auth-test",
                principal="principal:test",
                subject="employee:1",
                domain="administrative",
            )
        )
        work = self.runtime.execution.admit_work(
            responsibility_id=responsibility.id,
            kind="administrative-effect",
            payload={},
        )

        async def invoke_without_authorization():
            await self.runtime.invoke(
                CapabilityRequest(
                    capability=capability,
                    work_id=work.id,
                    actor_ref="principal:test",
                    principal="principal:test",
                    resource_ref="administrative:iam:employee:1",
                    resource="administrative:iam:employee:1",
                    subject_version_refs=[
                        "administrative-case:case:test:v1",
                        "authority-epoch:1",
                    ],
                    idempotency_key="baa:missing-auth",
                    parameters={"subject_ref": "employee:1"},
                    effect_class="external-effect",
                )
            )

        with self.assertRaisesRegex(
            PermissionError,
            "effectful capability requires authorization",
        ):
            asyncio.run(invoke_without_authorization())
        self.assertIsNone(
            self.runtime.ledger.project_get(
                "execution.provider-attempt",
                "baa:missing-auth",
            )
        )

    def test_runtime_rejects_missing_resource_and_version_before_attempt(self):
        capability = AIOS_RUNTIME_CAPABILITY_BY_EFFECT[
            ("iam", "identity.disable")
        ]
        responsibility = self.runtime.responsibility.create(
            __import__(
                "world_runtime.responsibility",
                fromlist=["Responsibility"],
            ).Responsibility(
                id="responsibility:baa-scope-test",
                principal="principal:test",
                subject="employee:1",
                domain="administrative",
            )
        )
        work = self.runtime.execution.admit_work(
            responsibility_id=responsibility.id,
            kind="administrative-effect",
            payload={},
        )

        missing_resource = CapabilityRequest(
            capability=capability,
            work_id=work.id,
            actor_ref="principal:test",
            principal="principal:test",
            subject_version_refs=["administrative-case:case:test:v1"],
            idempotency_key="baa:missing-resource",
            parameters={"subject_ref": "employee:1"},
            effect_class="external-effect",
        )
        with self.assertRaisesRegex(
            PermissionError,
            "requires an explicit resource boundary",
        ):
            asyncio.run(self.runtime.invoke(missing_resource))
        self.assertIsNone(
            self.runtime.ledger.project_get(
                "execution.provider-attempt",
                "baa:missing-resource",
            )
        )

        missing_version = CapabilityRequest(
            capability=capability,
            work_id=work.id,
            actor_ref="principal:test",
            principal="principal:test",
            resource_ref="administrative:iam:employee:1",
            resource="administrative:iam:employee:1",
            idempotency_key="baa:missing-version",
            parameters={"subject_ref": "employee:1"},
            effect_class="external-effect",
        )
        with self.assertRaisesRegex(
            PermissionError,
            "requires explicit subject version refs",
        ):
            asyncio.run(self.runtime.invoke(missing_version))
        self.assertIsNone(
            self.runtime.ledger.project_get(
                "execution.provider-attempt",
                "baa:missing-version",
            )
        )

    def test_durable_effect_identity_rejects_scope_rebound(self):
        capability = AIOS_RUNTIME_CAPABILITY_BY_EFFECT[
            ("iam", "identity.disable")
        ]
        request = CapabilityRequest(
            capability=capability,
            actor_ref="principal:test",
            principal="principal:test",
            resource_ref="administrative:iam:employee:1",
            resource="administrative:iam:employee:1",
            subject_version_refs=[
                "administrative-case:case:test:v4",
                "authority-epoch:2",
            ],
            authorization_id="authorization:test",
            idempotency_key="baa:stable-effect",
            parameters={"subject_ref": "employee:1"},
            effect_class="external-effect",
        )
        binding = RuntimeScopeBinding.from_request(request)
        assert_scope_binding(
            binding,
            capability=capability,
            resource="administrative:iam:employee:1",
            subject_version_refs=(
                "administrative-case:case:test:v4",
                "authority-epoch:2",
            ),
            idempotency_key="baa:stable-effect",
        )

        fingerprint = effect_identity_fingerprint(request)
        self.runtime.execution.bind_effect_identity(
            request,
            fingerprint=fingerprint,
        )

        for changed in (
            request.model_copy(
                update={
                    "capability": AIOS_RUNTIME_CAPABILITY_BY_EFFECT[
                        ("iam", "sessions.revoke")
                    ]
                }
            ),
            request.model_copy(
                update={
                    "resource_ref": "administrative:iam:employee:2",
                    "resource": "administrative:iam:employee:2",
                }
            ),
            request.model_copy(
                update={
                    "subject_version_refs": [
                        "administrative-case:case:test:v5",
                        "authority-epoch:2",
                    ]
                }
            ),
        ):
            with self.subTest(change=changed.model_dump(mode="json")):
                self.assertNotEqual(
                    effect_identity_fingerprint(changed),
                    fingerprint,
                )
                with self.assertRaises(EffectIdentityReboundError):
                    self.runtime.execution.validate_effect_identity(
                        changed,
                        result_projection="execution.provider-idempotency",
                    )


if __name__ == "__main__":
    unittest.main()
