"""Choose an honest fallback when GitHub Models is unavailable.

The fallback runs deterministic investigation only; it never impersonates an LLM.
"""
import json
from pathlib import Path

def choose_fallback(diagnostic, report):
    if diagnostic.get("status") == "valid_model_response":
        return {"mode": "model_available", "reason": "Endpoint returned a valid model response"}
    failures = report.get("failures", [])
    if not isinstance(failures, list):
        raise ValueError("Malformed investigation report")
    if diagnostic.get("status") in ("invalid_model_response", "http_error", "transport_error"):
        return {
            "mode": "offline_investigator",
            "reason": "Model endpoint unavailable or malformed",
            "model_used": False,
            "independent_tasks_available": ["inspect_workflow_metadata", "rank_failures", "archive_evidence"],
            "failures_observed": len(failures),
            "next_check": "Recheck model endpoint on next scheduled run",
            "boundary": "No model reasoning, no credential bypass, no external mutations",
        }
    return {"mode": "halt", "reason": "Unknown diagnostic status; fail closed"}

if __name__ == "__main__":
    diagnostic = json.loads(Path("receipts/executed-action.json").read_text())
    report = json.loads(Path("receipts/live-investigation.json").read_text())
    result = choose_fallback(diagnostic, report)
    Path("receipts/fallback-decision.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
