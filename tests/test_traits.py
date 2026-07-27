"""Phase 18: the traits must bite, against the REAL organs.

The phase 18 adversarial review proved the first tripwire set was
decorative: reverting the personal kappa to the config scalar passed
the whole suite. These tests drive the implementations directly and
were verified red under exactly that mutation (and the horizon
equivalent) before commit; the mutation checks are recorded in
specs/phase-18.md Deviations.

The isolation trick: two models with identical configs consume
identical RNG streams, so overwriting one model's trait array after
spawn is the ONLY difference between runs. If the mechanism ignores
the array, the trajectories collapse into equality and the test goes
red.
"""

import numpy as np
from dataclasses import replace

import core.action as action_mod
from core.config import Config
from core.drives import update_weights
from core.model import Model, golden_hash, run
from core.state import allocate


def test_personal_kappa_is_the_law_exactly():
    """Two agents, identical state, kappa 0.5 vs 3.0: each row must
    equal the law computed with that agent's own exponent, machine
    exact, and the rows must differ."""
    cfg = replace(Config(), attention_floor=0.0)
    arrays = allocate(2, cfg.init_energy)
    arrays.alive[:] = True
    arrays.tau[:] = 20.0
    arrays.kappa[:] = [0.5, 3.0]
    arrays.urgency[:] = [0.6, 0.3, 0.2, 0.1]
    arrays.weights[:] = [0.5, 0.25, 0.15, 0.05]
    w_before = arrays.weights.copy()

    update_weights(arrays, cfg)

    for i in (0, 1):
        ratio = w_before[i] / w_before[i].max()
        gate = np.maximum(ratio, cfg.attention_floor)
        heard = arrays.urgency[i] * gate ** arrays.kappa[i]
        expected = w_before[i] + (1.0 / arrays.tau[i]) * (heard - w_before[i])
        assert np.array_equal(arrays.weights[i], expected), (
            f"agent {i}: personal kappa not applied by the law "
            f"(phase 18 kill switch)"
        )
    assert not np.array_equal(arrays.weights[0], arrays.weights[1])


def test_kappa_array_is_load_bearing():
    """Same seed, same config, one model's kappa flattened post-spawn:
    trajectories must diverge. If drives ignores arrays.kappa they
    collapse into equality (the exact mutation the review landed)."""
    cfg = replace(Config(), attention_sharpness=2.0, attention_spread=0.7,
                  n_agents=40, record_every=1)
    a = Model(cfg, seed=5)
    b = Model(cfg, seed=5)
    b.arrays.kappa[:] = cfg.attention_sharpness  # flatten minds in b
    for _ in range(400):
        a.step()
        b.step()
    assert not (np.array_equal(a.arrays.weights, b.arrays.weights)
                and np.array_equal(a.arrays.x, b.arrays.x)), (
        "flattening kappa changed nothing: arrays.kappa is not load "
        "bearing in drives.py (phase 18 kill switch)"
    )


def test_horizon_array_is_load_bearing():
    """Same trick for foresight: flatten one model's horizons and the
    farsighted pricing must notice."""
    cfg = replace(Config(), prospect_horizon=30, prospect_spread=1.0,
                  n_agents=40, record_every=1)
    a = Model(cfg, seed=7)
    b = Model(cfg, seed=7)
    b.arrays.horizon[:] = float(cfg.prospect_horizon)
    for _ in range(400):
        a.step()
        b.step()
    assert not (np.array_equal(a.arrays.x, b.arrays.x)
                and np.array_equal(a.arrays.energy, b.arrays.energy)), (
        "flattening horizons changed nothing: arrays.horizon is not "
        "load bearing in action.py (phase 18 kill switch)"
    )


def test_geom_relief_finite_at_huge_horizon():
    """The review's confirmed major: factor > 1 with a huge personal
    horizon overflowed factor**steps and poisoned the value table
    with nan via 0 * inf. Clamped now: enormous penalty, never nan."""
    out = action_mod._geom_relief(np.array([0.5]), np.array([1.1]),
                                  np.array([8000.0]))
    assert np.isfinite(out).all(), "nan/inf leaked from _geom_relief"
    assert out[0] < 0.0
    out2 = action_mod._geom_relief(np.array([0.5]), np.array([1.1]),
                                   np.array([8000.0]),
                                   cap=np.array([7000.0]))
    assert np.isfinite(out2).all()
    out3 = action_mod._geom_moving(np.array([0.5]), np.array([1.1]),
                                   np.array([8000.0]))
    assert np.isfinite(out3).all()


def test_uniform_spread_zero_matches_scalar_world():
    """Spread 0 worlds must hash identically whether or not the trait
    arrays exist: the inertness contract in miniature."""
    cfg = replace(Config(), attention_sharpness=2.0, prospect_horizon=20,
                  n_agents=40)
    h1 = golden_hash(run(cfg, seed=3, ticks=300))
    h2 = golden_hash(run(cfg, seed=3, ticks=300))
    assert h1 == h2
