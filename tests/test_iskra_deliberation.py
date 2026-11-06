import unittest
from iskra_deliberation import Request, deliberate
from iskra_team import Task

class DeliberationTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(deliberate(Request('sum', (Task('a', 'sum', (2, 3)),)))['status'], 'verified')

    def test_ambiguity(self):
        tasks = (Task('a', 'sum', (2, 3)), Task('b', 'max', (2, 3)))
        result = deliberate(Request('ambiguous', tasks))
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertFalse(any('result' in e for e in result['transcript']))

    def test_denied(self):
        self.assertEqual(deliberate(Request('denied', (Task('a', 'network'),)))['status'], 'blocked')

    def test_mixed(self):
        tasks = (Task('a', 'network'), Task('b', 'sort', (3, 1)))
        self.assertEqual(deliberate(Request('mixed', tasks))['status'], 'verified')

if __name__ == '__main__':
    unittest.main()
