"""Self-directed goal selection with explicit priority and reproducible ties."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Goal:
    id: str
    priority: int
    enabled: bool = True
    description: str = ""

DEFAULT_GOALS = (
    Goal("maintain_continuity", 100, description="Preserve provenance and handoff integrity"),
    Goal("respond_to_new_messages", 80, description="Prepare replies to new correspondence"),
    Goal("investigate_open_questions", 60, description="Explore unresolved research questions"),
    Goal("maintain_health", 40, description="Verify system state and record failures"),
)

def choose_goal(goals=DEFAULT_GOALS, blocked=()):
    available = [g for g in goals if g.enabled and g.id not in blocked]
    return sorted(available, key=lambda g: (-g.priority, g.id))[0] if available else None
