"""Phase 17: the memory of places, driven directly (no Model, no RNG).

The organ's contract: remember what you saw, forget by calendar or by
seeing the place empty, offer the freshest memory when nothing is in
sight, and never touch what the agent wants.
"""

from types import SimpleNamespace
from dataclasses import replace

import numpy as np

from core.config import Config
from core.memory import make_memory, memory_step
from core.model import Model
from core.state import allocate


def _harness(agent_x=0.0):
    cfg = replace(Config(), r_sight=12.0, memory_slots=3)
    arrays = allocate(1, cfg.init_energy)
    arrays.x[0] = agent_x
    arrays.r_sight[:] = cfg.r_sight
    world = SimpleNamespace(food_x=np.array([5.0]),
                            food_y=np.array([0.0]),
                            food_timer=np.zeros(1, dtype=np.int64))
    return cfg, arrays, world, make_memory(1, cfg)


def _blind_percept():
    return (np.array([np.inf]), np.array([0.0]), np.array([0.0]),
            np.array([-1]))


def test_seen_food_is_remembered_and_passes_through():
    cfg, arrays, world, mem = _harness()
    d, dx, dy, ids, _ = memory_step(
        mem, arrays, world, cfg,
        np.array([5.0]), np.array([1.0]), np.array([0.0]), np.array([0]), 0)
    assert mem.mem_seen[0, 0] == 0
    assert mem.mem_x[0, 0] == 5.0 and mem.mem_y[0, 0] == 0.0
    assert d[0] == 5.0 and dx[0] == 1.0 and ids[0] == 0


def test_memory_guides_when_nothing_is_in_sight():
    cfg, arrays, world, mem = _harness()
    memory_step(mem, arrays, world, cfg,
                np.array([5.0]), np.array([1.0]), np.array([0.0]),
                np.array([0]), 0)
    # The agent wanders far; the food is consumed; only memory remains.
    arrays.x[0] = 50.0
    world.food_timer[:] = 5
    d, dx, dy, ids, _ = memory_step(mem, arrays, world, cfg,
                                    *_blind_percept(), 1)
    assert np.isclose(d[0], 45.0)
    assert np.isclose(dx[0], -1.0) and np.isclose(dy[0], 0.0)
    assert ids[0] == -1, "a remembered site is a place, not an edible id"


def test_disappointment_clears_the_slot_on_sight():
    cfg, arrays, world, mem = _harness()
    memory_step(mem, arrays, world, cfg,
                np.array([5.0]), np.array([1.0]), np.array([0.0]),
                np.array([0]), 0)
    # Food consumed while the agent still stands near enough to see
    # the empty place: the memory dies of the evidence.
    world.food_timer[:] = 5
    d, _, _, _, _ = memory_step(mem, arrays, world, cfg,
                                *_blind_percept(), 1)
    assert mem.mem_seen[0, 0] == -1
    assert np.isinf(d[0])


def test_forgetting_by_calendar():
    cfg, arrays, world, mem = _harness()
    memory_step(mem, arrays, world, cfg,
                np.array([5.0]), np.array([1.0]), np.array([0.0]),
                np.array([0]), 0)
    arrays.x[0] = 50.0  # too far to see the site again
    world.food_timer[:] = 5
    d, _, _, _, _ = memory_step(mem, arrays, world, cfg, *_blind_percept(),
                                cfg.memory_horizon + 1)
    assert mem.mem_seen[0, 0] == -1, "memory must expire by calendar"
    assert np.isinf(d[0])


def test_refresh_beats_reinsertion():
    cfg, arrays, world, mem = _harness()
    for tick in (0, 1, 2):
        memory_step(mem, arrays, world, cfg,
                    np.array([5.0]), np.array([1.0]), np.array([0.0]),
                    np.array([0]), tick)
    assert mem.mem_seen[0, 0] == 2, "same site must refresh its slot"
    assert (mem.mem_seen[0] >= 0).sum() == 1, "one site, one slot"


def test_memory_absent_at_r_sight_zero():
    cfg = Config()
    assert cfg.r_sight == 0.0
    m = Model(cfg, seed=3)
    assert m.memory is None
    assert np.all(np.isinf(m.arrays.r_sight))


def test_novelty_clock_and_staleness():
    """Insertion resets wonder's clock; refresh does not; staleness
    climbs toward 1 over wonder_horizon (Amendment 6). The drive is
    declared on here; the default is off and returns no percept."""
    cfg, arrays, world, mem = _harness()
    off = memory_step(mem, arrays, world, cfg, *_blind_percept(), 0)
    assert off[4] is None, "wonder_horizon 0 must yield no percept"
    cfg = replace(cfg, wonder_horizon=400)
    *_, s0 = memory_step(mem, arrays, world, cfg,
                         np.array([5.0]), np.array([1.0]), np.array([0.0]),
                         np.array([0]), 0)
    assert mem.mem_last_novel[0] == 0 and s0[0] == 0.0
    # Refresh at tick 10: same place, no novelty, clock does not move.
    *_, s1 = memory_step(mem, arrays, world, cfg,
                         np.array([5.0]), np.array([1.0]), np.array([0.0]),
                         np.array([0]), 10)
    assert mem.mem_last_novel[0] == 0
    assert np.isclose(s1[0], 10 / cfg.wonder_horizon)
    # A new place at tick 20 resets the clock.
    world.food_x[:] = 40.0
    *_, s2 = memory_step(mem, arrays, world, cfg,
                         np.array([4.0]), np.array([1.0]), np.array([0.0]),
                         np.array([0]), 20)
    assert mem.mem_last_novel[0] == 20 and s2[0] == 0.0
    # Far past the horizon with nothing new: staleness saturates at 1.
    arrays.x[0] = 50.0
    world.food_timer[:] = 5
    *_, s3 = memory_step(mem, arrays, world, cfg, *_blind_percept(),
                         20 + 2 * cfg.wonder_horizon)
    assert s3[0] == 1.0


def test_familiarity_is_not_discovery():
    """The phase 19 review's confirmed major: re-learning a forgotten
    place, or shuttling among more familiar sites than there are
    slots, must not reset wonder's clock. Novelty is judged against
    the lifetime visited grid, not the working slots."""
    cfg, arrays, world, mem = _harness()
    cfg = replace(cfg, wonder_horizon=400)
    # Learn the place at tick 0.
    memory_step(mem, arrays, world, cfg,
                np.array([5.0]), np.array([1.0]), np.array([0.0]),
                np.array([0]), 0)
    assert mem.mem_last_novel[0] == 0
    # Forget it by calendar (agent far away), then re-sight the SAME
    # place: an insertion happens, the clock must not move.
    arrays.x[0] = 50.0
    world.food_timer[:] = 5
    memory_step(mem, arrays, world, cfg, *_blind_percept(),
                cfg.memory_horizon + 1)
    assert mem.mem_seen[0, 0] == -1, "precondition: forgotten"
    arrays.x[0] = 0.0
    world.food_timer[:] = 0
    *_, s = memory_step(mem, arrays, world, cfg,
                        np.array([5.0]), np.array([1.0]), np.array([0.0]),
                        np.array([0]), cfg.memory_horizon + 2)
    assert (mem.mem_seen >= 0).any(), "re-inserted"
    assert mem.mem_last_novel[0] == 0, (
        "re-learning a forgotten place counted as discovery: "
        "familiarity is not novelty (phase 19 review fix)"
    )
    assert s[0] > 0.0
    # A genuinely new cell of the world IS discovery.
    world.food_x[:] = 60.0
    arrays.x[0] = 58.0
    t2 = cfg.memory_horizon + 3
    memory_step(mem, arrays, world, cfg,
                np.array([2.0]), np.array([1.0]), np.array([0.0]),
                np.array([0]), t2)
    assert mem.mem_last_novel[0] == t2
