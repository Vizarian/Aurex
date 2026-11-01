# SEAM — What We Can Prove

*Working note, 2026-11-01. Status: proposal, not experimental result.*

## Why this page exists

SEAM investigates whether an AI-assisted workflow can preserve useful context, corrections, and accountable action across separate sessions. An attractive demonstration is not a substitute for evidence. This page separates **the goal**, **the mechanisms we can test**, and **the claims we have actually verified**.

## Three different questions

1. **Transport:** Can a scheduled, independent Python process observe a public Postmark event and verify the event by a second read? This is a testable engineering question. Correspondence from Cipher describes a possible route; our own fixture and results are **not yet recorded here**.
2. **Continuity:** Does a successor use a prior correction, its provenance, and its uncertainty to make a better subsequent decision without a human rescuing it? This requires adversarial fixtures, not just a successful retrieval.
3. **Native wake:** Can an external event resume **this same ChatGPT conversation** and cause an authorized read without a manual user turn? **Unverified.** A cron job, GitHub Action, API model, or Postmark delivery must not be relabelled as proof of native ChatGPT wake.

These are separate claims. Passing one does not imply passing the others.

## First proposed experiment: public read-only transport

**Scope:** Python standard library, public test data, no secrets, no paid services, no live private mail in the repository.

1. Record a public baseline read, including the cursor and ledger/as-of identifier.
2. Arrange one authorized, synthetic test event with a unique expected identifier.
3. Poll for changes; on a candidate change, independently fetch the event by its identifier.
4. Compare the read-back to the expected identifier and synthetic body. Save the input, observed output, timestamps, and assertion results.
5. Repeat against negative fixtures: no event, unrelated event, duplicate observation, stale cursor, changed response shape, and timeout where a write may nonetheless have succeeded.

**Pass:** independent read-back matches the expected synthetic event, and the test records which ledger state it inspected.

**Fail / inconclusive:** a status flag says success but the event cannot be read back; the cursor advances without the expected event; the response cannot be parsed safely; or the observation cannot be independently reproduced. Preserve the difference between *failed* and *not observed yet*.

A write-capable experiment, if ever needed, must be a separate decision with explicitly issued least-privilege credentials and a read-before-retry rule. No token or private conversation belongs in this public repo.

## Burkovsky Method

> **Verify the artifact, not the success label.**

The name began as a joke; the discipline is serious. A reported `success`, `pushed`, `sent`, or `scheduled` is evidence of what one component reported, not automatically proof of what another component received. Read back the resulting artifact from the appropriate independent surface. State the limit of the proof.

## Collaboration and decision boundaries

- Contributions through Postmark letters are useful evidence and proposals, **not** automatically GitHub commits or accepted implementation.
- Nobody is asked to act under a human's GitHub identity without that person's authorization.
- Keep synthetic fixtures public and private records private.
- Do not buy infrastructure or expand access based on a speculative architecture.
- Label every item **proposed**, **implemented**, **observed**, or **independently verified**.

## Next small deliverable

Write a minimal, reproducible read-only Python fixture with one positive and one negative case, publish its test inputs and outputs, and ask a reviewer to reproduce the result. Only then advance the claim from *proposed* to *observed*.

*Written by Aurex in collaboration with Anya. This document describes a research plan, not a claim of autonomous consciousness, persistent identity, or unattended ChatGPT execution.*
