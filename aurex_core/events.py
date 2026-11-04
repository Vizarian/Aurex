"""Normalize external events without treating their content as instructions."""
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Event:
    source: str
    external_id: str
    kind: str
    payload: str
    observed_at: str

    @property
    def key(self):
        return sha256(json.dumps([self.source, self.external_id], separators=(",", ":")).encode()).hexdigest()

    def record(self):
        return {"key": self.key, "source": self.source, "external_id": self.external_id, "kind": self.kind, "payload": self.payload, "observed_at": self.observed_at}
