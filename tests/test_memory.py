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
    d, dx, dy, ids = memory_step(
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
    d, dx, dy, ids = memory_step(mem, arrays, world, cfg,
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
    d, _, _, _ = memory_step(mem, arrays, world, cfg,
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
    d, _, _, _ = memory_step(mem, arrays, world, cfg, *_blind_percept(),
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
