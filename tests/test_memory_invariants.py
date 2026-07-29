"""Phase 17 tripwires, written before the mechanism (CLAUDE.md).

Ignorance changes what the agent knows, never how it wants: the
memory organ may not touch drive state, and the action layer may not
know memory exists. Written before core/memory.py.
"""

import ast
import pathlib

CORE = pathlib.Path(__file__).resolve().parents[1] / "core"


def _attr_refs(path, attrs):
    tree = ast.parse(path.read_text())
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and n.attr in attrs]


MEM_ATTRS = ("mem_x", "mem_y", "mem_seen", "mem_last_novel", "mem_visited",
             "mem_told", "mem_source")


def test_only_memory_touches_memory():
    """core/memory.py is the only file that may even reference the
    remembered-place arrays (reads, writes, and call-based mutation
    alike, per the phase 16 review hardening)."""
    for path in sorted(CORE.glob("*.py")):
        if path.name == "memory.py":
            continue
        refs = _attr_refs(path, MEM_ATTRS)
        assert not refs, (
            f"{path.name} references memory arrays at line "
            f"{refs[0].lineno}; only core/memory.py may (phase 17)"
        )


def test_memory_blind_to_the_mind():
    """memory.py knows places, not feelings: no reference to drive
    state, credence, or the action table."""
    path = CORE / "memory.py"
    if not path.exists():
        return
    src = path.read_text()
    for banned in ("urgency", "weights", "tau", "credence", "integrity",
                   "fatigue"):
        assert banned not in src, (
            f"memory.py references '{banned}': the memory organ holds "
            f"places only (phase 17 tripwire)"
        )


def test_action_blind_to_memory_and_sight():
    """action.py prices the composite food percept it is handed; it
    may never know whether the target is seen or remembered."""
    src = (CORE / "action.py").read_text()
    for banned in ("mem_", "memory", "r_sight"):
        assert banned not in src, (
            f"action.py references '{banned}': ignorance changes what "
            f"the agent knows, never how it wants (phase 17 tripwire)"
        )


def test_drives_untouched_by_sight():
    """drives.py must not know sight exists: hunger is how empty the
    stomach is, whether or not food was ever seen."""
    src = (CORE / "drives.py").read_text()
    for banned in ("mem_", "r_sight"):
        assert banned not in src, (
            f"drives.py references '{banned}' (phase 17 tripwire)"
        )
