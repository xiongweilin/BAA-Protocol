import asyncio
import os
import tempfile
import unittest

from administrative_orchestrator.config import Settings
from world_runtime.execution import CapabilityRequest

import scripts.domains.administrative.production_world_runtime_stack as stack

from baa_protocol.aios_adapter import AIOS_RUNTIME_CAPABILITY_BY_EFFECT


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
                self.assertTrue(rule.authorization_required)
                self.assertTrue(rule.resource_required)
                self.assertTrue(rule.version_required)

    def test_covered_effects_have_distinct_writer_and_verifier_domains(self):
        providers = self.runtime.registry.list()

        for capability in AIOS_RUNTIME_CAPABILITY_BY_EFFECT.values():
            with self.subTest(capability=capability):
                writers = [
                    item
                    for item in providers
                    if capability in item.capabilities
                ]
                verifiers = [
                    item
                    for item in providers
                    if f"{capability}.verify" in item.capabilities
                ]
                self.assertEqual(len(writers), 1)
                self.assertEqual(len(verifiers), 1)
                self.assertNotEqual(
                    writers[0].credential_domain,
                    verifiers[0].credential_domain,
                )

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
                    idempotency_key="baa:missing-auth",
                    parameters={"subject_ref": "employee:1"},
                    effect_class="external-effect",
                )
            )

        with self.assertRaises(PermissionError):
            asyncio.run(invoke_without_authorization())


if __name__ == "__main__":
    unittest.main()
