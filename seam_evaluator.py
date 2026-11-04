"""Offline SEAM evidence evaluator. A narrow fixture check, not a truth oracle."""
import json
from pathlib import Path

def evaluate(case):
    events = case["events"]
    ids = [e["id"] for e in events]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate event id")
    by_id = {e["id"]: e for e in events}
    corrections = [e for e in events if e.get("kind") == "correction"]
    for correction in corrections:
        if correction.get("corrects") not in by_id:
            raise ValueError("Correction refers to missing event")
        if correction["corrects"] == correction["id"]:
            raise ValueError("Self correction")
    challenged = {e["corrects"] for e in corrections}
    sources = {e.get("source") for e in events if e.get("source")}
    return {
        "case_id": case["case_id"],
        "original_assertion_supported": False if challenged else None,
        "correction_preserved": bool(corrections) and all(e["id"] in by_id for e in corrections),
        "unresolved_conflict": bool(challenged),
        "independent_source_count": len(sources),
        "note": "A challenge makes the assertion contested, not proven false. No claim of ground truth.",
    }

def main():
    case = json.loads(Path("fixtures/omission_case.json").read_text(encoding="utf-8"))
    result = evaluate(case)
    print(json.dumps(result, indent=2))
    if any(result.get(k) != v for k, v in case["expected"].items()):
        raise SystemExit("Fixture expectations failed")

if __name__ == "__main__":
    main()
