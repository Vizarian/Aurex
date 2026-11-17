"""Inspect live GitHub Actions runs and produce an evidence-backed failure report.

No fixtures, no model call, no issue posting. The report cites real run URLs.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com/repos/kalinkacs/Aurex"

def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Aurex-live-investigator"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
        return json.load(response)

def investigate():
    runs = get_json(API + "/actions/runs?per_page=30")["workflow_runs"]
    findings = []
    for run in runs:
        if run.get("status") != "completed" or run.get("conclusion") != "failure":
            continue
        jobs = get_json(API + "/actions/runs/" + str(run["id"]) + "/jobs")["jobs"]
        failed_steps = []
        for job in jobs:
            for step in job.get("steps") or []:
                if step.get("conclusion") == "failure":
                    failed_steps.append({"job": job["name"], "step": step["name"]})
        findings.append({
            "workflow": run["name"], "run_id": run["id"],
            "run_url": run["html_url"], "conclusion": run["conclusion"],
            "failed_steps": failed_steps,
            "hypothesis": "Investigate the named failed steps; job metadata alone does not establish root cause",
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": API + "/actions/runs?per_page=30",
        "runs_inspected": len(runs),
        "failures": findings,
        "status": "observed" if runs else "no_data",
        "model_invoked": False,
        "limitations": "Metadata inspection only; no model reasoning or automatic fixes",
    }

if __name__ == "__main__":
    report = investigate()
    output = Path("receipts/live-investigation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
