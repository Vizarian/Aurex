"""One bounded autonomous decision cycle, offline by default."""
from dataclasses import asdict
from .engine import Engine
from .goals import choose_goal
from .memory import retrieve

def cycle(events, journal, outbox, policy, max_events=3):
    if max_events < 0 or max_events > 100:
        raise ValueError("Invalid event budget")
    engine = Engine(journal, policy)
    selected = choose_goal()
    results = []
    for event in events[:max_events]:
        decision = engine.handle(event)
        if decision.action == "draft":
            policy.check("draft", already_taken=len(results))
            outbox.enqueue(event.key, event.source, decision.draft)
        results.append({"event_key": event.key, **asdict(decision)})
    return {
        "goal": selected.id if selected else None,
        "decisions": results,
        "context": [asdict(x) for x in retrieve(journal.read())],
        "outbound_sent": 0,
    }
