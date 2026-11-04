import tempfile
import unittest
from pathlib import Path
from aurex_core.events import Event
from aurex_core.journal import Journal
from aurex_core.outbox import Outbox
from aurex_core.policy import Policy
from aurex_core.goals import choose_goal, Goal
from aurex_core.runtime import cycle

class AutonomousCycleTests(unittest.TestCase):
    def test_goal_selection(self):
        self.assertEqual(choose_goal((Goal("b", 3), Goal("a", 3))).id, "a")
        self.assertIsNone(choose_goal(blocked=("maintain_continuity", "respond_to_new_messages", "investigate_open_questions", "maintain_health")))

    def test_bounded_dry_run_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            journal = Journal(Path(d) / "events.jsonl")
            outbox = Outbox(Path(d) / "outbox.json")
            events = [Event("postmark", "a", "message", "hi", "t1"), Event("postmark", "b", "message", "hello", "t2")]
            result = cycle(events, journal, outbox, Policy(), max_events=2)
            self.assertEqual(result["outbound_sent"], 0)
            self.assertEqual(len(outbox.list()), 2)
            cycle(events, journal, outbox, Policy(), max_events=2)
            self.assertEqual(len(outbox.list()), 2)
            self.assertEqual(len(journal.read()), 2)

    def test_budget_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            events = [Event("postmark", str(i), "message", "hi", "t") for i in range(4)]
            with self.assertRaises(PermissionError):
                cycle(events, Journal(Path(d)/"journal"), Outbox(Path(d)/"outbox"), Policy(max_actions_per_run=1), max_events=3)

if __name__ == "__main__":
    unittest.main()
