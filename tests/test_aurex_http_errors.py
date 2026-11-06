"""Tests for bounded HTTP failure diagnostics."""
import io
import unittest
import urllib.error
from unittest.mock import patch

import aurex_ai_agent as agent


class HttpErrorTests(unittest.TestCase):
    def test_http_403_has_stage_and_status_without_body(self):
        error = urllib.error.HTTPError(
            agent.MODELS, 403, 'Forbidden', {}, io.BytesIO(b'SENSITIVE_RESPONSE_BODY')
        )
        with patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(RuntimeError) as raised:
                agent.request_json(agent.MODELS, 'fake-token', {'model': 'test'})
        message = str(raised.exception)
        self.assertIn('stage=model', message)
        self.assertIn('status=403', message)
        self.assertNotIn('SENSITIVE_RESPONSE_BODY', message)
        self.assertNotIn('fake-token', message)


if __name__ == '__main__':
    unittest.main()
