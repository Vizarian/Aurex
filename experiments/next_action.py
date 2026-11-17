"""Select a concrete next action from real investigation evidence.

This is a bounded, deterministic autonomous decision policy, not an LLM.
Only recommends actions; never modifies code, secrets or external issues.
"""
import json
from pathlib import Path

def choose(report):
    if not isinstance(report, dict) or not isinstance(report.get("failures"), list):
        raise ValueError("Expected a live-investigation report")
    failures = sorted(report["failures"], key=lambda x: x.get("run_id", 0), reverse=True)
    for failure in failures:
        steps = failure.get("failed_steps") or []
        for step in steps:
            name = str(step.get("step", ""))
            if "Model review" in name or "model" in name.lower():
                return {
                    "decision": "diagnose_model_endpoint",
                    "priority": "high",
                    "source_run": failure.get("run_url"),
                    "failed_step": name,
                    "next_action": "Inspect response media type, length and endpoint configuration without logging response bodies or credentials",
                    "reason": "Model invocation failure blocks independent model reasoning",
                    "requires_approval_for_external_mutation": True,
                }
        if steps:
            return {
                "decision": "inspect_failed_job",
                "priority": "normal",
                "source_run": failure.get("run_url"),
                "failed_step": str(steps[0].get("step", "")),
                "next_action": "Read job logs and formulate a minimal reproducible test",
                "reason": "Observed failure needs diagnosis before changes",
                "requires_approval_for_external_mutation": True,
            }
    return {
        "decision": "monitor",
        "priority": "low",
        "source_run": None,
        "next_action": "Inspect next scheduled workflow results",
        "reason": "No failed jobs observed in the report",
        "requires_approval_for_external_mutation": False,
    }

if __name__ == "__main__":
    source = Path("receipts/live-investigation.json")
    report = json.loads(source.read_text(encoding="utf-8"))
    decision = choose(report)
    target = Path("receipts/next-action.json")
    target.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, indent=2))
