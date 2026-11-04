import json
import os
import unittest
from unittest.mock import patch
import model_probe

class FakeResponse:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return b""

class ProbeTests(unittest.TestCase):
    def test_missing_key_fails_without_network(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("model_probe.urlopen") as network:
                self.assertEqual(model_probe.main(), 2)
                network.assert_not_called()

    def test_valid_response(self):
        payload = {"id":"test","output":[{"content":[{"type":"output_text","text":"AUREX_API_OK"}]}],"usage":{"total_tokens":3}}
        with patch.dict(os.environ, {"OPENAI_API_KEY":"test-placeholder"}, clear=True):
            with patch("model_probe.urlopen") as network:
                network.return_value.__enter__.return_value = FakeJsonResponse(payload)
                self.assertEqual(model_probe.main(), 0)
                req = network.call_args.args[0]
                self.assertEqual(req.full_url, "https://api.openai.com/v1/responses")
                self.assertIn(b'"store": false', req.data)
                self.assertEqual(req.get_header("Authorization"), "Bearer test-placeholder")

class FakeJsonResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, *args):
        return json.dumps(self.payload).encode()

if __name__ == "__main__":
    unittest.main()
