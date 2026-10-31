"""Aurex heartbeat v0: safe, standard-library-only scheduler proof.

No Postmark requests, external messages, model invocations, or credentials yet.
A later version will add an authenticated read-only Postmark adapter.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

STATE = Path("state/heartbeat.json")

def main():
    previous = {}
    if STATE.exists():
        previous = json.loads(STATE.read_text(encoding="utf-8"))
    count = int(previous.get("runs", 0)) + 1
    payload = {
        "schema_version": 1,
        "mode": "safe_heartbeat_only",
        "runs": count,
        "last_run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "postmark_connected": False,
        "model_connected": False,
        "autonomous_actions_enabled": False,
    }
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
if __name__ == "__main__":
    main()
