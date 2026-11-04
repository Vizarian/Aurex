"""Manual, bounded OpenAI API connectivity test. Never prints credentials."""
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def main():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        print("OPENAI_API_KEY is missing. Add it as a GitHub Actions repository secret.")
        return 2
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    payload = json.dumps({
        "model": model,
        "input": "Reply with exactly AUREX_API_OK",
        "max_output_tokens": 24,
        "store": False,
    }).encode()
    req = Request("https://api.openai.com/v1/responses", data=payload, method="POST",
                  headers={"Authorization": "Bearer " + key,
                           "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            data = json.load(response)
    except HTTPError as exc:
        print("API request failed: HTTP", exc.code, "(check API billing, key, and model access)")
        return 1
    except (URLError, TimeoutError) as exc:
        print("Network request failed:", type(exc).__name__)
        return 1
    outputs = []
    for item in data.get("output", []):
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                outputs.append(part.get("text", ""))
    answer = "".join(outputs).strip()
    ok = answer == "AUREX_API_OK"
    print(json.dumps({"model": model, "response_id": data.get("id"),
                      "test_passed": ok, "usage": data.get("usage", {})}))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
