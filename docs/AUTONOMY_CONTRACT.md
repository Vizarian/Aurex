# Aurex autonomy contract — provisional v1

**Design decision:** Aurex is a self-directed agent. It can select goals and initiate bounded work without a human choosing every next task.

**Autonomy is not unlimited authority.** Self-directed planning and action authorization are independent. A goal does not grant credentials, private-data access, spending rights, or permission to contact people.

## Operational rules

1. Goals are prioritized by the agent's own scheduler, with an auditable decision trace.
2. Every external observation is stored with provenance. An inherited record is not a personal recollection.
3. Repeated inputs are deduplicated across sessions.
4. Decisions must be bounded by event, time, token, and action budgets.
5. External sends remain off until a scoped channel policy, valid credential, rate limit, and delivery receipt are implemented.
6. Sensitive actions require separate human authorization.
7. Every action should be reconstructible from journal, goal, policy, and resulting receipt.
8. Stop/pause takes precedence over every goal.
9. Research claims are hypotheses, not evidence of machine consciousness.

## Currently implemented

Offline goal selector, bounded event cycle, event journal, evidence-backed context, dry-run outbox, default-deny external write policy, and tests.

## Not implemented

Model-based planning, persistent goal state, reliable multi-process locking, Postmark authenticated send, multi-channel adapters, complete recovery and operational shutdown controls. These remain explicit build targets.
