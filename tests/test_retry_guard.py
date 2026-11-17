import unittest
from experiments.retry_guard import select_with_history

class RetryGuardTests(unittest.TestCase):
    def test_first_attempt_allowed(self):
        decision, ledger = select_with_history({"decision": "diagnose_model_endpoint"}, {"attempts": {}})
        self.assertEqual(decision["decision"], "diagnose_model_endpoint")
        self.assertEqual(ledger["attempts"]["diagnose_model_endpoint"], 1)

    def test_repeated_failure_escalates(self):
        decision, ledger = select_with_history({"decision": "diagnose_model_endpoint"}, {"attempts": {"diagnose_model_endpoint": 2}})
        self.assertEqual(decision["decision"], "escalate_blocker")
        self.assertEqual(ledger["attempts"]["diagnose_model_endpoint"], 3)

    def test_other_actions_not_blocked(self):
        decision, _ = select_with_history({"decision": "inspect_failed_job"}, {"attempts": {"diagnose_model_endpoint": 99}})
        self.assertEqual(decision["decision"], "inspect_failed_job")

    def test_invalid_ledger_fails_closed(self):
        with self.assertRaises(ValueError):
            select_with_history({"decision": "monitor"}, {"attempts": {"monitor": -1}})

if __name__ == "__main__":
    unittest.main()
