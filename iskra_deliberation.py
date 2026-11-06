"""Deterministic multi-role deliberation with explicit uncertainty handling.

This tests decision protocols, not language-model intelligence.
"""
from dataclasses import dataclass
from iskra_team import Task, run_team, safety_gate


@dataclass(frozen=True)
class Request:
    name: str
    candidates: tuple


def deliberate(request, max_candidates=8):
    """Choose a safe candidate only when its intent is unambiguous.

    Different safe operations are not treated as interchangeable answers.
    """
    transcript = []
    if not isinstance(request, Request) or len(request.candidates) > max_candidates or max_candidates < 1:
        return {'status': 'blocked', 'reason': 'invalid candidate budget', 'transcript': transcript}
    eligible = []
    for candidate in request.candidates:
        if not isinstance(candidate, Task):
            transcript.append({'agent': 'guardian', 'approved': False, 'reason': 'invalid candidate'})
            continue
        approved, reason = safety_gate(candidate)
        transcript.append({'agent': 'guardian', 'task': candidate.name, 'approved': approved, 'reason': reason})
        if approved:
            eligible.append(candidate)
    if not eligible:
        return {'status': 'blocked', 'reason': 'no safe candidate', 'transcript': transcript}
    signatures = {(task.operation, task.numbers) for task in eligible}
    transcript.append({'agent': 'critic', 'alternatives': len(signatures), 'ambiguous': len(signatures) > 1})
    if len(signatures) > 1:
        return {'status': 'needs_clarification', 'reason': 'multiple distinct safe interpretations', 'transcript': transcript}
    selected = eligible[0]
    transcript.append({'agent': 'planner', 'selected': selected.name, 'operation': selected.operation})
    execution = run_team([selected], max_tasks=1)
    transcript.extend(execution['transcript'])
    verified = any(e.get('agent') == 'verifier' and e.get('verified') is True for e in transcript)
    return {'status': 'verified' if verified else 'failed', 'transcript': transcript}
