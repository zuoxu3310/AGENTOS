"""Role skill receipts bind a seat to exact native SKILL.md bytes."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "aos_skill_receipt", ROOT / "agent-os/tools/aos_skill_receipt.py"
)
assert SPEC and SPEC.loader
RECEIPT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECEIPT)


class SkillReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="agentos-skills-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        manifest = {"menxia": ["reasoning-causality-review", "evidence-claim-review"]}
        path = self.root / "agent-os/skills/seat-skills.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        for runtime_root in (".agents", ".claude"):
            for name in manifest["menxia"]:
                skill = self.root / runtime_root / "skills" / name / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(f"# {runtime_root}/{name}\n", encoding="utf-8")
        self.original_root = RECEIPT.ROOT
        self.original_manifest = RECEIPT.MANIFEST
        RECEIPT.ROOT = self.root
        RECEIPT.MANIFEST = path
        self.addCleanup(self.restore)

    def restore(self) -> None:
        RECEIPT.ROOT = self.original_root
        RECEIPT.MANIFEST = self.original_manifest

    def test_receipt_records_runtime_names_and_hashes_once(self) -> None:
        self.assertEqual(0, RECEIPT.record("demo", "menxia", "codex"))
        self.assertEqual(0, RECEIPT.record("demo", "menxia", "codex"))
        events = [json.loads(line) for line in
                  (self.root / "agent-os/state/tasks/demo.jsonl").read_text().splitlines()]
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertEqual("skill_load", event["kind"])
        self.assertEqual("ok", event["status"])
        self.assertTrue(event["evidence"].startswith("codex|reasoning-causality-review:"))
        self.assertIn(";evidence-claim-review:", event["evidence"])

    def test_runtime_uses_its_own_skill_tree(self) -> None:
        _, codex = RECEIPT.receipt("menxia", "codex")
        _, claude = RECEIPT.receipt("menxia", "claude")
        self.assertNotEqual(codex, claude)


if __name__ == "__main__":
    unittest.main()
