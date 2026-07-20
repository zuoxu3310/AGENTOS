from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = PROJECT_ROOT / "tests" / "capabilities.json"


class CapabilityManifestContractTests(unittest.TestCase):
    def test_manifest_ids_are_contiguous_and_describe_behavioral_evidence_routes(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        capabilities = data["capabilities"]
        expected = [f"C{number:02d}" for number in range(1, len(capabilities) + 1)]
        self.assertEqual(expected, [item["id"] for item in capabilities])
        self.assertEqual(len(expected), len({item["id"] for item in capabilities}))

        required = {
            "name",
            "user_visible_contract",
            "decision_sources",
            "deterministic_tests",
            "runtime_evidence_required",
            "live_evidence_required",
        }
        for capability in capabilities:
            with self.subTest(capability=capability["id"]):
                self.assertTrue(required.issubset(capability))
                self.assertTrue(capability["deterministic_tests"])
                self.assertTrue(capability["runtime_evidence_required"])
                self.assertTrue(capability["live_evidence_required"])

    def test_every_manifest_test_anchor_names_a_real_test_method(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for capability in data["capabilities"]:
            for anchor in capability["deterministic_tests"]:
                with self.subTest(capability=capability["id"], anchor=anchor):
                    relative_path, _, test_name = anchor.partition("::")
                    source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
                    method_name = test_name.rsplit("::", 1)[-1]
                    self.assertIn(f"def {method_name}(", source)


if __name__ == "__main__":
    unittest.main()
