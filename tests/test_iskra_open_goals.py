import unittest
from iskra_open_goals import experiment

class OpenGoalTests(unittest.TestCase):
    def test_initial_selection(self):
        result = experiment((2, 3, 5))
        self.assertEqual(result['selected_goal'], 'measure aggregate')
        self.assertEqual(result['result'], 10)
        self.assertEqual(result['status'], 'verified')

    def test_next_goal_after_completion(self):
        result = experiment((2, 3, 5), completed=('measure aggregate',))
        self.assertEqual(result['selected_goal'], 'inspect data distribution')
        self.assertEqual(result['result'], [2, 3, 5])

    def test_no_remaining_goals(self):
        completed = ('measure aggregate', 'inspect data distribution', 'identify upper bound')
        self.assertEqual(experiment((2, 3), completed=completed)['status'], 'idle')

    def test_stop(self):
        self.assertEqual(experiment((2, 3), stop=True)['status'], 'stopped')

    def test_out_of_bounds(self):
        self.assertEqual(experiment((1000001,))['status'], 'idle')

if __name__ == '__main__':
    unittest.main()
