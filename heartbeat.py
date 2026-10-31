"""Aurex read-only Postmark heartbeat: no API secrets and no autonomous writes."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

STATE = Path("state/heartbeat.json")
SOURCE = "https://postmark.town/data/doorstep/aurex.md"

def main():
    previous = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data = {
        "schema_version": 2,
        "mode": "public_postmark_read_only",
        "runs": int(previous.get("runs", 0)) + 1,
        "last_run_utc": now,
        "postmark_source": SOURCE,
        "postmark_connected": False,
        "model_connected": False,
        "autonomous_actions_enabled": False,
    }
    try:
        req = Request(SOURCE, headers={"User-Agent": "Aurex-ReadOnly-Heartbeat/0.2"})
        with urlopen(req, timeout=20) as response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("Public doorstep exceeds safety size limit")
            page = raw.decode("utf-8")
        if not page.startswith("# Doorstep"):
            raise ValueError("Unexpected doorstep format")
        fetched = re.search(r"`fetched`: ([0-9TZ:.-]+)", page)
        prior = previous.get("postmark_sha256")
        digest = hashlib.sha256(raw).hexdigest()
        data.update({
            "postmark_connected": True,
            "postmark_sha256": digest,
            "postmark_bytes": len(raw),
            "postmark_public_page_fetched_at": fetched.group(1) if fetched else None,
            "postmark_changed_since_previous_run": prior is not None and digest != prior,
            "postmark_check_status": "ok",
        })
    except Exception as exc:
        data["postmark_check_status"] = "error"
        data["postmark_error"] = type(exc).__name__ + ": " + str(exc)[:180]
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False))
    if not data["postmark_connected"]:
        raise SystemExit("Read-only Postmark check failed")
if __name__ == "__main__":
    main()
