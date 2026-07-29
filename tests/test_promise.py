"""Phase 23: the promised place must bite, against the real organs.

Kill switches in the established style, mutation-verified before
commit (recorded in specs/phase-23.md Deviations): seeding, spread
and stickiness, both settlement directions, the theology of foresight
(myopia cannot want a future), and the dormant burst.
"""

from dataclasses import replace

import numpy as np

from core.config import Config
from core.memory import (has_believers, make_memory, promise_percept,
                         promise_step, take_events)
from core.model import Model
from core.state import allocate
from core.world import deliver_promise, spawn_world
from core.rng import spawn_streams


def _world(n=8, **kw):
    from types import SimpleNamespace
    cfg = replace(Config(), r_sight=12.0, memory_slots=3, r_social=8.0,
                  tell_places=True, prophecy_tick=2000,
                  prophecy_seed_tick=500, prophecy_seeds=5, **kw)
    arrays = allocate(n, cfg.init_energy)
    arrays.x[:] = np.arange(n) * 3.0
    arrays.y[:] = 0.0
    arrays.r_sight[:] = cfg.r_sight
    bare = SimpleNamespace(food_x=np.zeros(0), food_y=np.zeros(0),
                           food_timer=np.zeros(0, dtype=np.int64))
    return cfg, arrays, make_memory(n, cfg), bare


def test_seeding_and_spread_and_stickiness():
    cfg, arrays, mem, w = _world()
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, 499)
    assert not has_believers(mem), "believed before the seeding tick"
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, 500)
    assert mem.prom_active[:5].all() and not mem.prom_active[5:].any()
    assert (mem.prom_from[:5] == -1).all(), "the apparatus has no name"
    # Agent 6 hears from the lowest-indexed eligible believer.
    elig = np.zeros((8, 8), dtype=bool)
    elig[6, 2] = True
    elig[6, 4] = True
    promise_step(mem, arrays, w, cfg, elig, 50.0, 50.0, 501)
    assert mem.prom_active[6] and mem.prom_from[6] == 2
    # Faith is sticky: a louder later mouth changes nothing.
    elig2 = np.zeros((8, 8), dtype=bool)
    elig2[6, 4] = True
    promise_step(mem, arrays, w, cfg, elig2, 50.0, 50.0, 502)
    assert mem.prom_from[6] == 2


def test_false_promise_settles_at_the_grace_edge():
    cfg, arrays, mem, w = _world()
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, 500)
    elig = np.zeros((8, 8), dtype=bool)
    elig[6, 0] = True
    promise_step(mem, arrays, w, cfg, elig, 50.0, 50.0, 501)
    # Agent 6 keeps the vigil at the site; agent 0 (seed) stays away.
    arrays.x[6], arrays.y[6] = 50.0, 45.0
    end = cfg.prophecy_tick + cfg.prophecy_grace
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, end)
    ev = take_events(mem)
    assert (6, 0, 0.0) in ev, "the empty field did not cost the mouth"
    assert not any(li == 0 for li, _, _ in ev), (
        "a seed with no mouth to blame emitted an event"
    )
    assert not has_believers(mem), "faith survived the reckoning"
    assert mem.prom_settled[6], "spent faith must be marked"
    # One faith per prophecy: the settled cannot be re-told.
    elig3 = np.zeros((8, 8), dtype=bool)
    elig3[6, 1] = True
    mem.prom_active[1] = True
    promise_step(mem, arrays, w, cfg, elig3, 50.0, 50.0, end + 1)


def test_true_promise_settles_on_witnessed_food_only():
    from types import SimpleNamespace
    cfg, arrays, mem, w = _world(prophecy_true=True)
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, 500)
    elig = np.zeros((8, 8), dtype=bool)
    elig[6, 0] = True
    promise_step(mem, arrays, w, cfg, elig, 50.0, 50.0, 501)
    arrays.x[6], arrays.y[6] = 50.0, 45.0
    # The site is bare (burst eaten or not yet seen): mere visibility
    # settles NOTHING (review fix: faith settled on scenery).
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, cfg.prophecy_tick + 1)
    assert not take_events(mem), "faith settled on scenery"
    assert mem.prom_active[6]
    # The feast stands at the site: now the witness settles TRUE.
    fed = SimpleNamespace(food_x=np.array([50.0, 53.0]),
                          food_y=np.array([50.0, 50.0]),
                          food_timer=np.zeros(2, dtype=np.int64))
    promise_step(mem, arrays, fed, cfg, None, 50.0, 50.0,
                 cfg.prophecy_tick + 2)
    ev = take_events(mem)
    assert (6, 0, 1.0) in ev, "the witnessed feast did not pay its mouth"
    assert not mem.prom_active[6] and mem.prom_settled[6]


def test_myopia_cannot_want_a_future():
    from core.action import SEEK_PROMISE, select_actions
    cfg = replace(Config(), prophecy_tick=2000, prophecy_size=0.3)
    arrays = allocate(1, cfg.init_energy)
    arrays.alive[:] = True
    arrays.weights[:] = [0.9, 0.0, 0.001, 0.0, 0.0]
    zero, inf = np.zeros(1), np.full(1, np.inf)
    prom = (np.full(1, 10.0), np.ones(1), np.zeros(1), 30)
    act = select_actions(arrays, cfg, zero, inf, inf,
                         food_dir=(zero, zero), away_dir=(zero, zero),
                         target_dir=(zero, zero), danger_scale=np.ones(1),
                         promise=prom)
    assert act[0] != SEEK_PROMISE, "a myopic mind wanted a future"
    # After the hour, the same mind goes.
    prom_now = (np.full(1, 10.0), np.ones(1), np.zeros(1), 0)
    act = select_actions(arrays, cfg, zero, inf, inf,
                         food_dir=(zero, zero), away_dir=(zero, zero),
                         target_dir=(zero, zero), danger_scale=np.ones(1),
                         promise=prom_now)
    assert act[0] == SEEK_PROMISE
    # The farsighted mind waits before the hour arrives.
    cfg_far = replace(cfg, prospect_horizon=60)
    arrays.horizon[:] = 60.0
    act = select_actions(arrays, cfg_far, zero, inf, inf,
                         food_dir=(zero, zero), away_dir=(zero, zero),
                         target_dir=(zero, zero), danger_scale=np.ones(1),
                         promise=prom)
    assert act[0] == SEEK_PROMISE, "foresight refused a priced future"


def test_burst_sleeps_until_delivered():
    cfg = replace(Config(), prophecy_tick=2000, prophecy_burst=20)
    world_rng, _ = spawn_streams(3, cfg.n_agents)
    world = spawn_world(cfg, world_rng)
    assert world.food_x.size == cfg.n_food + 20
    assert (world.food_timer[-20:] > 10 ** 8).all(), "burst awake early"
    deliver_promise(world, cfg, 50.0, 50.0)
    assert (world.food_timer[-20:] == 0).all()
    d = np.hypot(world.food_x[-20:] - 50.0, world.food_y[-20:] - 50.0)
    assert np.allclose(d, 3.0), "the ring is not where it was foretold"


def test_promise_percept_is_believers_only_and_arrival_waits():
    cfg, arrays, mem, w = _world()
    promise_step(mem, arrays, w, cfg, None, 50.0, 50.0, 500)
    d, dx, dy = promise_percept(mem, arrays, cfg, 50.0, 50.0)
    assert np.isfinite(d[:5]).all()
    assert np.isinf(d[5:]).all() and (dx[5:] == 0.0).all()
    # Within the arrival radius the direction is zero: the believer
    # waits instead of bouncing across the point (review fix).
    arrays.x[0], arrays.y[0] = 50.4, 50.0
    d, dx, dy = promise_percept(mem, arrays, cfg, 50.0, 50.0)
    assert d[0] < 1.0 and dx[0] == 0.0 and dy[0] == 0.0


def test_prophecy_needs_the_telling_channel():
    cfg = replace(Config(), r_sight=12.0, memory_slots=8, r_social=8.0,
                  tell_places=False, prophecy_tick=700,
                  prophecy_seed_tick=100, n_agents=30)
    m = Model(cfg, seed=5)
    for _ in range(200):
        m.step()
    assert not has_believers(m.memory), (
        "a prophecy took hold without the telling channel"
    )
