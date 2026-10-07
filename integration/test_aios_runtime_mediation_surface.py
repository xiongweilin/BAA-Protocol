import inspect
import unittest

from administrative_orchestrator.integrations.world_runtime import WorldRuntimeBridge
from autonomous_development.adapters.world_runtime import WorldRuntimeDevelopmentBridge
from world_runtime import WorldRuntime
from world_runtime.service import create_app


_DISPATCH_MARKERS = {
    "runtime.invoke(": "canonical-invoke",
    "runtime.effect_boundary.prepare(": "domain-effect-prepare",
    "runtime.effect_boundary.start(": "domain-effect-start",
    "runtime.effect_boundary.record_result(": "domain-effect-result",
    "runtime.recovery.recover(": "reconcile",
}

_EXPECTED_RUNTIME_SURFACE = {
    ("POST", "/v1/invoke"),
    ("POST", "/v1/domain-effects/prepare"),
    ("POST", "/v1/domain-effects/{idempotency_key}/start"),
    ("POST", "/v1/domain-effects/{idempotency_key}/result"),
    ("POST", "/v1/reconcile/{idempotency_key}"),
}


class RuntimeMediationSurfaceTests(unittest.TestCase):
    def test_provider_dispatch_and_recovery_http_surface_is_frozen(self):
        app = create_app(WorldRuntime.sqlite(runtime_id="runtime:baa-surface"))
        observed: dict[tuple[str, str], tuple[str, ...]] = {}

        for route in app.routes:
            endpoint = getattr(route, "endpoint", None)
            path = getattr(route, "path", None)
            methods = set(getattr(route, "methods", ()) or ())
            if endpoint is None or path is None:
                continue
            try:
                source = inspect.getsource(endpoint)
            except (OSError, TypeError):
                continue
            markers = tuple(
                label
                for needle, label in _DISPATCH_MARKERS.items()
                if needle in source
            )
            if not markers:
                continue

            self.assertIn(
                "_request_context(",
                source,
                msg=f"{path} crosses Runtime provider state without request context",
            )
            self.assertIn(
                "_assert_transition_authority(",
                source,
                msg=f"{path} crosses Runtime provider state without transition authority",
            )
            if "canonical-invoke" in markers or "domain-effect-prepare" in markers:
                self.assertIn(
                    "_assert_effect_authority(",
                    source,
                    msg=f"{path} can prepare/release an effect without effect authority",
                )

            for method in methods:
                if method in {"POST", "PUT", "PATCH", "DELETE"}:
                    observed[(method, path)] = markers

        self.assertEqual(set(observed), _EXPECTED_RUNTIME_SURFACE)

    def test_administrative_effect_bridge_uses_canonical_runtime_invoke(self):
        source = inspect.getsource(WorldRuntimeBridge.execute_effect)

        self.assertIn('"/v1/invoke"', source)
        self.assertNotIn("/v1/domain-effects/", source)
        self.assertIn('"authorization_id": runtime_auth["id"]', source)
        self.assertIn('"subject_version_refs": [', source)
        self.assertIn('"idempotency_key": self.idempotency_key_for_effect', source)

    def test_development_provider_call_occurs_only_after_runtime_dispatch_grant(self):
        source = inspect.getsource(WorldRuntimeDevelopmentBridge.execute_external_effect)

        prepare = source.index('"/v1/domain-effects/prepare"')
        start = source.index('f"/v1/domain-effects/{idempotency_key}/start"')
        dispatch_guard = source.index('if started.get("dispatch_allowed") is not True')
        provider_call = source.index("result = invoke()")
        result_record = source.index(
            'f"/v1/domain-effects/{idempotency_key}/result"',
            provider_call,
        )

        self.assertLess(prepare, start)
        self.assertLess(start, dispatch_guard)
        self.assertLess(dispatch_guard, provider_call)
        self.assertLess(provider_call, result_record)
        self.assertNotIn('"/v1/invoke"', source)


if __name__ == "__main__":
    unittest.main()
