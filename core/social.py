"""The social organ: honest displays, earned credence, testimony.

THIS IS THE ONLY FILE THAT MAY MUTATE CREDENCE (phase 16 chokepoint
rule, tests/test_social_invariants.py). Displays are never stored:
the display IS the safety urgency of the previous tick, read here.

Credence obeys the integrated form of the one law: at each window
close, c += (1 - exp(-W/tau_cred)) * (score - c), which is exactly
W ticks of the uniform lag driven by a constant score. No RNG, no
allocation after construction, pure functions of state: the organ is
deterministic by construction.
"""

from dataclasses import dataclass

import numpy as np

from .drives import SAFETY


@dataclass
class SocialState:
    credence: np.ndarray     # (n, n) listener i's credence in signaler j
    window_open: np.ndarray  # (n, n) tick a verification window opened; -1 = none
    last_peril: np.ndarray   # (n,) latest tick local danger >= verify_level; -1 = never


def make_social(n, config):
    return SocialState(
        credence=np.full((n, n), config.cred_init),
        window_open=np.full((n, n), -1, dtype=np.int64),
        last_peril=np.full(n, -1, dtype=np.int64),
    )


def _torus_delta(d, size):
    return (d + size / 2.0) % size - size / 2.0


def social_step(social, arrays, config, danger, tick):
    """One tick of the social organ, run after danger perception and
    before urgencies. Returns the testimony field: per listener, the
    loudest credence-weighted, distance-discounted display in range.
    """
    alive = arrays.alive
    n = alive.size

    # The listener's own ledger of verified peril, unmediated.
    social.last_peril[alive & (danger >= config.verify_level)] = tick

    # Close windows opened exactly verify_window ticks ago. Score 1 if
    # verified peril reached the listener strictly after the open.
    closing = (social.window_open >= 0) & (
        social.window_open == tick - config.verify_window)
    if closing.any():
        rows, cols = np.nonzero(closing)
        # The window is [open, close): peril at the open tick counts,
        # peril at the closing tick does not (specs/phase-16.md,
        # Honesty notes). Neighbors in shared danger vouch for each
        # other by geography; tightening to strictly-predictive
        # scoring would be a declared change.
        lp = social.last_peril[rows]
        op = social.window_open[rows, cols]
        score = ((lp >= op) & (lp < tick)).astype(float)
        gain = 1.0 - np.exp(-config.verify_window / config.tau_cred)
        social.credence[rows, cols] += gain * (score - social.credence[rows, cols])
        social.window_open[rows, cols] = -1

    # The display is last tick's safety urgency: honest, one tick late.
    display = np.where(alive, arrays.urgency[:, SAFETY], 0.0)

    dx = _torus_delta(arrays.x[None, :] - arrays.x[:, None], config.world_size)
    dy = _torus_delta(arrays.y[None, :] - arrays.y[:, None], config.world_size)
    dist = np.hypot(dx, dy)
    in_range = (dist <= config.r_social) & alive[:, None] & alive[None, :]
    np.fill_diagonal(in_range, False)

    # Open one window per listening pair for every alarm in range.
    alarm = in_range & (display[None, :] >= config.alarm_threshold)
    fresh = alarm & (social.window_open < 0)
    if fresh.any():
        social.window_open[fresh] = tick

    # Testimony: the loudest discounted rumor. cred_floor keeps a
    # whisper of every voice, mirroring the attention floor.
    heard = np.where(
        in_range,
        display[None, :]
        * np.exp(-dist / config.r_social)
        * np.maximum(social.credence, config.cred_floor),
        0.0,
    )
    return heard.max(axis=1)


def eligible_tellers(social, arrays, config):
    """The told place (Amendment 8): who may tell whom. A boolean
    (listener, teller) mask: within r_social, both alive, credence at
    least tell_threshold, never oneself. memory.py receives this as a
    value and never sees credence itself."""
    dx = _torus_delta(arrays.x[None, :] - arrays.x[:, None],
                      config.world_size)
    dy = _torus_delta(arrays.y[None, :] - arrays.y[:, None],
                      config.world_size)
    in_range = np.hypot(dx, dy) <= config.r_social
    np.fill_diagonal(in_range, False)
    return (in_range & arrays.alive[:, None] & arrays.alive[None, :]
            & (social.credence >= config.tell_threshold))


def apply_belief_feedback(social, events, config):
    """Settlement events from the memory of places, applied through
    the one credence law at the window-close gain: a rumor that fed
    scores its teller 1, a rumor that died against the listener's own
    eyes scores 0. social.py remains the sole writer of credence."""
    if not events:
        return
    gain = 1.0 - np.exp(-config.verify_window / config.tau_cred)
    for li, tj, score in events:
        c = social.credence[li, tj]
        social.credence[li, tj] = c + gain * (score - c)


def reset_agent(social, idx, config):
    """A clean ledger for a reborn slot (Amendment 10): initial
    credence in both directions, no open windows."""
    social.credence[idx, :] = config.cred_init
    social.credence[:, idx] = config.cred_init
    social.window_open[idx, :] = -1
    social.window_open[:, idx] = -1
    social.last_peril[idx] = -1
