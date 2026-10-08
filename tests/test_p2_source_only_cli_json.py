"""P2 source-only CLI sidecar must parse as a single JSON document.

This test mocks only the source verifier boundary, not an empirical P2 model
response. It establishes that source-only qualification makes no model call.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_p2_readonly_maintenance_model.py"
WORKLOAD = ROOT / "experiments/p2_readonly_maintenance_v1.json"


class SourceOnlyCliTests(unittest.TestCase):
    def test_emits_one_valid_json_document_without_model_gateway(self):
        spec = importlib.util.spec_from_file_location("p2_readonly_cli", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "source-qualification.json"
            cmd = [
                str(SCRIPT),
                "--workload", str(WORKLOAD),
                "--source-zip", str(Path(tmp) / "original.zip"),
                "--qualify-source-only",
                "--output", str(target),
            ]
            qualified = {
                "schema": "p2-isolated-maintenance-source-qualification-v1",
                "qualified": True,
                "new_model_calls": 0,
            }
            with (
                patch.object(sys, "argv", cmd),
                patch.object(
                    module, "qualify_p2_source_archive", return_value=qualified
                ) as source_check,
                patch.object(
                    module, "make_client", side_effect=AssertionError("model called")
                ) as model_factory,
            ):
                module.main()
            source_check.assert_called_once()
            model_factory.assert_not_called()
            raw = target.read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("\n"))
            self.assertFalse(raw.endswith("\\n"))
            self.assertEqual(json.loads(raw), qualified)
            self.assertEqual(json.JSONDecoder().raw_decode(raw)[1], len(raw.strip()))


if __name__ == "__main__":
    unittest.main()
