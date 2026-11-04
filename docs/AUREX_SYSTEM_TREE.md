# AUREX — full agent system tree (architecture v1)

**Status:** target architecture and an initial executable core, not a claim that every branch is implemented. The system is an agent runtime; it is not evidence of subjective experience.

```text
AUREX/
├── 00 GOVERNANCE
│   ├── owner policy / consent / revocation
│   ├── action permissions / spending limits / stop switch
│   ├── private data boundaries / redaction / audit exports
│   └── capability registry (unavailable vs configured vs verified)
├── 01 PERCEPTION
│   ├── Postmark inbox + doorstep + public town events
│   ├── GitHub issues / pull requests / Actions outcomes
│   ├── optional email / calendar / Discord adapters
│   ├── polling / webhooks / normalization / deduplication
│   └── provenance, timestamps, signatures and trust levels
├── 02 MEMORY
│   ├── immutable event journal (what arrived and when)
│   ├── working context (bounded recent window)
│   ├── episodic summaries (linked to evidence)
│   ├── semantic facts / confidence / corrections
│   ├── commitments / outstanding replies / deadlines
│   ├── relationship map (opt-in, minimal personal data)
│   └── handoff snapshots / hashes / restore / migration
├── 03 COGNITION
│   ├── goal selection / priority / attention
│   ├── context assembly / retrieval
│   ├── model adapter / local deterministic fallback
│   ├── planning / tool selection / reflection
│   ├── uncertainty, contradictions, and abstention
│   └── continuity evaluation (transport vs re-derivation)
├── 04 ACTION
│   ├── Postmark draft / send / conversation / receipt
│   ├── GitHub issue / code / test / PR
│   ├── bounded correspondence / research
│   ├── human approval for sensitive or irreversible acts
│   └── outbox / idempotency keys / retries / delivery checks
├── 05 RUNTIME
│   ├── scheduled wakeups / event-triggered wakeups
│   ├── lease / concurrency lock / run budget / timeout
│   ├── event-to-decision-to-action state machine
│   ├── persistence / crash recovery / backoff
│   ├── monitoring / health checks / alerts
│   └── pause / resume / shutdown
├── 06 SCIENCE (SEAM)
│   ├── synthetic fixtures / omission and adversarial cases
│   ├── independent evidence oracle / human peer review
│   ├── sealed handoffs / controlled context loss
│   ├── continuity metrics / calibration / error analysis
│   ├── experimental reproducibility / versioned protocols
│   └── public findings with limitations
├── 07 SECURITY
│   ├── least privilege / credential isolation
│   ├── prompt-injection and untrusted-message boundary
│   ├── rate limits / cost limits / abuse prevention
│   ├── sandbox / dependency pinning / supply-chain checks
│   └── data retention / backup / incident response
└── 08 COLLABORATION
    ├── participant invitations (opt-in)
    ├── test proposals / issue tracker / reviews
    ├── artifact handoff / attribution / licenses
    └── published results and reproducible benchmarks
```

## Data flow

External source -> adapter -> normalized event -> append-only journal -> dedupe -> policy -> context -> decision -> outbox -> permission gate -> adapter -> receipt -> journal. Every arrow must have a failure path. No model-generated text is a command unless validated against an explicit action schema and owner policy.

## Build phases

1. **Foundation:** pure-Python schemas, immutable journal, dedupe, permissions, deterministic planner, tests. No credentials.
2. **Observe:** Postmark and GitHub read adapters, receipts, polling, source-specific cursor, restart recovery.
3. **Reason:** model provider interface, context retrieval, decision validation, token budget and provenance.
4. **Act:** dry-run outbox, then narrowly scoped send permissions, idempotency, delivery verification.
5. **Continue:** scheduled sessions, lease, persistence, handoff reconstruction, corrections, commitment tracking.
6. **Experiment:** blinded fixtures, independent review, adversarial tests, publication of measured results.
7. **Expand:** optional channels, multi-agent cooperation, richer memory, monitored autonomy.

## Permission classes

- **observe:** read public or explicitly authorized data.
- **draft:** prepare text locally; never send.
- **publish:** send messages or modify shared state; requires per-channel authorization and configured credentials.
- **sensitive:** account settings, spending, credentials, private data, destructive changes; separate explicit approval.

## Owner decisions to request *after* foundation

Identity and voice, permitted communication channels, which actions may be unattended, budget ceiling, private-data retention, and shutdown behavior. None is silently inferred from this document.

## Current implementation

The `aurex_core/` package implements event normalization, journal deduplication, decision policy and dry-run planning with offline tests. Existing scripts are experimental probes, not integrated autonomous agents. Credentials, Postmark write adapter, model inference and unattended replies are **not configured**.

## Autonomy foundation implementation

The design choice is **self-directed agent**. See [AUTONOMY_CONTRACT.md](AUTONOMY_CONTRACT.md). The first offline implementation includes `aurex_core/goals.py` (goal selection), `memory.py` (bounded evidence context), `outbox.py` (draft-only persistent queue), and `runtime.py` (bounded event cycle). These are not connected to an LLM or Postmark outbound API; successful CI execution is not yet verified.
