import tempfile
import unittest
from pathlib import Path
from aurex_core.events import Event
from aurex_core.initiative import propose, prioritize
from aurex_core.stop import assert_running, Stopped

class InitiativeTests(unittest.TestCase):
    def test_proposes_from_events(self):
        events = [Event("postmark","1","message","hello","t"),Event("github","2","failure","job failed","t")]
        tasks = prioritize(propose(events))
        self.assertEqual([t.goal for t in tasks], ["maintain_health","respond_to_new_messages"])
        self.assertTrue(all(t.status == "proposed" for t in tasks))

    def test_same_event_same_task(self):
        event = Event("postmark","1","message","hello","t")
        self.assertEqual(propose([event,event]), propose([event]))

    def test_stop_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"STOP"
            assert_running(path)
            path.touch()
            with self.assertRaises(Stopped):
                assert_running(path)

if __name__ == "__main__":
    unittest.main()
