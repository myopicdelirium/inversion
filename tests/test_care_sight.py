"""Through the eyes (phase 25, Amendment 5 addendum): the care percept
gated on the witness's own sight. Default False is bit-inert; the kill
switch must kill; the gate must be exact in both directions; an
infinite eye must see everything (the vacuous-gate arithmetic)."""

import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.drives import BOND  # noqa: E402
from core.model import Model, golden_hash, run  # noqa: E402


def _pair_world(**kw):
    base = dict(bond_target="partner", n_hazard=0, storm_nest=0,
                storm_onset=0, storm_ramp=1, care=1.0, r_sight=12.0,
                memory_slots=8)
    base.update(kw)
    return replace(Config(), **base)


def test_gate_exact_both_directions():
    """A partner in peril within sight is felt exactly as the
    telepathic percept feels it; beyond sight it is exactly zero."""
    cfg = _pair_world(n_agents=4, empathy_sighted=True)
    m = Model(cfg, seed=3)
    m.arrays.partner[:] = (1, 0, 3, 2)
    m.arrays.alive[:] = True
    sx, sy = m.world.storm_x, m.world.storm_y
    # Partners 1 and 3 stand at the storm's center; witness 0 in
    # sight, witness 2 beyond it.
    m.arrays.x[:] = (sx + 5.0, sx, sx + 30.0, sx)
    m.arrays.y[:] = (sy, sy, sy, sy)
    d, _, _ = m._bond_distances()
    active, storm = m._hazards_active(), m._storm_intensity()
    assert storm > 0.0
    gated = m._target_peril(active, storm, d)
    m.config = replace(cfg, empathy_sighted=False)
    open_eye = m._target_peril(active, storm, d)
    m.config = cfg
    assert open_eye[0] > 0.0 and open_eye[2] > 0.0
    assert gated[0] == open_eye[0], "in-sight peril must be telepathic"
    assert gated[2] == 0.0, "beyond-sight peril must be exactly zero"


def test_kill_switch_kills():
    """Flipping empathy_sighted in a finite-sight partner-peril world
    must change the trajectory: a kill switch that has never killed
    anything is a decoration."""
    cfg = _pair_world(n_agents=60, storm_onset=60, help_strength=1.0)
    h_off = golden_hash(run(cfg, seed=7, ticks=300))
    h_on = golden_hash(run(replace(cfg, empathy_sighted=True),
                           seed=7, ticks=300))
    assert h_off != h_on, "the gate changed nothing where it must bite"


def test_infinite_eye_is_vacuous():
    """With unlimited sight the gate passes everything: empathy_sighted
    is behaviorally invisible, bit for bit."""
    cfg = _pair_world(n_agents=60, storm_onset=60, help_strength=1.0,
                      r_sight=0.0, memory_slots=0)
    h_off = golden_hash(run(cfg, seed=7, ticks=300))
    h_on = golden_hash(run(replace(cfg, empathy_sighted=True),
                           seed=7, ticks=300))
    assert h_off == h_on, "an infinite eye must see everything"


def test_gate_identity_through_the_law():
    """R2's identity, in miniature: along a live gated run, the bond
    urgency the model writes each tick reconstructs exactly from
    pre-step state and the gated percept."""
    cfg = _pair_world(n_agents=40, storm_onset=40, empathy_sighted=True)
    m = Model(cfg, seed=11)
    worst = 0.0
    for _ in range(200):
        d, _, _ = m._bond_distances()
        per = m._target_peril(m._hazards_active(), m._storm_intensity(), d)
        sep = 1.0 - np.exp(-d / cfg.r_bond)
        expected = m.arrays.bond * np.clip(sep + cfg.care * per, 0.0, 1.0)
        alive = m.arrays.alive.copy()
        m.step()
        if alive.any():
            worst = max(worst, float(np.abs(
                m.arrays.urgency[alive, BOND] - expected[alive]).max()))
    assert worst < 1e-9, f"gate identity broken: residual {worst}"
