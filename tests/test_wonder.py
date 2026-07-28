"""Phase 19: wonder must bite, against the real organs (Amendment 6).

Kill switches in the phase 18 style, mutation-verified before commit
(recorded in specs/phase-19.md Deviations): the urgency row must be
the percept exactly, the drive must be load bearing in a sighted
world, and it must be structurally incapable of touching a world
without memory even when cranked to maximum.
"""

import numpy as np
from dataclasses import replace

from core.config import Config
from core.drives import WONDER, compute_urgencies
from core.model import Model, golden_hash, run
from core.state import allocate


def test_wonder_urgency_is_the_percept_exactly():
    cfg = Config()
    arrays = allocate(3, cfg.init_energy)
    arrays.alive[:] = True
    stale = np.array([0.0, 0.4, 1.0])
    compute_urgencies(arrays, cfg, np.zeros(3), np.zeros(3),
                      staleness=stale)
    assert np.array_equal(arrays.urgency[:, WONDER], stale)
    compute_urgencies(arrays, cfg, np.zeros(3), np.zeros(3),
                      staleness=None)
    assert np.array_equal(arrays.urgency[:, WONDER], np.zeros(3)), (
        "no private world means no boredom, ever"
    )


def test_wonder_is_load_bearing_in_a_sighted_world():
    """Same seeds, wonder declared on versus off: BEHAVIOR must
    diverge, not bookkeeping. The first version of this switch
    compared full hashes, which the urgency and weight arrays change
    even when the pricing row is dead; the mutation audit caught it
    staying green (specs/phase-19.md Deviations). Behavioral arrays
    only, at a relief the wiring test is entitled to crank: if the
    pricing row is dead, no action ever changes and this goes red."""
    base = dict(r_sight=12.0, memory_slots=8, n_agents=60, n_food=60,
                wonder_relief=1.0)
    on = replace(Config(), **base, wonder_horizon=400)
    off = replace(Config(), **base, wonder_horizon=0)
    t_on = run(on, seed=9, ticks=1500)
    t_off = run(off, seed=9, ticks=1500)
    behavioral_same = all(
        np.array_equal(t_on[k], t_off[k])
        for k in ("x", "y", "energy", "integrity", "fatigue"))
    assert not behavioral_same, (
        "declaring wonder changed no behavior in a sighted world: the "
        "fifth drive is decorative (phase 19 kill switch)"
    )


def test_wonder_structurally_inert_without_memory():
    """N1b: an omniscient world with wonder cranked to maximum must
    run bit-identical to the same world with wonder off. Inertness is
    a consequence of the definition, not a flag."""
    loud = replace(Config(), wonder_horizon=400, wonder_relief=1.0)
    quiet = replace(Config(), wonder_horizon=0)
    h_loud = golden_hash(run(loud, seed=4, ticks=600))
    h_quiet = golden_hash(run(quiet, seed=4, ticks=600))
    assert h_loud == h_quiet, (
        "wonder leaked into a world without memory: Amendment 6's "
        "structural inertness is broken (phase 19 kill switch)"
    )
    m = Model(loud, seed=4)
    assert m.memory is None


def test_boredom_prices_the_quest_deterministically():
    """A mind whose wonder weight dominates, with nothing to eat, no
    one to flee, no reason to rest, and an unknown cell within reach,
    must choose SEEK_NOVEL (Amendment 7: the quest replaced wander's
    serendipity in the table, which this test's predecessor priced).
    Kills the pricing row: with it dead, nothing beats resting still."""
    from core.action import SEEK_NOVEL, select_actions

    cfg = Config()
    arrays = allocate(1, cfg.init_energy)
    arrays.alive[:] = True
    arrays.weights[:] = [0.0, 0.0, 0.001, 0.0, 0.9]
    zero = np.zeros(1)
    inf = np.full(1, np.inf)
    act = select_actions(arrays, cfg, zero, inf, inf,
                         food_dir=(zero, zero), away_dir=(zero, zero),
                         target_dir=(zero, zero), danger_scale=np.ones(1),
                         novel=(np.full(1, 8.0), np.ones(1), np.zeros(1)))
    assert act[0] == SEEK_NOVEL, (
        "a bored agent with elsewhere in reach did not quest: the "
        "SEEK_NOVEL pricing row is dead (phase 21 kill switch)"
    )


def test_wonder_span_is_load_bearing():
    """The personal boredom clock must reach behavior: same seed, one
    model's spans flattened post-spawn, trajectories must diverge
    (the phase 18 flatten trick). If memory.py still divides by the
    config scalar, they collapse into equality."""
    cfg = replace(Config(), r_sight=12.0, memory_slots=8, n_agents=40,
                  n_food=60, wonder_horizon=100, wonder_spread=1.0,
                  wonder_relief=0.1, record_every=1)
    a = Model(cfg, seed=13)
    b = Model(cfg, seed=13)
    b.arrays.wonder_span[:] = float(cfg.wonder_horizon)
    for _ in range(600):
        a.step()
        b.step()
    assert not (np.array_equal(a.arrays.x, b.arrays.x)
                and np.array_equal(a.arrays.energy, b.arrays.energy)), (
        "flattening the boredom clocks changed nothing: wonder_span "
        "is not load bearing (third-guard kill switch)"
    )
