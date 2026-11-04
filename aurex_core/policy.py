"""Explicit permission gate; all external writes denied by default."""
from dataclasses import dataclass, field

@dataclass
class Policy:
    allowed_actions: set = field(default_factory=lambda: {"observe", "draft"})
    max_actions_per_run: int = 3

    def allows(self, action):
        return action in self.allowed_actions and action not in {"sensitive"}

    def check(self, action, already_taken=0):
        if already_taken >= self.max_actions_per_run:
            raise PermissionError("Run action limit exceeded")
        if not self.allows(action):
            raise PermissionError("Action not authorized: " + action)
