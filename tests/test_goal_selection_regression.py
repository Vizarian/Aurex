"""Regression checks for autonomous goal selection."""
import unittest
from aurex_core.goals import Goal, choose_goal


class GoalSelectionTests(unittest.TestCase):
    def test_highest_priority_is_selected(self):
        goals = (Goal('low', 10), Goal('high', 90), Goal('medium', 50))
        self.assertEqual(choose_goal(goals).id, 'high')

    def test_blocked_and_disabled_goals_are_not_selected(self):
        goals = (Goal('blocked', 100), Goal('disabled', 90, enabled=False), Goal('ready', 20))
        self.assertEqual(choose_goal(goals, blocked=('blocked',)).id, 'ready')

    def test_no_eligible_goal_is_safe(self):
        self.assertIsNone(choose_goal((Goal('disabled', 10, enabled=False),)))

    def test_ties_are_deterministic(self):
        self.assertEqual(choose_goal((Goal('z', 10), Goal('a', 10))).id, 'a')


if __name__ == '__main__':
    unittest.main()
