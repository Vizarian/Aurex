"""Local emergency stop gate for all agent work."""
from pathlib import Path

class Stopped(RuntimeError):
    pass

def assert_running(path="state/STOP"):
    if Path(path).exists():
        raise Stopped("Aurex paused by local stop file")
