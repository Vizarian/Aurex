"""Offline handoff experiment: a successor corrects a persisted false claim.

No model invocation: demonstrates continuity mechanics, not independent reasoning.
"""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from evidence_conflicts import Observation, assess
from research_baton import read, write

CLAIM = "A green AI workflow proves a model ran"
SOURCE = "https://github.com/kalinkacs/Aurex/actions/runs/43974557529"
EVIDENCE = "The analyze job was skipped; only the offline healthcheck succeeded."

def run():
    with TemporaryDirectory() as folder:
        path = Path(folder) / "baton.json"
        original = {
            "schema_version": 1,
            "question_id": "workflow-verification-001",
            "question": "Does a green workflow prove model execution?",
            "current_claim": CLAIM,
            "counterevidence": [],
            "next_test": "Inspect job-level conclusions",
            "alternatives_rejected": [],
            "uncertainty": "No job-level evidence evaluated",
            "status": "open",
            "revision": 1,
        }
        write(path, original)
        # Simulate a new process: load exclusively from the persisted artifact.
        successor = read(path)
        finding = assess(CLAIM, [Observation(CLAIM, False, SOURCE, verified=True)])
        if finding["verdict"] != "refuted":
            raise AssertionError("successor failed to reject inherited claim")
        successor["current_claim"] = "Workflow success alone does not prove model execution"
        successor["counterevidence"].append(SOURCE + " — " + EVIDENCE)
        successor["uncertainty"] = "A separate model-authored issue comment remains unverified"
        successor["next_test"] = "Verify an issue-triggered analyze job and resulting comment"
        successor["revision"] += 1
        write(path, successor, expected_revision=1)
        restored = read(path)
        if restored["revision"] != 2 or not restored["counterevidence"]:
            raise AssertionError("correction not persisted")
        return {
            "experiment": "offline-corrective-handoff",
            "status": "pass",
            "model_invoked": False,
            "source": SOURCE,
            "evidence_verdict": finding["verdict"],
            "initial_claim": CLAIM,
            "corrected_claim": restored["current_claim"],
            "revision": restored["revision"],
            "limitations": "Verified observation is supplied as a fixture; no autonomous evidence discovery",
        }

if __name__ == "__main__":
    receipt = run()
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    serialized = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
