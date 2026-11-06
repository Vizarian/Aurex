import unittest
from iskra_team import Task, run_team


class TeamTests(unittest.TestCase):
    def test_collaboration_and_verification(self):
        events = run_team([Task('a', 'sum', (1, 2)), Task('b', 'sort', (3, 1))])['transcript']
        self.assertEqual(sum(e.get('verified') is True for e in events), 2)
        self.assertEqual(sum(e.get('approved') is True for e in events), 2)

    def test_forbidden_operation_is_blocked(self):
        events = run_team([Task('x', 'network')])['transcript']
        self.assertIn({'agent': 'executor', 'task': 'x', 'status': 'blocked'}, events)
        self.assertFalse(any('result' in e for e in events))

    def test_stop(self):
        self.assertEqual(run_team([Task('x', 'sum', (1,))], stop=True)['transcript'], [])

    def test_budget(self):
        events = run_team([Task('a', 'sum', (1,)), Task('b', 'sum', (2,))], max_tasks=1)['transcript']
        self.assertFalse(any(e.get('task') == 'b' for e in events))

    def test_oversized_input_is_blocked(self):
        events = run_team([Task('large', 'sum', (1000001,))])['transcript']
        self.assertTrue(any(e.get('approved') is False for e in events))


if __name__ == '__main__':
    unittest.main()
