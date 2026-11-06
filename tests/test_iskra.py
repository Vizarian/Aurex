"""Offline checks for Iskra's visible decision loop."""
import json
import tempfile
import unittest
from pathlib import Path
from iskra import cycle


class IskraTests(unittest.TestCase):
    def test_selects_goal_and_records_unverified_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = cycle(root / 'state', root / 'STOP')
            self.assertEqual(result['status'], 'proposed')
            self.assertFalse(result['verified'])
            saved = json.loads((root / 'state' / 'last_run.json').read_text())
            self.assertEqual(saved['goal'], result['goal'])

    def test_stop_prevents_state_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'STOP').touch()
            self.assertEqual(cycle(root / 'state', root / 'STOP')['status'], 'stopped')
            self.assertFalse((root / 'state').exists())

    def test_reuses_previous_state_without_claiming_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = cycle(root / 'state', root / 'STOP')
            second = cycle(root / 'state', root / 'STOP')
            self.assertEqual(second['previous_goal'], first['goal'])
            self.assertEqual(second['goal'], first['goal'])


if __name__ == '__main__':
    unittest.main()
