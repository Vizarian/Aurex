"""Offline regression tests for research baton continuity."""
import copy
import tempfile
import unittest
from pathlib import Path
from research_baton import read, write

BASE = {
    "schema_version": 1, "question_id": "continuity-001",
    "question": "Can a successor correct an inherited false conclusion?",
    "current_claim": "Green workflow means model executed",
    "counterevidence": ["Run 43974557529: analyze job skipped"],
    "next_test": "Inspect job conclusions and issue comments",
    "alternatives_rejected": [], "uncertainty": "Model execution unverified",
    "status": "open", "revision": 1,
}

class BatonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "state" / "baton.json"

    def test_restart_and_correction(self):
        write(self.path, copy.deepcopy(BASE))
        successor = read(self.path)
        successor["current_claim"] = "Green workflow alone does not prove model execution"
        successor["revision"] = 2
        successor["counterevidence"].append("Independent job metadata confirms skip")
        write(self.path, successor, expected_revision=1)
        self.assertEqual(read(self.path)["revision"], 2)
        self.assertEqual(len(read(self.path)["counterevidence"]), 2)

    def test_stale_revision_rejected(self):
        write(self.path, copy.deepcopy(BASE))
        changed = copy.deepcopy(BASE)
        changed["revision"] = 2
        with self.assertRaisesRegex(ValueError, "stale"):
            write(self.path, changed, expected_revision=0)
        self.assertEqual(read(self.path)["revision"], 1)

    def test_evidence_cannot_be_erased(self):
        write(self.path, copy.deepcopy(BASE))
        changed = copy.deepcopy(BASE)
        changed["revision"] = 2
        changed["counterevidence"] = []
        with self.assertRaisesRegex(ValueError, "erase"):
            write(self.path, changed, expected_revision=1)

    def test_malformed_baton_rejected(self):
        bad = copy.deepcopy(BASE)
        bad["counterevidence"] = ["valid", 42]
        with self.assertRaisesRegex(ValueError, "list items"):
            write(self.path, bad)

    def test_new_baton_requires_revision_one(self):
        bad = copy.deepcopy(BASE)
        bad["revision"] = 2
        with self.assertRaisesRegex(ValueError, "revision one"):
            write(self.path, bad)

if __name__ == "__main__":
    unittest.main()
