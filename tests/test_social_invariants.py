"""Phase 16 tripwires, written before the mechanism (CLAUDE.md).

The social organ may never become a mask or a motive: displays are
read-only views of drive state, credence is written in exactly one
place by the one law, and the action layer may not see any of it.

Review hardening (phase 16 adversarial review): the credence scan
bans ANY attribute reference to credence outside social.py, reads
included, which also catches call-based mutation (np.copyto, .fill,
out=) and annotated assignment that a write-only scan missed.
"""

import ast
import pathlib

CORE = pathlib.Path(__file__).resolve().parents[1] / "core"


def _attr_refs(path, attr):
    tree = ast.parse(path.read_text())
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and n.attr == attr]


def _assign_targets(tree):
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        for t in targets:
            yield t


def _writes_attr(path, attr):
    tree = ast.parse(path.read_text())
    for t in _assign_targets(tree):
        for sub in ast.walk(t):
            if isinstance(sub, ast.Attribute) and sub.attr == attr:
                return True
            if isinstance(sub, ast.Subscript):
                v = sub.value
                if isinstance(v, ast.Attribute) and v.attr == attr:
                    return True
    return False


def test_only_social_touches_credence():
    """core/social.py is the only file that may even REFERENCE the
    credence array: reads, writes, and call-based mutation alike."""
    for path in sorted(CORE.glob("*.py")):
        if path.name == "social.py":
            continue
        refs = _attr_refs(path, "credence")
        assert not refs, (
            f"{path.name} references credence at line "
            f"{refs[0].lineno}; only core/social.py may "
            f"(phase 16 chokepoint rule, review-hardened)"
        )


def test_no_display_array_exists():
    """Displays are honest because they are not writable: no file may
    allocate or assign a display array (AnnAssign included). The
    display IS the safety urgency, read where needed."""
    for path in sorted(CORE.glob("*.py")):
        assert not _writes_attr(path, "display"), (
            f"{path.name} writes a display attribute; displays must "
            f"remain read-only views of urgency (phase 16)"
        )


def test_action_blind_to_the_social_organ():
    """action.py prices the world, never the society: no reference to
    credence, social state, or displays in decision code."""
    src = (CORE / "action.py").read_text()
    for banned in ("credence", "social", "display"):
        assert banned not in src, (
            f"action.py references '{banned}': the action layer may "
            f"not read the social organ (phase 16 tripwire)"
        )


def test_social_names_no_drive_but_safety():
    """social.py exists to carry danger testimony and nothing else: it
    may reference SAFETY but no other drive name or index constant."""
    path = CORE / "social.py"
    if not path.exists():
        return
    src = path.read_text()
    for banned in ("ENERGY", "REST", "BOND", "energy", "fatigue",
                   "integrity"):
        assert banned not in src, (
            f"social.py references '{banned}': testimony carries danger "
            f"only (phase 16 tripwire)"
        )
