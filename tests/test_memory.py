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
    # The agent stays in its KNOWN home cell: walking into a fresh
    # cell would itself be discovery under occupancy semantics
    # (Amendment 7), which test_familiarity_is_not_discovery covers.
    world.food_x[:] = 5.0
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
    # Forget it (disappointment: the empty place is in sight, and the
    # agent never leaves its known cell, so no occupancy novelty can
    # contaminate the clock), then re-sight the SAME place: an
    # insertion happens, the clock must not move.
    world.food_timer[:] = 5
    memory_step(mem, arrays, world, cfg, *_blind_percept(),
                cfg.memory_horizon + 1)
    assert mem.mem_seen[0, 0] == -1, "precondition: forgotten"
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


def test_novel_percept_points_at_the_unknown():
    """The quest's percept (Amendment 7): nearest never-known cell,
    unit direction; infinite when the agent's world is complete."""
    from core.memory import novel_percept
    cfg, arrays, world, mem = _harness()
    # Nothing known yet except what this call marks: the percept from
    # a fresh grid points at the agent's own neighborhood first, so
    # mark a few cells by stepping, then ask.
    memory_step(mem, arrays, world, cfg, *_blind_percept(), 0)
    nd, ndx, ndy = novel_percept(mem, arrays, cfg)
    assert np.isfinite(nd[0]) and nd[0] > 0.0
    assert np.isclose(np.hypot(ndx[0], ndy[0]), 1.0)
    # A completed world: no elsewhere remains.
    mem.mem_visited[:] = True
    nd, ndx, ndy = novel_percept(mem, arrays, cfg)
    assert np.isinf(nd[0]) and ndx[0] == 0.0 and ndy[0] == 0.0


def test_occupancy_is_discovery():
    """Standing in a never-known cell resets wonder's clock even with
    nothing to see there; standing there again does not (Amendment 7:
    novelty is occupancy)."""
    cfg, arrays, world, mem = _harness()
    cfg = replace(cfg, wonder_horizon=400)
    world.food_timer[:] = 5
    memory_step(mem, arrays, world, cfg, *_blind_percept(), 0)
    assert mem.mem_last_novel[0] == 0
    arrays.x[0] = 30.0  # a fresh cell, nothing there but ground
    *_, s = memory_step(mem, arrays, world, cfg, *_blind_percept(), 50)
    assert mem.mem_last_novel[0] == 50, (
        "walking somewhere new was not discovery (Amendment 7)"
    )
    assert s[0] == 0.0
    *_, s2 = memory_step(mem, arrays, world, cfg, *_blind_percept(), 60)
    assert mem.mem_last_novel[0] == 50, "the second visit is not novel"


def test_truncated_cell_centers_stay_inside_their_cells():
    """Phase 21 review, confirmed major: at world sizes that do not
    divide by the cell edge, the last cell's nominal center could wrap
    across the torus into cell 0's territory, a phantom target that
    occupancy could never extinguish. Centers are now true midpoints
    of the possibly-truncated cells."""
    from core.memory import make_memory, novel_percept
    cfg = replace(Config(), world_size=13.0, r_eat=3.0, r_sight=12.0,
                  memory_slots=3, wonder_horizon=100)
    arrays = allocate(1, cfg.init_energy)
    arrays.r_sight[:] = cfg.r_sight
    mem = make_memory(1, cfg)
    mem.mem_visited[:] = True
    mem.mem_visited[0, 2, 2] = False  # only the truncated corner unknown
    arrays.x[0] = arrays.y[0] = 12.5  # standing inside it
    world = SimpleNamespace(food_x=np.array([5.0]), food_y=np.array([0.0]),
                            food_timer=np.full(1, 5, dtype=np.int64))
    nd, ndx, ndy = novel_percept(mem, arrays, cfg)
    assert np.isfinite(nd[0]) and nd[0] < 1.0, (
        "the truncated cell's center left its own cell (phantom target)"
    )
    memory_step(mem, arrays, world, cfg, *_blind_percept(), 0)
    nd2, _, _ = novel_percept(mem, arrays, cfg)
    assert np.isinf(nd2[0]), (
        "standing in the last unknown cell did not extinguish it"
    )
