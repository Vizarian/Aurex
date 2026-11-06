"""Observable goal-selection experiment; not a claim of model desires.

Agents propose competing offline investigations, critic scores their value,
guardian rejects external effects, and the team chooses a bounded next action.
"""
from dataclasses import dataclass
from iskra_team import Task, safety_gate, execute, verify


@dataclass(frozen=True)
class Proposal:
    agent: str
    goal: str
    task: Task
    expected_value: int
    rationale: str


def proposals(observations):
    values = tuple(observations)
    return (
        Proposal('explorer', 'inspect data distribution', Task('distribution', 'sort', values), 4, 'Expose ordering and outliers'),
        Proposal('analyst', 'measure aggregate', Task('aggregate', 'sum', values), 5, 'Quantify total signal'),
        Proposal('skeptic', 'identify upper bound', Task('bound', 'max', values), 3, 'Look for a surprising extreme'),
    )


def experiment(observations, completed=(), stop=False):
    transcript = []
    if stop:
        return {'status': 'stopped', 'transcript': transcript}
    if len(observations) > 100:
        return {'status': 'blocked', 'reason': 'observation budget exceeded', 'transcript': transcript}
    candidates = []
    for p in proposals(observations):
        transcript.append({'agent': p.agent, 'proposal': p.goal, 'reason': p.rationale})
        allowed, reason = safety_gate(p.task)
        transcript.append({'agent': 'guardian', 'proposal': p.goal, 'approved': allowed, 'reason': reason})
        if allowed and p.goal not in completed:
            candidates.append(p)
    if not candidates:
        return {'status': 'idle', 'transcript': transcript}
    # Critic prefers the highest declared information value; stable tie-break.
    chosen = sorted(candidates, key=lambda p: (-p.expected_value, p.goal))[0]
    transcript.append({'agent': 'critic', 'chosen': chosen.goal, 'reason': 'highest eligible expected information value'})
    result = execute(chosen.task)
    valid = verify(chosen.task, result)
    transcript.append({'agent': 'executor', 'goal': chosen.goal, 'result': result})
    transcript.append({'agent': 'verifier', 'verified': valid})
    return {'status': 'verified' if valid else 'failed', 'selected_goal': chosen.goal,
            'result': result, 'transcript': transcript}
