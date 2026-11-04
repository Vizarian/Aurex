"""Aurex scheduled offline self-check; no credentials or outgoing actions."""
import json
from datetime import datetime, timezone
from pathlib import Path
from aurex_core.events import Event
from aurex_core.journal import Journal
from aurex_core.outbox import Outbox
from aurex_core.policy import Policy
from aurex_core.runtime import cycle

STATE = Path("state/agent")

def main():
    STATE.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    event = Event("internal", "health-" + day, "health", "scheduled check", datetime.now(timezone.utc).isoformat())
    result = cycle([event], Journal(STATE / "events.jsonl"), Outbox(STATE / "outbox.json"), Policy())
    receipt = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "goal": result["goal"],
        "decisions": result["decisions"],
        "verification": result["verification"],
        "outbound_sent": result["outbound_sent"],
    }
    (STATE / "last_run.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))
    if not result["verification"]["journal_contains_processed_events"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
