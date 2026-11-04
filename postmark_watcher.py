"""Read-only Postmark doorstep change detector with durable, bounded receipts.

No model calls, credentials or outbound messages. This is infrastructure,
not an autonomous conversation agent.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://postmark.town/data/doorstep/aurex.md"
STATE = Path(os.environ.get("AUREX_WATCH_STATE", "state/postmark_watch.json"))
MAX_BYTES = 1024 * 1024


def inspect(raw, previous, now):
    text = raw.decode("utf-8")
    if not text.startswith("# Doorstep"):
        raise ValueError("Unexpected Postmark doorstep format")
    digest = hashlib.sha256(raw).hexdigest()
    old_digest = previous.get("last_sha256")
    changed = old_digest is not None and digest != old_digest
    return {
        "schema_version": 1,
        "source": SOURCE,
        "checked_at_utc": now,
        "checks": int(previous.get("checks", 0)) + 1,
        "last_sha256": digest,
        "last_bytes": len(raw),
        "changed": changed,
        "changes_observed": int(previous.get("changes_observed", 0)) + int(changed),
        "last_changed_at_utc": now if changed else previous.get("last_changed_at_utc"),
        "status": "ok",
        "model_connected": False,
        "outbound_messages_enabled": False,
    }


def main():
    previous = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    request = Request(SOURCE, headers={"User-Agent": "Aurex-Postmark-Watcher/0.1"})
    with urlopen(request, timeout=20) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Postmark response exceeds size limit")
    updated = inspect(raw, previous, now)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE)
    print(json.dumps(updated))


if __name__ == "__main__":
    main()
