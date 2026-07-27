"""Phase 16 R1: the credence law made exact, against the REAL organ.

R1 is a kill switch (specs/phase-16.md): under consecutive false
windows credence must equal cred_init * (1-g)^k machine-exact, and a
verified window must apply c += g*(1-c) exactly. The adversarial
review found the first version of these tests recomputed the law in
Python and compared it to itself, so a wrong gain in the code passed;
these tests drive core/social.py's social_step directly and were
proven to fail under a doubled gain (mutation check recorded in
specs/phase-16.md Deviations).
"""

import numpy as np
import pytest
from dataclasses import replace

from core.config import Config
from core.model import Model
from core.social import make_social, social_step
from core.state import allocate


def _harness(n=2):
    """A hand-built two-agent world: agent 1 screams, agent 0 listens
    from distance 3. No Model, no RNG: the organ alone."""
    cfg = replace(Config(), r_social=8.0, testimony=1.0, n_agents=n)
    arrays = allocate(n, cfg.init_energy)
    arrays.x[:] = [0.0, 0.0][:n] if n == 2 else 0.0
    arrays.y[:n] = [0.0, 3.0][:n] if n == 2 else 0.0
    arrays.urgency[1, 1] = 0.9  # signaler's displayed safety urgency
    social = make_social(n, cfg)
    return cfg, arrays, social


def test_false_windows_follow_the_law_exactly():
    """k consecutive unverified windows: credence must equal
    cred_init stepped k times by the organ's own arithmetic, and that
    must equal the closed form to within float roundoff."""
    cfg, arrays, social = _harness()
    danger = np.zeros(2)
    k_targets = {}
    expected = cfg.cred_init
    g = 1.0 - np.exp(-cfg.verify_window / cfg.tau_cred)
    for k in range(1, 5):
        expected = expected + g * (0.0 - expected)
        k_targets[k] = expected
    closes = 0
    for tick in range(4 * cfg.verify_window + 1):
        before = social.credence[0, 1]
        social_step(social, arrays, cfg, danger, tick)
        if social.credence[0, 1] != before:
            closes += 1
            assert social.credence[0, 1] == k_targets[closes], (
                f"close {closes}: organ produced "
                f"{social.credence[0, 1]!r}, law says "
                f"{k_targets[closes]!r} (R1 kill switch)"
            )
    assert closes == 4, f"expected 4 window closes, saw {closes}"
    closed_form = cfg.cred_init * (1.0 - g) ** 4
    assert social.credence[0, 1] == pytest.approx(closed_form, abs=1e-12)


def test_verified_window_scores_one_exactly():
    """Peril reaching the listener inside [open, close) scores 1 and
    applies c += g*(1-c) exactly; peril at the closing tick does not
    count (specs/phase-16.md Honesty notes)."""
    cfg, arrays, social = _harness()
    g = 1.0 - np.exp(-cfg.verify_window / cfg.tau_cred)
    danger = np.zeros(2)
    for tick in range(cfg.verify_window + 1):
        d = danger.copy()
        if tick == 10:
            d[0] = cfg.verify_level  # peril reaches the listener
        social_step(social, arrays, cfg, d, tick)
    expected = cfg.cred_init + g * (1.0 - cfg.cred_init)
    assert social.credence[0, 1] == expected, (
        f"verified window: organ produced {social.credence[0, 1]!r}, "
        f"law says {expected!r} (R1 kill switch)"
    )

    # Closing-tick peril must NOT count: fresh organ, peril only at
    # the close.
    cfg, arrays, social = _harness()
    for tick in range(cfg.verify_window + 1):
        d = np.zeros(2)
        if tick == cfg.verify_window:
            d[0] = cfg.verify_level
        social_step(social, arrays, cfg, d, tick)
    expected = cfg.cred_init + g * (0.0 - cfg.cred_init)
    assert social.credence[0, 1] == expected, (
        "peril at the closing tick was scored; the window is "
        "[open, close)"
    )


def test_open_tick_peril_counts():
    """Peril co-occurring with the alarm at the open tick scores 1:
    the registered boundary (specs/phase-16.md Honesty notes)."""
    cfg, arrays, social = _harness()
    g = 1.0 - np.exp(-cfg.verify_window / cfg.tau_cred)
    for tick in range(cfg.verify_window + 1):
        d = np.zeros(2)
        if tick == 0:
            d[0] = cfg.verify_level
        social_step(social, arrays, cfg, d, tick)
    expected = cfg.cred_init + g * (1.0 - cfg.cred_init)
    assert social.credence[0, 1] == expected


def test_social_organ_absent_at_r_social_zero():
    cfg = Config()
    assert cfg.r_social == 0.0
    m = Model(cfg, seed=3)
    assert m.social is None
    for _ in range(5):
        m.step()
    assert m.social is None


def test_credence_moves_only_at_window_close_in_sim():
    """In a live dense world, credence never changes except when a
    window opened exactly verify_window ticks earlier was pending."""
    cfg = replace(Config(), r_social=8.0, testimony=1.0, n_agents=60,
                  n_hazard=9, hazard_drift=0.02)
    m = Model(cfg, seed=96)
    prev = m.social.credence.copy()
    changes = 0
    for _ in range(400):
        due = (m.social.window_open >= 0) & (
            m.social.window_open == m.tick - cfg.verify_window)
        m.step()
        changed = m.social.credence != prev
        if changed.any():
            changes += 1
            assert due.any(), "credence changed with no window due"
            assert changed[due].any() and not changed[~due].any(), (
                "credence changed outside the due window set"
            )
        prev = m.social.credence.copy()
    assert changes > 0, (
        "no window ever closed in 400 dense ticks: the sim guard is "
        "vacuous at this seed, pick another"
    )
