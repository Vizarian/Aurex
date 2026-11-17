import unittest
from unittest.mock import patch
from experiments.retry_guard import select_with_history
from experiments.execute_next_action import execute

class BoundedExecutionTests(unittest.TestCase):
    def test_escalation_does_not_call_network(self):
        candidate = {"decision": "diagnose_model_endpoint"}
        decision, ledger = select_with_history(candidate, {"attempts": {"diagnose_model_endpoint": 2}})
        with patch("urllib.request.urlopen", side_effect=AssertionError("Network must not be called")):
            with patch.dict("os.environ", {"GITHUB_TOKEN": "fake"}, clear=False):
                result = execute(decision)
        self.assertEqual(result["status"], "not_applicable")
        self.assertEqual(decision["decision"], "escalate_blocker")
        self.assertEqual(ledger["attempts"]["diagnose_model_endpoint"], 3)

    def test_missing_token_blocks_diagnostic(self):
        with patch.dict("os.environ", {}, clear=True):
            result = execute({"decision": "diagnose_model_endpoint"})
        self.assertEqual(result["status"], "blocked")

if __name__ == "__main__":
    unittest.main()
