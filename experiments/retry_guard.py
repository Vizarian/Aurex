"""Prevent autonomous agent from endlessly repeating a known failed action.

The ledger is a portable JSON artifact. It can be restored by an orchestrator
between runs; without restoration it provides only within-run protection.
"""
import json
from pathlib import Path

def select_with_history(candidate, ledger, max_repeats=2):
    if not isinstance(candidate, dict) or not isinstance(ledger, dict):
        raise ValueError("candidate and ledger must be objects")
    if type(max_repeats) is not int or max_repeats < 1:
        raise ValueError("max_repeats must be positive")
    key = str(candidate.get("decision", ""))
    if not key:
        raise ValueError("decision required")
    attempts = ledger.get("attempts", {})
    if not isinstance(attempts, dict):
        raise ValueError("invalid ledger")
    count = attempts.get(key, 0)
    if type(count) is not int or count < 0:
        raise ValueError("invalid attempt count")
    updated = {"attempts": dict(attempts)}
    updated["attempts"][key] = count + 1
    if count >= max_repeats:
        return ({
            "decision": "escalate_blocker",
            "blocked_action": key,
            "reason": "Repeated attempts without verified recovery",
            "attempts": count + 1,
            "next_action": "Stop retrying this action; preserve evidence and investigate a different failure",
        }, updated)
    return candidate, updated

if __name__ == "__main__":
    candidate = json.loads(Path("receipts/next-action.json").read_text())
    path = Path("receipts/attempt-ledger.json")
    ledger = json.loads(path.read_text()) if path.exists() else {"attempts": {}}
    decision, ledger = select_with_history(candidate, ledger)
    path.write_text(json.dumps(ledger, indent=2) + "\n")
    Path("receipts/bounded-decision.json").write_text(json.dumps(decision, indent=2) + "\n")
    print(json.dumps(decision, indent=2))
