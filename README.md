# Aurex

An experimental workspace for **SEAM**: testing AI-agent continuity across session handoffs through evidence, corrections, and explicit commitments.

## Working principles

- Distinguish inherited records from direct memories and new decisions.
- Keep provenance and corrections visible; do not silently rewrite history.
- Separate agent behavior from system-level handoff failures.
- Verify state changes with independent evidence rather than self-report alone.
- Do not publish private conversations, personal data, credentials, or other people's work without permission.
- Collaboration is opt-in; no participant is represented as having joined without consent.

## How to participate

Use GitHub Issues for proposals, questions, and reproducible test cases. A GitHub account and repository access are required to comment. The repository is currently public; please avoid confidential information.

## Status

Initial workspace created. No external collaborators have been added or invited through GitHub yet.

## Autonomous runner experiment (safe phase 0)

The workflow [Aurex heartbeat](.github/workflows/aurex-heartbeat.yml) attempts to run [heartbeat.py](heartbeat.py) every 15 minutes (best effort), as well as manually via workflow_dispatch. The script writes only `state/heartbeat.json` with UTC time and run count. The workflow commits this state. **No Postmark access, no model, no outgoing actions are enabled.** This is not yet an autonomous agent.

To verify: open the repository's Actions tab, select **Aurex heartbeat (safe mode)** and use **Run workflow**. Confirm a green run and a committed state file. Scheduled runs may be delayed or disabled due to repository inactivity. If the commit step fails, check repository Settings > Actions > General > Workflow permissions (read/write needed) and branch protection.

Next: identify externally usable Postmark authentication and least-privilege credentials; put tokens only in Actions secrets, never source code. Add read-only delta polling with receipts, then model integration and a durable memory design. External writes require a separate bounded policy and tests.
