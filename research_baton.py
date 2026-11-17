"""Evidence-preserving research baton with optimistic revision checks.

Standard-library only. Does not call a model or perform external sends.
"""
import json
import os
import tempfile
from pathlib import Path

REQUIRED = {
    "schema_version": int, "question_id": str, "question": str,
    "current_claim": str, "counterevidence": list, "next_test": str,
    "alternatives_rejected": list, "uncertainty": str,
    "status": str, "revision": int,
}

def validate(baton):
    if not isinstance(baton, dict):
        raise ValueError("baton must be an object")
    for key, kind in REQUIRED.items():
        if key not in baton or type(baton[key]) is not kind:
            raise ValueError("invalid or missing field: " + key)
    if baton["schema_version"] != 1 or baton["revision"] < 1:
        raise ValueError("unsupported schema or revision")
    if baton["status"] not in ("open", "blocked", "closed"):
        raise ValueError("invalid status")
    if not baton["question_id"].strip() or not baton["question"].strip():
        raise ValueError("empty identity or question")
    for key in ("counterevidence", "alternatives_rejected"):
        if not all(isinstance(item, str) for item in baton[key]):
            raise ValueError("invalid list items: " + key)
    return baton

def read(path):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))

def write(path, baton, expected_revision=None):
    """Atomically replace one baton. Revision checks detect sequential stale writes.

    Callers must separately serialize concurrent writers (e.g. GitHub Actions
    concurrency groups). This is NOT a cross-process compare-and-swap.
    """
    path = Path(path)
    validate(baton)
    if path.exists():
        previous = read(path)
        if expected_revision != previous["revision"]:
            raise ValueError("stale revision")
        if baton["question_id"] != previous["question_id"]:
            raise ValueError("question identity changed")
        if baton["revision"] != previous["revision"] + 1:
            raise ValueError("revision must increase by one")
        if not set(previous["counterevidence"]).issubset(baton["counterevidence"]):
            raise ValueError("cannot silently erase counterevidence")
    elif expected_revision is not None or baton["revision"] != 1:
        raise ValueError("new baton must start at revision one")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".baton-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(baton, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return read(path)
