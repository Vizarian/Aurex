"""Bounded autonomous cycle: perceive, select, plan, execute local actions, verify."""
from dataclasses import asdict
from .engine import Engine
from .goals import choose_goal
from .initiative import propose, prioritize
from .memory import retrieve
from .stop import assert_running

def cycle(events, journal, outbox, policy, max_events=3, stop_path="state/STOP"):
    if max_events < 0 or max_events > 100:
        raise ValueError("Invalid event budget")
    assert_running(stop_path)
    engine = Engine(journal, policy)
    selected = choose_goal()
    results = []
    tasks = prioritize(propose(events[:max_events]))
    for event in events[:max_events]:
        assert_running(stop_path)
        # Reserve action capacity before journaling; never mark an event processed\n        # if this run cannot complete its permitted decision.\n        if len(results) >= policy.max_actions_per_run:\n            raise PermissionError("Run action limit exceeded")\n        decision = engine.handle(event)
        if decision.action == "draft":
            policy.check("draft", already_taken=len(results))
            outbox.enqueue(event.key, event.source, decision.draft)
        results.append({"event_key": event.key, **asdict(decision)})
    drafts = outbox.list()
    verification = {
        "journal_contains_processed_events": all(
            any(r["key"] == d["event_key"] for r in journal.read())
            for d in results if d["action"] != "skip"
        ),
        "drafts_only": all(d["status"] == "draft" for d in drafts),
        "outbound_sent": 0,
    }
    return {
        "goal": selected.id if selected else None,
        "proposed_tasks": [asdict(task) for task in tasks],
        "decisions": results,
        "context": [asdict(x) for x in retrieve(journal.read())],
        "verification": verification,
        "outbound_sent": 0,
    }
