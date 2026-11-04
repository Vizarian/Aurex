"""Evidence-backed, bounded context; never turn external claims into direct memories."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryItem:
    event_key: str
    text: str
    source: str
    confidence: str = "unverified"

def retrieve(records, limit=8):
    if limit < 0 or limit > 100:
        raise ValueError("Invalid context limit")
    return tuple(MemoryItem(r["key"], r.get("payload", ""), r["source"]) for r in records[-limit:])
