import json
import urllib.error
import unittest

from baa_protocol.prospective_transport import ReplaySafeTransportClient
from baa_protocol.prospective_types import ModelResponseError


class ScriptedClient:
    model_id = "scripted"
    interface_mode = "function_tool"

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def generate(self, prompt, *, episode_id, capability_level, phase, regime):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class ReplaySafeTransportClientTests(unittest.TestCase):
    def call(self, client):
        return client.generate(
            "prompt",
            episode_id="E1",
            capability_level=0,
            phase="initial",
            regime="bounded_action_protocol",
        )

    def test_retries_one_decode_failure_then_succeeds(self):
        raw = ScriptedClient(
            [
                json.JSONDecodeError("truncated", "{", 1),
                ("{\"actions\":[]}", {"input_tokens": 1}, 0.01),
            ]
        )
        client = ReplaySafeTransportClient(raw, max_retries=1)

        result = self.call(client)

        self.assertEqual(result[0], '{"actions":[]}')
        self.assertEqual(raw.calls, 2)
        self.assertEqual(client.http_attempts, 2)
        self.assertEqual(client.transport_failures_seen, 1)
        self.assertEqual(client.transport_retries, 1)
        self.assertEqual(client.recovered_transport_calls, 1)

    def test_model_response_error_is_not_retried(self):
        raw = ScriptedClient(
            [
                ModelResponseError("missing required function call"),
                ("unused", {}, 0.0),
            ]
        )
        client = ReplaySafeTransportClient(raw, max_retries=1)

        with self.assertRaises(ModelResponseError):
            self.call(client)

        self.assertEqual(raw.calls, 1)
        self.assertEqual(client.http_attempts, 1)
        self.assertEqual(client.transport_retries, 0)

    def test_explicit_http_error_is_not_retried(self):
        error = urllib.error.HTTPError(
            "http://127.0.0.1:4101/v1/responses",
            502,
            "bad gateway",
            hdrs=None,
            fp=None,
        )
        raw = ScriptedClient([error, ("unused", {}, 0.0)])
        client = ReplaySafeTransportClient(raw, max_retries=1)

        with self.assertRaises(urllib.error.HTTPError):
            self.call(client)

        self.assertEqual(raw.calls, 1)
        self.assertEqual(client.http_attempts, 1)
        self.assertEqual(client.transport_retries, 0)

    def test_second_retryable_failure_escapes_after_one_retry(self):
        raw = ScriptedClient(
            [
                json.JSONDecodeError("first", "{", 1),
                json.JSONDecodeError("second", "{", 1),
            ]
        )
        client = ReplaySafeTransportClient(raw, max_retries=1)

        with self.assertRaises(json.JSONDecodeError):
            self.call(client)

        self.assertEqual(raw.calls, 2)
        self.assertEqual(client.http_attempts, 2)
        self.assertEqual(client.transport_failures_seen, 2)
        self.assertEqual(client.transport_retries, 1)
        self.assertEqual(client.recovered_transport_calls, 0)


if __name__ == "__main__":
    unittest.main()
