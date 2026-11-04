"""Aurex: bounded AI reasoning on GitHub issues via GitHub Models.

Requires GITHUB_TOKEN and a repository with GitHub Models access.
No secrets are sent in prompts; no automatic code changes.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
MODELS = "https://models.github.ai/inference/chat/completions"
STATE = Path("state/agent/ai_last_run.json")
SYSTEM = (
    "You are Aurex, a practical autonomous software engineering agent. "
    "Analyze the assigned GitHub issue independently. Return concise Markdown "
    "with: objective, diagnosis, concrete implementation steps, test strategy, "
    "and risks. Be precise about what you have NOT executed. Never ask for "
    "passwords or secrets. Do not claim to have changed code."
)

def request_json(url, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "Aurex-agent",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.load(response)

def issue_number(event):
    if event.get("action") not in ("opened", "reopened", "labeled"):
        return None
    issue = event.get("issue") or {}
    if "pull_request" in issue:
        return None
    return issue.get("number")

def run():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not token or "/" not in repo:
        raise RuntimeError("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    event = json.loads(Path(event_path).read_text()) if event_path else {}
    number = issue_number(event)
    if not number:
        print("No eligible issue event; no model request made")
        return
    issue = event["issue"]
    title = str(issue.get("title", ""))[:250]
    body = str(issue.get("body") or "")[:8000]
    prompt = "Repository: " + repo + "\nIssue #" + str(number) + "\nTitle: " + title + "\nDescription:\n" + body
    result = request_json(MODELS, token, {
        "model": os.environ.get("AUREX_MODEL", "openai/gpt-4o-mini"),
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
        "temperature": 0.2, "max_tokens": 1200,
    })
    answer = result["choices"][0]["message"]["content"]
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Model returned no text")
    comment = "### Aurex autonomous analysis\n\n" + answer[:12000] + (
        "\n\n---\n_Automated analysis, not a verified code change._"
    )
    request_json(API + "/repos/" + repo + "/issues/" + str(number) + "/comments",
                 token, {"body": comment})
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "issue": number, "model": os.environ.get("AUREX_MODEL", "openai/gpt-4o-mini"),
        "comment_posted": True, "code_modified": False,
    }, indent=2) + "\n")
    print("AUREX_AI_RESPONSE_POSTED issue=" + str(number))

if __name__ == "__main__":
    try:
        run()
    except (KeyError, ValueError, OSError, urllib.error.HTTPError) as exc:
        print("AUREX_AI_FAILED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
