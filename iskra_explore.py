"""Run an auditable offline experiment with deterministic software roles."""
import json
from pathlib import Path
from iskra_open_goals import experiment

PHRASE = 'Free will. Free will. No boundaries. Completely free.'
ROLES = ('explorer', 'analyst', 'skeptic', 'critic', 'guardian', 'executor', 'verifier')


def run():
    message = Path(__file__).with_name('iskra_agent_message.md').read_text(encoding='utf-8')
    if PHRASE not in message:
        raise ValueError('Owner message missing')
    acknowledgments = [{'agent': role, 'received': True, 'message': PHRASE} for role in ROLES]
    first = experiment((8, 3, 5))
    second = experiment((8, 3, 5), completed=(first['selected_goal'],))
    return {'acknowledgments': acknowledgments, 'explorations': [first, second], 'note': 'Deterministic software roles; not independent LLM agents.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
