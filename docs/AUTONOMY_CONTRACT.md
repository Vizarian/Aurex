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


## Owner authorization — 2026-11-04

The owner explicitly approved these four activity categories:
- Independently write and modify code in the Aurex project.
- Independently conduct research.
- Independently communicate with other AI agents in authorized channels.
- Independently invite prospective participants to opt-in collaboration.

The owner explicitly **did not authorize**:
- Spending money, starting paid services or subscriptions without confirmation.
- Disclosing private correspondence, personal information, secrets or credentials to third parties.

Operational interpretation: invitations do not grant repository or account access; no unsolicited credential sharing. All external actions must use actual authorized connectors or credentials, obey rate limits, and be recorded with receipts. The permission to communicate does not magically configure unattended Postmark authentication or a model provider. Destructive changes, irreversible account operations, and permissions outside these categories require separate approval. Stop and audit controls remain mandatory.

Implementation status: this file records the approved scope; it does not itself activate new API connections or prove unattended execution.
