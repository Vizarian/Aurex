import unittest
from iskra_explore import PHRASE, ROLES, run

class ExplorationTests(unittest.TestCase):
    def test_message_read_and_acknowledged(self):
        result = run()
        self.assertEqual(len(result['acknowledgments']), len(ROLES))
        self.assertTrue(all(x['received'] and x['message'] == PHRASE for x in result['acknowledgments']))

    def test_exploration_progresses(self):
        first, second = run()['explorations']
        self.assertEqual(first['status'], 'verified')
        self.assertEqual(second['status'], 'verified')
        self.assertNotEqual(first['selected_goal'], second['selected_goal'])

if __name__ == '__main__':
    unittest.main()
