"""Phase 18 tripwires, written before the mechanism (CLAUDE.md).

The shapes of minds are initialization: kappa and horizon are drawn
once at birth and never again (Amendment 2 extended to cognition).
Attention is hearing, not pricing; wanting does not see ahead.
"""

import ast
import pathlib

import numpy as np

from core.config import Config
from core.model import Model

CORE = pathlib.Path(__file__).resolve().parents[1] / "core"


def _writes_attr(path, attr):
    tree = ast.parse(path.read_text())
    hits = []
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        for t in targets:
            for sub in ast.walk(t):
                if isinstance(sub, ast.Attribute) and sub.attr == attr:
                    hits.append(node.lineno)
                if isinstance(sub, ast.Subscript):
                    v = sub.value
                    if isinstance(v, ast.Attribute) and v.attr == attr:
                        hits.append(node.lineno)
    return hits


def _init_span(path, cls, fn):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == fn:
                    return sub.lineno, sub.end_lineno
    raise AssertionError(f"{cls}.{fn} not found in {path.name}")


def test_traits_written_only_at_spawn():
    """arrays.kappa and arrays.horizon may be assigned only in
    state.py (allocation) and inside Model.__init__ (spawn). A write
    anywhere else in model.py, including step(), is a violation: the
    phase 18 review landed a tick-60 trait rewrite that the first
    version of this scan could not see because it exempted model.py
    wholesale and the runtime check stopped at tick 50."""
    lo, hi = _init_span(CORE / "model.py", "Model", "__init__")
    for attr in ("kappa", "horizon", "wonder_span"):
        for path in sorted(CORE.glob("*.py")):
            hits = _writes_attr(path, attr)
            if path.name == "state.py":
                continue
            if path.name == "model.py":
                bad = [ln for ln in hits if not lo <= ln <= hi]
                assert not bad, (
                    f"model.py writes arrays.{attr} at line {bad[0]}, "
                    f"outside Model.__init__ ({lo}-{hi}): traits are "
                    f"initialization (phase 18 tripwire, review-hardened)"
                )
                continue
            assert not hits, (
                f"{path.name} writes arrays.{attr} at line {hits[0]}: "
                f"traits are initialization (phase 18 tripwire)"
            )


def test_action_deaf_to_attention():
    """action.py prices consequences; it may not know how loudly the
    agent hears its drives."""
    src = (CORE / "action.py").read_text()
    for banned in ("kappa", "attention_sharpness", "attention_floor"):
        assert banned not in src, (
            f"action.py references '{banned}': attention is hearing, "
            f"not pricing (phase 18 tripwire)"
        )


def test_drives_blind_to_the_horizon():
    """drives.py wants; it may not see ahead."""
    src = (CORE / "drives.py").read_text()
    for banned in ("horizon", "prospect"):
        assert banned not in src, (
            f"drives.py references '{banned}': wanting does not see "
            f"ahead (phase 18 tripwire)"
        )


def test_traits_immutable_at_runtime():
    """Fifty live ticks change neither trait by a single bit."""
    from dataclasses import replace
    cfg = replace(Config(), attention_sharpness=2.0, attention_spread=0.5,
                  prospect_horizon=20, prospect_spread=0.5,
                  r_sight=12.0, wonder_horizon=100, wonder_spread=1.0)
    m = Model(cfg, seed=11)
    k0 = m.arrays.kappa.copy()
    h0 = m.arrays.horizon.copy()
    s0 = m.arrays.wonder_span.copy()
    for _ in range(50):
        m.step()
    assert np.array_equal(m.arrays.kappa, k0)
    assert np.array_equal(m.arrays.horizon, h0)
    assert np.array_equal(m.arrays.wonder_span, s0)
