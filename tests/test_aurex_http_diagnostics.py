"""Offline regression tests for safe HTTP response diagnostics."""
import unittest
from aurex_http_diagnostics import decode_json_response


class DiagnosticsTests(unittest.TestCase):
    def test_valid_json(self):
        self.assertEqual(decode_json_response(b'{"ok": true}', 200, 'application/json', 'model'), {'ok': True})

    def test_non_json_response(self):
        secret = 'SENSITIVE_RESPONSE_BODY'
        with self.assertRaises(ValueError) as raised:
            decode_json_response(secret.encode(), 200, 'text/html; charset=utf-8', 'model')
        message = str(raised.exception)
        self.assertIn('stage=model', message)
        self.assertIn('status=200', message)
        self.assertIn('content_type=text/html', message)
        self.assertNotIn(secret, message)

    def test_empty_response(self):
        with self.assertRaisesRegex(ValueError, 'bytes=0'):
            decode_json_response(b'', 204, '', 'github')


if __name__ == '__main__':
    unittest.main()
