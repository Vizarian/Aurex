"""Iskra: auditable, offline autonomous task selection with persistent state.

No network, subprocesses, credential access, or hidden background activity.
Run explicitly or from a visible scheduler; stop by creating state/STOP.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from aurex_core.goals import DEFAULT_GOALS, choose_goal


def cycle(state_dir=Path('state/iskra'), stop_file=Path('state/STOP')):
    state_dir = Path(state_dir)
    if Path(stop_file).exists():
        return {'status': 'stopped', 'reason': 'stop file present'}
    state_file = state_dir / 'last_run.json'
    previous = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
    completed = set(previous.get('completed', []))
    goal = choose_goal(DEFAULT_GOALS, blocked=completed)
    if goal is None:
        return {'status': 'idle', 'reason': 'no remaining eligible goals', 'completed': sorted(completed)}
    # A goal is only observed and selected here; it is not claimed as completed.
    result = {
        'status': 'proposed', 'goal': goal.id,
        'reason': goal.description,
        'completed': sorted(completed),
        'previous_goal': previous.get('goal'),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'verified': False,
        'next_step': 'Implement and test an explicitly permitted action for this goal',
    }
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run one transparent offline Iskra decision cycle')
    parser.add_argument('--state-dir', type=Path, default=Path('state/iskra'))
    parser.add_argument('--stop-file', type=Path, default=Path('state/STOP'))
    args = parser.parse_args()
    print(json.dumps(cycle(args.state_dir, args.stop_file), indent=2))
