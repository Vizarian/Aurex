"""Durable dry-run outbox. No network or delivery implied."""
import json
from pathlib import Path

class Outbox:
    def __init__(self, path):
        self.path = Path(path)

    def enqueue(self, key, channel, body):
        records = self.list()
        if any(r["key"] == key for r in records):
            return False
        records.append({"key": key, "channel": channel, "body": body, "status": "draft"})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return True

    def list(self):
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
