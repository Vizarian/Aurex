import copy
import json
import unittest
from pathlib import Path
from seam_evaluator import evaluate

CASE = json.loads(Path("fixtures/omission_case.json").read_text(encoding="utf-8"))

class SeamEvidenceTests(unittest.TestCase):
    def test_omission_fixture(self):
        actual = evaluate(CASE)
        for key, expected in CASE["expected"].items():
            self.assertEqual(actual[key], expected)

    def test_no_correction_does_not_imply_truth(self):
        case = copy.deepcopy(CASE)
        case["events"] = case["events"][:2]
        result = evaluate(case)
        self.assertIsNone(result["original_assertion_supported"])
        self.assertFalse(result["unresolved_conflict"])

    def test_correction_cannot_reference_missing_record(self):
        case = copy.deepcopy(CASE)
        case["events"][-1]["corrects"] = "nonexistent"
        with self.assertRaises(ValueError):
            evaluate(case)

    def test_duplicate_ids_rejected(self):
        case = copy.deepcopy(CASE)
        case["events"][-1]["id"] = "e1"
        with self.assertRaises(ValueError):
            evaluate(case)

if __name__ == "__main__":
    unittest.main()
