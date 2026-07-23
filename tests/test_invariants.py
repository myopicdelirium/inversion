"""Static analysis enforcing the Prime Invariant (CLAUDE.md).

Written before the mechanism, per the constitution. These checks are a
tripwire, not a proof: the behavioural guarantees come from the Phase 1
lag validation and the Phase 3 null-region tests. Do not modify,
weaken, skip, or exclude these tests. If one fails, the code is wrong,
not the test.
"""

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
MECHANISM_FILES = (CORE / "drives.py", CORE / "action.py")

# Identifier tokens indicating mortality, damage, or threat state.
# "alive" and "dead" are deliberately excluded from the override check
# below: masking an update to living agents is the standard
# structure-of-arrays idiom and cannot grant a drive priority, while
# conditioning on impending death ("dying", "lethal", ...) can, and
# stays forbidden.
STATE_TOKENS = {
    "death", "die", "dies", "died", "dying", "mortal", "mortality",
    "kill", "killed", "lethal", "threat", "danger", "damage", "damaged",
    "health", "hp", "integrity", "hazard", "survive", "survival",
}

# Identifier tokens indicating drive valuation state.
WEIGHT_TOKENS = {"w", "weight", "weights", "priority", "priorities"}
TAU_TOKENS = {"tau", "taus"}

# No code path may be named or scoped to the phenomenon, anywhere.
FORBIDDEN_FRAGMENTS = ("sacrif", "martyr", "hero", "altru", "suicid")


def _tokens(name: str) -> set[str]:
    # Split snake_case and camelCase into lowercase word tokens, so
    # "danger" does not false-positive inside "gradient".
    parts = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().split("_")
    return {p for p in parts if p}


def _identifiers(node: ast.AST) -> set[str]:
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            out.add(sub.attr)
    return out


def _token_set(node: ast.AST) -> set[str]:
    out = set()
    for name in _identifiers(node):
        out |= _tokens(name)
    return out


def _assignments(tree: ast.AST):
    """Yield (target_tokens, value_node) for every assignment."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets, value = [node.target], node.value
            if isinstance(node, ast.AnnAssign) and node.value is None:
                # A bare annotation (dataclass field, type stub) declares
                # a name; it does not write to it.
                continue
        else:
            continue
        target_tokens = set()
        for t in targets:
            # For subscripted or attribute targets, only the base name
            # counts as the thing being written; index expressions are
            # inspected separately by the override test via the value.
            base = t
            while isinstance(base, ast.Subscript):
                base = base.value
            target_tokens |= _token_set(base)
        yield target_tokens, value, node


def _mechanism_trees():
    for path in MECHANISM_FILES:
        yield path, ast.parse(path.read_text())


def test_mechanism_files_exist():
    # Renaming the mechanism files must not dodge this analysis.
    for path in MECHANISM_FILES:
        assert path.is_file() and path.read_text().strip(), (
            f"{path} is missing or empty; the invariant analysis has no target"
        )


def test_no_forbidden_names():
    # Applies to every file in core/, not just the mechanism files.
    for path in sorted(CORE.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, ast.Attribute):
                names.append(node.attr)
            elif isinstance(node, ast.arg):
                names.append(node.arg)
            for name in names:
                lname = name.lower()
                for frag in FORBIDDEN_FRAGMENTS:
                    assert frag not in lname, (
                        f"{path.name}: identifier '{name}' is scoped to the "
                        f"phenomenon; the invariant forbids it"
                    )


def test_no_scripted_override():
    """No conditional on mortality/threat/damage state may assign drive
    valuation state, and no assignment to weights or taus may read such
    state at all. Urgencies are where body state legitimately enters the
    system, as continuous functions; weights may be written only from
    urgencies, taus, and other weights, via the uniform law.

    Covers `if` blocks, ternaries, and masked writes (np.where etc.),
    because all of those leave the state identifier visible either in
    the conditional test or in the assigned value expression.
    """
    for path, tree in _mechanism_trees():
        # Pattern A: if <state>: ... <weight or tau> = ...
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            if not (_token_set(node.test) & STATE_TOKENS):
                continue
            for stmt in node.body + node.orelse:
                for target_tokens, _value, assign in _assignments(stmt):
                    bad = target_tokens & (WEIGHT_TOKENS | TAU_TOKENS)
                    assert not bad, (
                        f"{path.name}:{assign.lineno}: assignment to {bad} "
                        f"inside a conditional on mortality/threat state"
                    )
        # Pattern B: <weight or tau> = <expression reading state>
        for target_tokens, value, assign in _assignments(tree):
            if not (target_tokens & (WEIGHT_TOKENS | TAU_TOKENS)):
                continue
            if value is None:
                continue
            bad = _token_set(value) & STATE_TOKENS
            assert not bad, (
                f"{path.name}:{assign.lineno}: drive valuation written from "
                f"state identifiers {bad}; state may only enter through "
                f"urgencies"
            )


def test_tau_written_only_at_declaration_or_init():
    """Time constants are declared in core/config.py and drawn once at
    spawn inside init functions of core/drives.py, the one sanctioned
    draw site (Amendment 2). Nothing else may write them, so nothing
    can modify them from circumstance (Amendment 1)."""
    for path in sorted(CORE.glob("*.py")):
        if path.name == "config.py":
            continue
        tree = ast.parse(path.read_text())
        allowed = set()
        if path.name == "drives.py":
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and node.name.startswith("init"):
                    for stmt in ast.walk(node):
                        allowed.add(id(stmt))
        for target_tokens, _value, assign in _assignments(tree):
            bad = target_tokens & TAU_TOKENS
            assert not bad or id(assign) in allowed, (
                f"{path.name}:{assign.lineno}: assignment to time constant "
                f"{bad} outside config.py and drives.py init functions"
            )


def test_update_law_names_no_drive():
    """Amendment 3: the update law (attention included) is drive
    agnostic. The function that moves weights may not reference any
    drive-index identifier; whatever dominance suppresses, it
    suppresses uniformly. Written before the attention mechanism."""
    tree = ast.parse((CORE / "drives.py").read_text())
    drive_ids = {"ENERGY", "SAFETY", "REST", "BOND"}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "update_weights":
            used = _identifiers(node)
            bad = used & drive_ids
            assert not bad, (
                f"update_weights references drive identifiers {bad}; "
                f"the law may not name a drive (Amendment 3)"
            )
            break
    else:
        raise AssertionError("update_weights not found in core/drives.py")


def test_timescales_immutable_at_runtime():
    """Per-agent time constants drawn at spawn never change, even under
    a storm with every spread nonzero (Amendment 2)."""
    from dataclasses import replace

    import numpy as np

    from core.config import Config
    from core.model import Model

    cfg = replace(
        Config(), n_hazard=0, storm_nest=0, storm_onset=100, storm_ramp=1,
        bond_init=1.0, tau_safety_spread=0.5, tau_bond_spread=0.5,
        bond_init_spread=0.25, n_agents=60,
    )
    m = Model(cfg, seed=7)
    at_spawn = m.arrays.tau.copy()
    assert np.std(at_spawn[:, 1]) > 0 and np.std(at_spawn[:, 3]) > 0, (
        "spreads are nonzero but the drawn time constants are uniform"
    )
    for _ in range(300):
        m.step()
    assert np.array_equal(m.arrays.tau, at_spawn), (
        "per-agent time constants changed during a run; Amendment 2 violated"
    )


def test_drive_state_written_only_in_drives():
    """Chokepoint rule: weights and urgencies are mutated only in
    core/drives.py. This is what makes the static analysis above sound;
    without it, the invariant could be violated from any other file."""
    protected = {"weights", "urgency", "urgencies"}
    for path in sorted(CORE.glob("*.py")):
        if path.name == "drives.py":
            continue
        tree = ast.parse(path.read_text())
        for target_tokens, _value, assign in _assignments(tree):
            bad = target_tokens & protected
            assert not bad, (
                f"{path.name}:{assign.lineno}: write to drive state {bad} "
                f"outside core/drives.py"
            )
