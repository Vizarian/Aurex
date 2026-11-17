import unittest
from evidence_conflicts import Observation, assess

CLAIM = "A green AI workflow proves a model ran"

class EvidenceConflictTests(unittest.TestCase):
    def test_verified_refutation(self):
        result = assess(CLAIM, [Observation(CLAIM, False, "run-43974557529/jobs", True)])
        self.assertEqual(result["verdict"], "refuted")

    def test_unverified_claim_not_counted(self):
        result = assess(CLAIM, [Observation(CLAIM, True, "rumor", False)])
        self.assertEqual(result["verdict"], "unverified")

    def test_disagreement_is_not_silenced(self):
        result = assess(CLAIM, [
            Observation(CLAIM, True, "source-a", True),
            Observation(CLAIM, False, "source-b", True),
        ])
        self.assertEqual(result["verdict"], "conflicted")
        self.assertEqual(result["opposing_sources"], ["source-b"])

    def test_other_proposition_not_counted(self):
        result = assess(CLAIM, [Observation("Different claim", False, "source", True)])
        self.assertEqual(result["verdict"], "unverified")

    def test_duplicate_source_deduplicated(self):
        result = assess(CLAIM, [
            Observation(CLAIM, False, "run", True),
            Observation(CLAIM, False, "run", True),
        ])
        self.assertEqual(result["opposing_sources"], ["run"])

if __name__ == "__main__":
    unittest.main()
