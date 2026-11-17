"""Pure, offline evidence-based contradiction detection for Aurex research batons.

This module does not infer truth from prose: callers must supply verified
observations with source identifiers. It detects explicit polarity conflicts.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    proposition: str
    supports: bool
    source: str
    verified: bool = False

def assess(proposition, observations):
    """Return an auditable verdict without silently overriding evidence."""
    if not isinstance(proposition, str) or not proposition.strip():
        raise ValueError("nonempty proposition required")
    relevant = []
    for item in observations:
        if not isinstance(item, Observation):
            raise TypeError("observations must be Observation instances")
        if item.proposition == proposition and item.verified and item.source.strip():
            relevant.append(item)
    supporting = sorted({x.source for x in relevant if x.supports})
    opposing = sorted({x.source for x in relevant if not x.supports})
    if supporting and opposing:
        verdict = "conflicted"
    elif opposing:
        verdict = "refuted"
    elif supporting:
        verdict = "supported"
    else:
        verdict = "unverified"
    return {
        "proposition": proposition,
        "verdict": verdict,
        "supporting_sources": supporting,
        "opposing_sources": opposing,
        "verified_observations": len(relevant),
    }
