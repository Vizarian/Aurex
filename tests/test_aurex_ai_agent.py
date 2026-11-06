"""Offline tests for the GitHub Models issue agent."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import aurex_ai_agent as agent


class AgentTests(unittest.TestCase):
    def test_issue_event(self):
        self.assertEqual(agent.issue_number({"action": "opened", "issue": {"number": 9}}), 9)
        self.assertIsNone(agent.issue_number({"action": "edited", "issue": {"number": 9}}))
        self.assertIsNone(agent.issue_number({"action": "opened", "issue": {"number": 9, "pull_request": {}}}))

    def test_end_to_end_mocked_model(self):
        with tempfile.TemporaryDirectory() as directory:
            event_file = Path(directory) / "event.json"
            event_file.write_text(json.dumps({"action": "opened", "issue": {
                "number": 5, "title": "Improve tests", "body": "Add a test"}}))
            calls = []
            def fake_request(url, token, payload=None):
                calls.append((url, payload))
                if url == agent.MODELS:
                    return {"choices": [{"message": {"content": "Test plan: add unit tests."}}]}
                if "/contents/" in url:
                    import base64
                    return {"content": base64.b64encode(b"def example(): pass").decode()}
                if url.endswith("/comments"):
                    return {"id": 1}
                raise AssertionError("Unexpected request " + url)
            env = {"GITHUB_TOKEN": "fake-token", "GITHUB_REPOSITORY": "example/Aurex",
                   "GITHUB_EVENT_PATH": str(event_file)}
            with patch.dict(os.environ, env), patch.object(agent, "request_json", side_effect=fake_request), patch.object(agent, "STATE", Path(directory) / "receipt.json"):
                agent.run()
            model_calls = [payload for url, payload in calls if url == agent.MODELS]
            self.assertEqual(len(model_calls), 1)
            self.assertIn("def example(): pass", model_calls[0]["messages"][1]["content"])
            self.assertTrue(any(url.endswith("/issues/5/comments") for url, _ in calls))
            receipt = json.loads((Path(directory) / "receipt.json").read_text())
            self.assertTrue(receipt["comment_posted"])
            self.assertEqual(receipt["comment_id"], 1)


if __name__ == "__main__":
    unittest.main()
