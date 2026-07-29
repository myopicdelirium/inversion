"""Phase 24: birth must bite, against the real organs.

Kill switches in the established style, mutation-verified before
commit (recorded in specs/phase-24.md Deviations): the cradle, the
inheritance channel, the fresh mind, the severed dead, and exact
replay.
"""

from dataclasses import replace

import numpy as np

from core.config import Config
from core.model import Model, golden_hash, run


def _world(**kw):
    cfg = replace(Config(), birth_threshold=0.9, birth_cost=0.4,
                  n_agents=30, n_food=200, **kw)
    return cfg


def test_off_is_absent():
    m = Model(Config(), seed=3)
    assert m.birth_rngs is None


def test_birth_fills_the_cradle_with_an_heir():
    cfg = _world(tau_safety_spread=0.5)
    m = Model(cfg, seed=5)
    # Make a cradle and a certain parent by hand (instrument edit).
    m.arrays.alive[7] = False
    m.arrays.energy[0] = 1.0
    e0 = float(m.arrays.energy[0])
    tau_parent = m.arrays.tau[0].copy()
    m.step()
    assert m.arrays.alive[7], "the cradle stayed empty"
    assert m.arrays.energy[0] <= e0 - cfg.birth_cost + 1e-9, (
        "the parent did not pay"
    )
    assert np.isclose(m.arrays.x[7], m.arrays.x[0], atol=2.0), (
        "the child was not born at its parent's side"
    )
    ratio = m.arrays.tau[7] / tau_parent
    assert not np.allclose(ratio, 1.0), (
        "mutation is dead: the child is a clone"
    )
    assert np.all(ratio > np.exp(-5 * cfg.birth_mutation))
    assert np.all(ratio < np.exp(5 * cfg.birth_mutation)), (
        "mutation out of lognormal bounds: not inheritance"
    )
    assert (m.arrays.weights[7] == 0.0).all(), "the mind was not fresh"


def test_the_dead_stay_dead():
    cfg = replace(_world(), bond_target="partner")
    m = Model(cfg, seed=5)
    # Find a bonded pair; kill one; give someone energy to breed.
    pairs = np.flatnonzero(m.arrays.partner >= 0)
    a = int(pairs[0])
    c = int(m.arrays.partner[a])
    m.arrays.alive[c] = False
    m.arrays.energy[0] = 1.0
    m.step()
    if m.arrays.alive[c]:  # the cradle was used this tick
        assert m.arrays.partner[a] == -1, (
            "a widow was wedded to a stranger's newborn"
        )


def test_replay_is_exact():
    cfg = _world(n_hazard=3)
    h1 = golden_hash(run(cfg, seed=9, ticks=400))
    h2 = golden_hash(run(cfg, seed=9, ticks=400))
    assert h1 == h2, "birth broke determinism"


def test_births_happen_in_a_live_world():
    """Cradles made by hand (30-agent equilibria refuse to kill on
    their own in 600 ticks: recorded); the energy must come from the
    world, and the loop must fill the cradles unprompted."""
    cfg = _world()
    m = Model(cfg, seed=9)
    for _ in range(100):
        m.step()
    m.arrays.alive[[3, 11, 19]] = False
    slots_reborn = 0
    prev_alive = m.arrays.alive.copy()
    for _ in range(60):
        m.step()
        slots_reborn += int((~prev_alive & m.arrays.alive).sum())
        prev_alive = m.arrays.alive.copy()
    assert slots_reborn >= 3, (
        f"only {slots_reborn} of 3 cradles filled in 60 rich-world "
        f"ticks: the loop is dead"
    )
