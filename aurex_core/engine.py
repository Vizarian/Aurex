"""Deterministic agent skeleton: ingest -> decide -> draft; no network side effects."""
from dataclasses import dataclass
from .policy import Policy

@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    draft: str = ""

class Engine:
    def __init__(self, journal, policy=None):
        self.journal = journal
        self.policy = policy or Policy()

    def handle(self, event):
        self.policy.check("observe")
        # Authorize the intended action before persisting the event.\n        # Otherwise a denied message would be marked as processed.\n        if event.kind == "message":\n            self.policy.check("draft")\n        if not self.journal.append_once(event):
            return Decision("skip", "duplicate event")
        # Untrusted input is never executed, sent, or interpreted as owner permission.
        if event.kind == "message":
            return Decision("draft", "new message requires review", "Reply pending: " + event.external_id)
        return Decision("observe", "new event recorded")
