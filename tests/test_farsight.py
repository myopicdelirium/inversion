"""Farsight (phase 11, Amendment 4). Selection under a nonzero horizon
is a pure function of state: two identical models must choose
identically at every tick, which reconstructs V-and-argmax exactly.
"""

from dataclasses import replace

import numpy as np

from core.config import Config
from core.model import Model


def test_farsighted_selection_reconstructs():
    cfg = replace(Config(), n_hazard=0, storm_nest=0, storm_onset=100,
                  storm_ramp=1, bond_init=1.0, prospect_horizon=60,
                  n_agents=80)
    a = Model(cfg, seed=9)
    b = Model(cfg, seed=9)
    for _ in range(300):
        act_a = a.step()
        act_b = b.step()
        assert np.array_equal(act_a, act_b)
    assert np.array_equal(a.arrays.weights, b.arrays.weights)
