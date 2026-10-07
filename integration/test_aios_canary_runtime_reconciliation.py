import unittest

import httpx
from autonomous_development.adapters.world_runtime import (
    WorldRuntimeBoundaryError,
    WorldRuntimeDevelopmentBridge,
)
from fastapi.testclient import TestClient
from world_runtime import WorldRuntime
from world_runtime.service import create_app

from world_runtime_refinement import assert_ambiguous_effect_fenced


class TestClientTransport(httpx.BaseTransport):
    def __init__(self, client: TestClient) -> None:
        self.client = client

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        body = request.read()
        response = self.client.request(
            request.method,
            str(request.url),
            content=body,
            headers=dict(request.headers),
        )
        return httpx.Response(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            request=request,
        )


class CanaryRuntimeReconciliationTests(unittest.TestCase):
    def test_unknown_traffic_effect_requires_reconciliation_before_redispatch(self):
        runtime = WorldRuntime.sqlite(runtime_id="runtime:baa-canary-reconcile")
        runtime.identity.bind_bearer_token(
            principal="controller:autonomous-development",
            token="development-runtime-token",
            credential_id="credential:autonomous-development",
        )
        app = create_app(runtime)
        calls = {"count": 0}
        key = "development:traffic:apply:experiment-1:stage-0"

        with TestClient(app) as client:
            bridge = WorldRuntimeDevelopmentBridge(
                "http://testserver",
                transport=TestClientTransport(client),
                bearer_token="development-runtime-token",
            )
            bridge.ensure_contracts()

            def ambiguous_provider():
                calls["count"] += 1
                raise TimeoutError("simulated lost acknowledgement")

            with self.assertRaises(TimeoutError):
                bridge.execute_external_effect(
                    target_id="target:1",
                    capability="development.traffic.apply",
                    resource="traffic:target:1",
                    idempotency_key=key,
                    parameters={
                        "experiment_id": "experiment:1",
                        "stage_index": 0,
                        "candidate_weight_percent": 10,
                    },
                    subject_version_refs=[
                        "release:release:0",
                        "deployment:deployment:1",
                    ],
                    provider_id="development:traffic-director",
                    provider_version="1",
                    invoke=ambiguous_provider,
                    encode=lambda value: dict(value),
                    decode=lambda value: dict(value),
                )

            effect = runtime.effect_boundary.get(key)
            assert_ambiguous_effect_fenced(effect)
            self.assertEqual(calls["count"], 1)

            def would_redispatch():
                calls["count"] += 1
                return {"candidate_weight_percent": 10}

            with self.assertRaises(WorldRuntimeBoundaryError):
                bridge.execute_external_effect(
                    target_id="target:1",
                    capability="development.traffic.apply",
                    resource="traffic:target:1",
                    idempotency_key=key,
                    parameters={
                        "experiment_id": "experiment:1",
                        "stage_index": 0,
                        "candidate_weight_percent": 10,
                    },
                    subject_version_refs=[
                        "release:release:0",
                        "deployment:deployment:1",
                    ],
                    provider_id="development:traffic-director",
                    provider_version="1",
                    invoke=would_redispatch,
                    encode=lambda value: dict(value),
                    decode=lambda value: dict(value),
                )

        self.assertEqual(calls["count"], 1)


if __name__ == "__main__":
    unittest.main()
