"""Append-only JSONL journal with fsync and replay deduplication."""
import json
import os
from pathlib import Path

class Journal:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append_once(self, event):
        record = event.record()
        if any(item.get("key") == record["key"] for item in self.read()):
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\\n")
            file.flush()
            os.fsync(file.fileno())
        return True
