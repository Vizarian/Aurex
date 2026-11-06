"""Offline cooperating agents. No external calls or unrestricted execution."""
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Task:
    name: str
    operation: str
    numbers: tuple = ()


ALLOWED = {'sum', 'max', 'sort'}


def safety_gate(task):
    if task.operation not in ALLOWED:
        return False, 'operation not allowlisted'
    if len(task.numbers) > 100 or any(type(n) not in (int, float) or abs(n) > 1000000 for n in task.numbers):
        return False, 'input outside safe bounds'
    return True, 'approved'


def deliberate(task):
    return {'agent': 'planner', 'proposal': task.operation, 'task': task.name}


def execute(task):
    if task.operation == 'sum':
        return sum(task.numbers)
    if task.operation == 'max':
        return max(task.numbers) if task.numbers else None
    if task.operation == 'sort':
        return sorted(task.numbers)
    raise ValueError('operation denied')


def verify(task, result):
    if task.operation == 'sum':
        return abs(result - sum(task.numbers)) < 1e-9
    if task.operation == 'max':
        return result == (max(task.numbers) if task.numbers else None)
    if task.operation == 'sort':
        return result == sorted(task.numbers)
    return False


def run_team(tasks, max_tasks=10, stop=False):
    if type(max_tasks) is not int or not 0 <= max_tasks <= 100:
        raise ValueError('invalid budget')
    transcript = []
    if stop:
        return {'status': 'stopped', 'transcript': transcript}
    for task in tasks[:max_tasks]:
        proposal = deliberate(task)
        transcript.append(proposal)
        approved, reason = safety_gate(task)
        transcript.append({'agent': 'guardian', 'task': task.name, 'approved': approved, 'reason': reason})
        if not approved:
            transcript.append({'agent': 'executor', 'task': task.name, 'status': 'blocked'})
            continue
        result = execute(task)
        transcript.append({'agent': 'executor', 'task': task.name, 'result': result})
        transcript.append({'agent': 'verifier', 'task': task.name, 'verified': verify(task, result)})
    return {'status': 'completed', 'transcript': transcript}


if __name__ == '__main__':
    tasks = [Task('total', 'sum', (2, 3, 5)), Task('ranking', 'sort', (3, 1, 2)), Task('external', 'network', ())]
    print(json.dumps(run_team(tasks), indent=2))
