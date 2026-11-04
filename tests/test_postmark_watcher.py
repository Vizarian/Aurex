import unittest
from postmark_watcher import inspect

class WatcherTests(unittest.TestCase):
    def test_first_observation_is_not_an_event(self):
        result = inspect(b"# Doorstep\nhello", {}, "2026-11-04T00:00:00Z")
        self.assertFalse(result["changed"])
        self.assertEqual(result["checks"], 1)

    def test_repeat_is_not_a_change(self):
        first = inspect(b"# Doorstep\nhello", {}, "t1")
        second = inspect(b"# Doorstep\nhello", first, "t2")
        self.assertFalse(second["changed"])
        self.assertEqual(second["changes_observed"], 0)

    def test_change_is_recorded_once(self):
        first = inspect(b"# Doorstep\nhello", {}, "t1")
        second = inspect(b"# Doorstep\nnew", first, "t2")
        third = inspect(b"# Doorstep\nnew", second, "t3")
        self.assertTrue(second["changed"])
        self.assertFalse(third["changed"])
        self.assertEqual(third["changes_observed"], 1)

    def test_unexpected_format_rejected(self):
        with self.assertRaises(ValueError):
            inspect(b"wrong", {}, "t1")
