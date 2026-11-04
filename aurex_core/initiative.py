"""Agent-initiated task proposals from observations, without unbounded side effects."""
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Task:
    id: str
    goal: str
    title: str
    evidence_key: str
    action: str
    status: str = "proposed"

def propose(events):
    tasks = []
    seen = set()
    for event in events:
        if event.kind == "message":
            goal, title, action = "respond_to_new_messages", "Consider a response to new message", "draft"
        elif event.kind == "failure":
            goal, title, action = "maintain_health", "Investigate observed system failure", "inspect"
        elif event.kind == "research":
            goal, title, action = "investigate_open_questions", "Review research evidence", "analyze"
        else:
            continue
        identifier = sha256(json.dumps([event.key, goal], separators=(",", ":")).encode()).hexdigest()[:20]
        if identifier in seen:
            continue
        seen.add(identifier)
        tasks.append(Task(identifier, goal, title, event.key, action))
    return tuple(tasks)

def prioritize(tasks):
    ranking = {"maintain_health": 100, "respond_to_new_messages": 80, "investigate_open_questions": 60}
    return tuple(sorted(tasks, key=lambda t: (-ranking.get(t.goal, 0), t.id)))
