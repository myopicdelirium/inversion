"""Phase 22: the told place must bite, against the real organs.

Kill switches in the established style, mutation-verified before
commit (recorded in specs/phase-22.md Deviations): the intake, both
settlement directions, the wonder-clock firewall, and the feedback
law, each driven directly through hand-built worlds.
"""

from types import SimpleNamespace
from dataclasses import replace

import numpy as np

from core.config import Config
from core.memory import hear_places, make_memory, memory_step, take_events
from core.model import Model, golden_hash, run
from core.social import apply_belief_feedback, make_social
from core.state import allocate


def _pair_world():
    cfg = replace(Config(), r_sight=12.0, memory_slots=3, r_social=8.0,
                  tell_places=True)
    arrays = allocate(2, cfg.init_energy)
    arrays.x[:] = [0.0, 3.0]
    arrays.y[:] = 0.0
    arrays.r_sight[:] = cfg.r_sight
    arrays.wonder_span[:] = 0.0
    world = SimpleNamespace(food_x=np.array([40.0]),
                            food_y=np.array([0.0]),
                            food_timer=np.zeros(1, dtype=np.int64))
    mem = make_memory(2, cfg)
    # The teller (agent 1) knows the distant place firsthand.
    mem.mem_x[1, 0] = 40.0
    mem.mem_y[1, 0] = 0.0
    mem.mem_seen[1, 0] = 5
    return cfg, arrays, world, mem


def test_telling_requires_credence():
    cfg, arrays, world, mem = _pair_world()
    low = np.zeros((2, 2), dtype=bool)   # nobody eligible
    hear_places(mem, arrays, cfg, low, 10)
    assert not mem.mem_told.any(), "an ineligible teller was heard"
    ok = np.zeros((2, 2), dtype=bool)
    ok[0, 1] = True                      # listener 0 trusts teller 1
    hear_places(mem, arrays, cfg, ok, 10)
    slot = mem.mem_told[0].argmax()
    assert mem.mem_told[0].any(), "an eligible telling did not land"
    assert mem.mem_source[0, slot] == 1
    assert mem.mem_x[0, slot] == 40.0
    assert mem.mem_seen[0, slot] == 5, (
        "secondhand news must age from the teller's sighting"
    )
    assert mem.mem_last_novel[0] == 0, "hearing is not discovery"
    before = mem.mem_told[0].copy()
    hear_places(mem, arrays, cfg, ok, 11)
    assert np.array_equal(mem.mem_told[0], before), (
        "the same place was told twice"
    )


def test_sight_settles_true_and_converts():
    cfg, arrays, world, mem = _pair_world()
    ok = np.zeros((2, 2), dtype=bool)
    ok[0, 1] = True
    hear_places(mem, arrays, cfg, ok, 10)
    # The listener walks there and sees the food with its own eyes.
    arrays.x[0] = 40.0
    memory_step(mem, arrays, world, cfg,
                np.array([0.0, np.inf]), np.array([1.0, 0.0]),
                np.zeros(2), np.array([0, -1]), 20)
    ev = take_events(mem)
    assert (0, 1, 1.0) in ev, "a true rumor did not settle its teller"
    assert not mem.mem_told[0].any(), "settled slot did not convert"


def test_emptiness_settles_false():
    cfg, arrays, world, mem = _pair_world()
    ok = np.zeros((2, 2), dtype=bool)
    ok[0, 1] = True
    hear_places(mem, arrays, cfg, ok, 10)
    world.food_timer[:] = 5  # the place is bare when the listener looks
    arrays.x[0] = 35.0       # close enough to see the told site
    memory_step(mem, arrays, world, cfg,
                np.array([np.inf, np.inf]), np.zeros(2),
                np.zeros(2), np.array([-1, -1]), 20)
    ev = take_events(mem)
    assert (0, 1, 0.0) in ev, "a dead rumor did not cost its teller"
    assert not mem.mem_told[0].any(), "disappointed told slot survived"


def test_feedback_is_the_law_exactly():
    cfg = Config()
    social = make_social(3, cfg)
    gain = 1.0 - np.exp(-cfg.verify_window / cfg.tau_cred)
    c0 = social.credence[0, 1]
    apply_belief_feedback(social, [(0, 1, 1.0), (2, 1, 0.0)], cfg)
    assert social.credence[0, 1] == c0 + gain * (1.0 - c0)
    assert social.credence[2, 1] == c0 + gain * (0.0 - c0)
    assert social.credence[1, 0] == c0, "an uninvolved pair moved"


def test_telling_inert_by_flag_and_by_absence():
    base = dict(r_sight=12.0, memory_slots=8, n_agents=40, n_food=60,
                r_social=8.0)
    on = replace(Config(), **base, tell_places=True)
    off = replace(Config(), **base, tell_places=False)
    h_on = golden_hash(run(on, seed=6, ticks=800))
    h_off = golden_hash(run(off, seed=6, ticks=800))
    assert h_on != h_off, (
        "telling changed nothing in a social sighted world: the "
        "channel is decorative (phase 22 kill switch)"
    )
    # Structurally absent without the social organ, even when flagged.
    asocial = {**base, "r_social": 0.0}
    lone = replace(Config(), **asocial, tell_places=True)
    lone_off = replace(Config(), **asocial, tell_places=False)
    assert golden_hash(run(lone, seed=6, ticks=800)) == golden_hash(
        run(lone_off, seed=6, ticks=800)), (
        "telling leaked into a world with no social organ"
    )
    m = Model(off, seed=6)
    for _ in range(50):
        m.step()
    assert not m.memory.mem_told.any(), "told slots appeared while off"
