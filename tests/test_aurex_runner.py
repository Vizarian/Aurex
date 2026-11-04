import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aurex_runner


class RunnerTests(unittest.TestCase):
    def test_first_run_and_replay_are_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(aurex_runner, "STATE", Path(folder)):
                aurex_runner.main()
                first = json.loads((Path(folder) / "last_run.json").read_text())
                self.assertEqual(first["outbound_sent"], 0)
                self.assertTrue(first["verification"]["journal_contains_processed_events"])
                self.assertTrue(first["verification"]["drafts_only"])
                aurex_runner.main()
                second = json.loads((Path(folder) / "last_run.json").read_text())
                self.assertEqual(second["outbound_sent"], 0)
                self.assertEqual(len((Path(folder) / "events.jsonl").read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
