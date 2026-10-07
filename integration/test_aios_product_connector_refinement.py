import unittest
from unittest.mock import AsyncMock

import httpx

from administrative_orchestrator.integrations.credentials import CredentialRef
from administrative_orchestrator.integrations.effect_common import (
    ConnectorResult,
    ConnectorStatus,
    _TransportUnknown,
)
from administrative_orchestrator.integrations.keycloak_effects import (
    KeycloakEffectConnection,
    KeycloakIdentityDisableConnector,
    KeycloakIdentityDisableVerifier,
    KeycloakIdentityEffectConnector,
    KeycloakSessionRevokeConnector,
    KeycloakSessionVerifier,
)
from administrative_orchestrator.integrations.odoo_effects import (
    OdooEffectConnection,
    OdooEmployeeDeactivateConnector,
    OdooEmployeeDeactivateVerifier,
    OdooEmployeeEffectConnector,
)
from world_runtime.execution import CapabilityRequest

from scripts.domains.administrative.production_world_runtime_stack import (
    ProductionEffectProvider,
)


def odoo_base() -> OdooEmployeeEffectConnector:
    return OdooEmployeeEffectConnector(
        OdooEffectConnection(
            base_url="https://odoo.example.test",
            database="company",
            username="writer",
            credential=CredentialRef("odoo:writer", "BAA_TEST_ODOO_SECRET"),
        )
    )


def keycloak_base() -> KeycloakIdentityEffectConnector:
    return KeycloakIdentityEffectConnector(
        KeycloakEffectConnection(
            base_url="https://keycloak.example.test",
            realm="company",
            client_id="writer",
            credential=CredentialRef(
                "keycloak:writer",
                "BAA_TEST_KEYCLOAK_SECRET",
            ),
        )
    )


class ProductConnectorRefinementTests(unittest.IsolatedAsyncioTestCase):
    async def test_runtime_request_identity_is_connector_reconciliation_identity(self):
        class Connector:
            def __init__(self):
                self.invoked = []
                self.reconciled = []

            async def invoke(self, **kwargs):
                self.invoked.append(kwargs)
                return ConnectorResult(
                    ConnectorStatus.SUCCEEDED,
                    external_operation_ref="external:test",
                )

            async def reconcile(self, request_ref):
                self.reconciled.append(request_ref)
                return ConnectorResult(
                    ConnectorStatus.SUCCEEDED,
                    external_operation_ref="external:test",
                    reconciled=True,
                )

        connector = Connector()
        provider = ProductionEffectProvider(
            provider_id="provider:test",
            name="test",
            capability="administrative.iam.identity.disable.v1",
            family="test",
            execution_domain="test",
            credential_configuration_ref="credential:test",
            network_domain="test",
            connector=connector,
        )
        request = CapabilityRequest(
            id="request:stable-effect:1",
            capability="administrative.iam.identity.disable.v1",
            parameters={"subject_ref": "employee:1"},
            effect_class="external-effect",
        )

        result = await provider.invoke(request, None)
        recovered = await provider.reconcile(request.id)

        self.assertEqual(result.request_id, request.id)
        self.assertEqual(connector.invoked[0]["request_ref"], request.id)
        self.assertEqual(connector.invoked[0]["subject_ref"], "employee:1")
        self.assertEqual(connector.reconciled, [request.id])
        self.assertIsNotNone(recovered)
        self.assertTrue(recovered.reconciled)

    async def test_odoo_deactivate_lost_ack_reconciles_without_second_write(self):
        base = odoo_base()
        connector = OdooEmployeeDeactivateConnector(base)
        request_ref = "request:odoo-deactivate:1"

        connector._read = AsyncMock(
            return_value={
                "id": 42,
                "active": True,
                "x_administrative_deactivate_request_ref": False,
            }
        )
        base._execute_kw = AsyncMock(
            side_effect=_TransportUnknown("simulated lost acknowledgement")
        )

        first = await connector.invoke(
            request_ref=request_ref,
            subject_ref="odoo:hr.employee:42",
            parameters={},
        )

        self.assertIs(first.status, ConnectorStatus.UNKNOWN)
        self.assertEqual(base._execute_kw.await_count, 1)
        write_args = base._execute_kw.await_args.args
        self.assertEqual(write_args[0:2], ("hr.employee", "write"))
        self.assertEqual(
            write_args[2],
            [
                [42],
                {
                    "active": False,
                    "x_administrative_deactivate_request_ref": request_ref,
                },
            ],
        )

        base._execute_kw.reset_mock()
        base._lookup = AsyncMock(return_value=[{"id": 42}])
        connector._read = AsyncMock(return_value={"id": 42, "active": False})

        recovered = await connector.reconcile(request_ref)

        self.assertIsNotNone(recovered)
        self.assertIs(recovered.status, ConnectorStatus.SUCCEEDED)
        self.assertTrue(recovered.reconciled)
        base._execute_kw.assert_not_awaited()

        observed = await OdooEmployeeDeactivateVerifier(connector).observe(
            subject_ref="employee:42",
            expected_postcondition={
                "employee_external_ref": "odoo:hr.employee:42",
                "active": False,
            },
        )
        self.assertEqual(
            observed.observed_postcondition,
            {
                "target_system": "hris",
                "operation": "employee.deactivate",
                "subject_ref": "employee:42",
                "active": False,
            },
        )

    async def test_odoo_deactivate_rejects_product_request_identity_rebound(self):
        base = odoo_base()
        connector = OdooEmployeeDeactivateConnector(base)
        connector._read = AsyncMock(
            return_value={
                "id": 42,
                "active": False,
                "x_administrative_deactivate_request_ref": "request:other",
            }
        )
        base._execute_kw = AsyncMock()

        result = await connector.invoke(
            request_ref="request:current",
            subject_ref="odoo:hr.employee:42",
            parameters={},
        )

        self.assertIs(result.status, ConnectorStatus.FAILED)
        self.assertEqual(result.error_code, "ConflictingExternalRequestIdentity")
        base._execute_kw.assert_not_awaited()

    async def test_keycloak_disable_lost_ack_reconciles_without_second_write(self):
        base = keycloak_base()
        connector = KeycloakIdentityDisableConnector(base)
        request_ref = "request:keycloak-disable:1"
        user = {
            "id": "user-1",
            "username": "alice",
            "enabled": True,
            "attributes": {
                "administrative_subject_ref": ["employee:1"],
                "preserve_me": ["yes"],
            },
        }
        base._find_by_attribute = AsyncMock(return_value=[{"id": "user-1"}])
        base._get_user = AsyncMock(return_value=user)
        base._request = AsyncMock(return_value=httpx.Response(503))

        first = await connector.invoke(
            request_ref=request_ref,
            subject_ref="employee:1",
            parameters={},
        )

        self.assertIs(first.status, ConnectorStatus.UNKNOWN)
        self.assertEqual(base._request.await_count, 1)
        self.assertEqual(base._request.await_args.args[0], "PUT")
        body = base._request.await_args.kwargs["json_body"]
        self.assertFalse(body["enabled"])
        self.assertEqual(
            body["attributes"]["administrative_disable_request_ref"],
            [request_ref],
        )
        self.assertEqual(body["attributes"]["preserve_me"], ["yes"])

        base._request.reset_mock()
        base._find_by_attribute = AsyncMock(return_value=[{"id": "user-1"}])
        base._get_user = AsyncMock(
            return_value={
                **user,
                "enabled": False,
                "attributes": {
                    **user["attributes"],
                    "administrative_disable_request_ref": [request_ref],
                },
            }
        )

        recovered = await connector.reconcile(request_ref)

        self.assertIsNotNone(recovered)
        self.assertIs(recovered.status, ConnectorStatus.SUCCEEDED)
        self.assertTrue(recovered.reconciled)
        base._request.assert_not_awaited()

        observed = await KeycloakIdentityDisableVerifier(base).observe(
            subject_ref="employee:1",
            expected_postcondition={"enabled": False},
        )
        self.assertEqual(
            observed.observed_postcondition,
            {
                "target_system": "iam",
                "operation": "identity.disable",
                "subject_ref": "employee:1",
                "enabled": False,
            },
        )

    async def test_keycloak_disable_rejects_product_request_identity_rebound(self):
        base = keycloak_base()
        connector = KeycloakIdentityDisableConnector(base)
        base._find_by_attribute = AsyncMock(return_value=[{"id": "user-1"}])
        base._get_user = AsyncMock(
            return_value={
                "id": "user-1",
                "username": "alice",
                "enabled": False,
                "attributes": {
                    "administrative_subject_ref": ["employee:1"],
                    "administrative_disable_request_ref": ["request:other"],
                },
            }
        )
        base._request = AsyncMock()

        result = await connector.invoke(
            request_ref="request:current",
            subject_ref="employee:1",
            parameters={},
        )

        self.assertIs(result.status, ConnectorStatus.FAILED)
        self.assertEqual(result.error_code, "ConflictingExternalRequestIdentity")
        base._request.assert_not_awaited()

    async def test_keycloak_session_lost_ack_reconciles_without_second_logout(self):
        base = keycloak_base()
        connector = KeycloakSessionRevokeConnector(base)
        request_ref = "request:keycloak-sessions:1"
        user = {
            "id": "user-1",
            "username": "alice",
            "enabled": False,
            "attributes": {
                "administrative_subject_ref": ["employee:1"],
                "preserve_me": ["yes"],
            },
        }
        base._find_by_attribute = AsyncMock(return_value=[{"id": "user-1"}])
        base._get_user = AsyncMock(return_value=user)
        base._request = AsyncMock(
            side_effect=[
                httpx.Response(204),
                httpx.Response(200, json=[{"id": "session-1"}]),
                httpx.Response(503),
            ]
        )

        first = await connector.invoke(
            request_ref=request_ref,
            subject_ref="employee:1",
            parameters={},
        )

        self.assertIs(first.status, ConnectorStatus.UNKNOWN)
        self.assertEqual(base._request.await_count, 3)
        marker_call, session_call, logout_call = base._request.await_args_list
        self.assertEqual(marker_call.args[0], "PUT")
        self.assertEqual(
            marker_call.kwargs["json_body"]["attributes"][
                "administrative_session_revoke_request_ref"
            ],
            [request_ref],
        )
        self.assertEqual(session_call.args[0], "GET")
        self.assertEqual(logout_call.args[0], "POST")
        self.assertTrue(logout_call.args[1].endswith("/user-1/logout"))

        base._find_by_attribute = AsyncMock(return_value=[{"id": "user-1"}])
        base._request = AsyncMock(return_value=httpx.Response(200, json=[]))

        recovered = await connector.reconcile(request_ref)

        self.assertIsNotNone(recovered)
        self.assertIs(recovered.status, ConnectorStatus.SUCCEEDED)
        self.assertTrue(recovered.reconciled)
        self.assertEqual(base._request.await_count, 1)
        self.assertEqual(base._request.await_args.args[0], "GET")

        observed = await KeycloakSessionVerifier(base).observe(
            subject_ref="employee:1",
            expected_postcondition={"active_sessions": 0},
        )
        self.assertEqual(
            observed.observed_postcondition,
            {
                "target_system": "iam",
                "operation": "sessions.revoke",
                "subject_ref": "employee:1",
                "active_sessions": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()
