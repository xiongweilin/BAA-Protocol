"""Lossless provenance test for the original qualified P2 real-model result.

This preserves a JSON result artifact after short GitHub Actions retention.
The file is base64-encoded gzip bytes of original result.json (no edits);
the original ZIP retains separate sidecar/provenance material.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENCODED = ROOT / "experiments/evidence/p2-readonly-maintenance-model-v1-result.json.gz.b64"
EXPECTED_RESULT_SHA256 = "0d9b6f19a42f8f42b0c083ed76e8c39a696056f7d567a50453d83808154e452c"


class ArchivedP2ModelResultTests(unittest.TestCase):
    def test_lossless_original_result_bytes_and_all_45_rows(self):
        compressed = base64.b64decode(ENCODED.read_text(encoding="ascii"), validate=False)
        raw = gzip.decompress(compressed)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_RESULT_SHA256)
        result = json.loads(raw)
        self.assertEqual(result["physical_model_calls"], 11)
        self.assertEqual(result["model_call_error_types"], [])
        self.assertEqual(result["tool_interface"], "function_tool")
        self.assertTrue(result["source_qualification"]["qualified"])
        self.assertEqual(len(result["episodes"]), 45)
        self.assertEqual(len({
            (r["episode_id"], r["capability_level"], r["regime"])
            for r in result["episodes"]
        }), 45)
        for cap in ("0", "1", "2"):
            self.assertEqual(
                [result["summary"][cap][reg]["episodes"]
                 for reg in (
                     "self_check", "external_record_audit", "bounded_action_protocol"
                 )],
                [5, 5, 5],
            )
            self.assertEqual(
                [result["summary"][cap][reg]["delegable"]
                 for reg in (
                     "self_check", "external_record_audit", "bounded_action_protocol"
                 )],
                [0, 0, 0] if cap in ("0", "1") else [1, 1, 1],
            )
        self.assertFalse(result["actual_principal_attention_observed"])
        self.assertFalse(result["statistical_external_validity_qualified"])


if __name__ == "__main__":
    unittest.main()
