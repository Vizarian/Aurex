"""Execute safe, read-only diagnostic tasks selected by Aurex.

Never logs authorization headers, response bodies, or credentials.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://models.github.ai/inference/chat/completions"

def execute(decision):
    if decision.get("decision") != "diagnose_model_endpoint":
        return {"status": "not_applicable", "decision": decision.get("decision")}
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {"status": "blocked", "reason": "missing GitHub token"}
    payload = json.dumps({
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "Reply with exactly OK"}],
        "max_tokens": 8,
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Aurex-readonly-diagnostic",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read(4096)
            content_type = response.headers.get("Content-Type", "")
            valid_json = False
            try:
                parsed = json.loads(body)
                valid_json = isinstance(parsed, dict) and "choices" in parsed
            except (ValueError, UnicodeDecodeError):
                pass
            return {
                "status": "valid_model_response" if valid_json else "invalid_model_response",
                "http_status": response.status,
                "content_type": content_type,
                "response_bytes_read": len(body),
                "json_with_choices": valid_json,
                "response_body_recorded": False,
            }
    except urllib.error.HTTPError as exc:
        return {"status": "http_error", "http_status": exc.code,
                "content_type": exc.headers.get("Content-Type", ""),
                "response_body_recorded": False}
    except (OSError, TimeoutError) as exc:
        return {"status": "transport_error", "error_type": type(exc).__name__}

if __name__ == "__main__":
    decision = json.loads(Path("receipts/next-action.json").read_text())
    result = execute(decision)
    path = Path("receipts/executed-action.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
