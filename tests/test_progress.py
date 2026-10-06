import io
import json
import time
import unittest

from baa_protocol.progress import ProgressModelClient


class _FakeClient:
    model_id = "fake-model"
    interface_mode = "fake-interface"

    def generate(self, prompt, **kwargs):
        time.sleep(0.02)
        return "{}", {}, 0.02


class ProgressModelClientTests(unittest.TestCase):
    def test_proxy_preserves_attributes_and_result(self):
        stream = io.StringIO()
        with ProgressModelClient(
            _FakeClient(),
            label="test",
            heartbeat_seconds=1.0,
            stream=stream,
        ) as client:
            self.assertEqual(client.model_id, "fake-model")
            result = client.generate(
                "prompt",
                episode_id="E1",
                capability_level=2,
                phase="adaptive-1",
                regime="bounded_action_protocol",
            )
        self.assertEqual(result, ("{}", {}, 0.02))

        events = [
            json.loads(line)
            for line in stream.getvalue().splitlines()
            if line.strip()
        ]
        names = [event["progress_event"] for event in events]
        self.assertEqual(names[0], "study_started")
        self.assertIn("model_call_started", names)
        self.assertIn("model_call_completed", names)
        self.assertEqual(names[-1], "study_finished")
        completed = next(
            event for event in events
            if event["progress_event"] == "model_call_completed"
        )
        self.assertEqual(completed["episode_id"], "E1")
        self.assertEqual(completed["phase"], "adaptive-1")

    def test_heartbeat_reports_inflight_call(self):
        stream = io.StringIO()
        with ProgressModelClient(
            _FakeClient(),
            label="heartbeat-test",
            heartbeat_seconds=0.005,
            stream=stream,
        ) as client:
            client.generate("prompt", episode_id="E2", phase="initial-shared")
        events = [
            json.loads(line)
            for line in stream.getvalue().splitlines()
            if line.strip()
        ]
        heartbeats = [
            event for event in events
            if event["progress_event"] == "heartbeat"
        ]
        self.assertTrue(heartbeats)
        self.assertTrue(
            any(
                event["current"]
                and event["current"]["episode_id"] == "E2"
                for event in heartbeats
            )
        )


if __name__ == "__main__":
    unittest.main()
