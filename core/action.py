"""Action valuation and selection. Reads drive state, never writes it
(CLAUDE.md chokepoint rule). The E table is specified in
specs/phase-1.md and phase-2.md; entries may be negative; basal_burn is
omitted because it is common to every action and argmax ignores common
terms.
"""

import numpy as np

from .drives import BOND, ENERGY, REST, SAFETY

ACTION_NAMES = ("seek_food", "flee", "rest", "wander", "return_home")
SEEK_FOOD, FLEE, REST_ACT, WANDER, RETURN_HOME = 0, 1, 2, 3, 4


def select_actions(arrays, config, danger_at_agent, dist_food, dist_home,
                   food_dir=None, away_dir=None, target_dir=None,
                   danger_scale=None, grip_info=None):
    """Per agent: value each action as the weight-weighted sum of
    expected urgency reductions, then take the argmax; ties resolve by
    the frozen action order.

    At prospect_horizon 0: the phase 1 closed forms, bit for bit, and
    the direction arguments are unused. At horizon h > 0 (Amendment 4):
    each action is valued as if held for h ticks, by closed-form
    integrals of predicted urgency under the agent's declared physics
    (straight lines, static fields, no other minds), evaluated under
    the agent's current, frozen weights. Farsighted in consequences,
    myopic in values."""
    if config.prospect_horizon > 0:
        return _select_farsighted(arrays, config, danger_at_agent, dist_food,
                                  dist_home, food_dir, away_dir, target_dir,
                                  danger_scale, grip_info)
    n = arrays.alive.shape[0]
    # Per agent: tired bodies move slower.
    v_eff = config.speed * (1.0 - arrays.fatigue / 2.0)
    # Per agent: ticks of travel to the nearest active food source
    # (infinite when no food is active anywhere).
    travel = dist_food / v_eff

    ev = np.zeros((n, 4, 5))
    # Food's value is its per-tick gain attenuated by travel time;
    # every moving action pays the movement burn.
    ev[:, ENERGY, SEEK_FOOD] = config.gain_eat / (1.0 + travel) - config.move_burn
    ev[:, ENERGY, FLEE] = -config.move_burn
    ev[:, ENERGY, WANDER] = config.wander_gain - config.move_burn
    ev[:, ENERGY, RETURN_HOME] = -config.move_burn
    # One step down the exponential danger field reduces danger by
    # exactly this closed form.
    ev[:, SAFETY, FLEE] = danger_at_agent * (1.0 - np.exp(-v_eff / config.r_hazard))
    # Movement builds fatigue; resting sheds it.
    ev[:, REST, SEEK_FOOD] = -config.fatigue_rate
    ev[:, REST, FLEE] = -config.fatigue_rate
    ev[:, REST, REST_ACT] = config.rest_rate
    ev[:, REST, WANDER] = -config.fatigue_rate
    ev[:, REST, RETURN_HOME] = -config.fatigue_rate
    # One step toward home reduces separation distress by exactly this
    # closed form (zero for homeless agents, whose bond is zero).
    ev[:, BOND, RETURN_HOME] = arrays.bond * np.exp(-dist_home / config.r_bond) * (
        np.exp(v_eff / config.r_bond) - 1.0
    )

    # Per agent: V(a) = sum over drives of weight * expected reduction.
    values = np.einsum("nd,nda->na", arrays.weights, ev)
    return np.argmax(values, axis=1)


def _geom_relief(level, factor, h, cap=None):
    """Per agent: cumulative relief over h ticks when a level changes
    geometrically by `factor` per tick, with the change stopping after
    `cap` ticks (arrival): thereafter the level holds at its arrival
    value. sum_{t=1..min(h,cap)} level*(1-factor^t) plus the held
    tail, all closed form. cap None means the motion never ends."""
    factor = np.clip(factor, 0.0, None)
    if cap is None:
        steps = np.full(np.shape(level), float(h))
    else:
        steps = np.minimum(np.where(np.isfinite(cap), cap, float(h)), float(h))
    near_one = np.isclose(factor, 1.0)
    safe = np.where(near_one, 0.5, factor)
    with np.errstate(over="ignore", invalid="ignore"):
        series = safe * (1.0 - safe ** steps) / (1.0 - safe)
        at_cap = factor ** steps
    series = np.where(near_one, steps, series)
    at_cap = np.where(near_one, 1.0, at_cap)
    moving_part = level * (steps - series)
    held_part = (h - steps) * level * (1.0 - at_cap)
    return moving_part + held_part


def _ramp_relief(rate, saturation, h):
    """Per agent: cumulative effect of a level ramping by `rate` per
    tick until it saturates at `saturation`, then holding:
    sum_{t=1..h} min(rate*t, saturation), closed form."""
    t_sat = np.ceil(saturation / np.maximum(rate, 1e-12))
    steps = np.minimum(t_sat, float(h))
    return rate * steps * (steps + 1) / 2.0 + (h - steps) * np.minimum(
        rate * steps, saturation
    )


def _grip_arrival(dist_outside_part, target_center_dist, v_eff, config,
                  intensity):
    """Full sight (phase 13): predicted arrival ticks at a destination
    inside a gripping storm, under the declared radial approximation:
    an outside leg at normal speed, an inside leg of length (radius
    minus the target's center distance) at gripped speed."""
    inside_leg = np.maximum(0.0, config.storm_radius - target_center_dist)
    outside_leg = np.maximum(0.0, dist_outside_part - inside_leg)
    v_in = np.maximum(v_eff * (1.0 - config.storm_snare * intensity), 1e-6)
    outside_ticks = np.ceil(outside_leg / v_eff)
    return outside_ticks + np.ceil(inside_leg / v_in), outside_ticks


def _geom_moving(level, factor, steps):
    """Per agent: the moving part of the geometric integral only, with
    per-agent step counts: sum_{t=1..steps} level * (1 - factor^t)."""
    factor = np.clip(factor, 0.0, None)
    near_one = np.isclose(factor, 1.0)
    safe = np.where(near_one, 0.5, factor)
    with np.errstate(over="ignore", invalid="ignore"):
        series = safe * (1.0 - safe ** steps) / (1.0 - safe)
    series = np.where(near_one, steps, series)
    return level * (steps - series)


def _select_farsighted(arrays, config, danger, dist_food, dist_target,
                       food_dir, away_dir, target_dir, danger_scale,
                       grip_info=None):
    """The h-tick rollout. Every term is an integral of the same
    physics the myopic table already knew; nothing here reads body
    integrity, and predicted harm enters only as accumulated danger
    exposure along the predicted path."""
    n = arrays.alive.shape[0]
    h = config.prospect_horizon
    v_eff = config.speed * (1.0 - arrays.fatigue / 2.0)
    tri = h * (h + 1) / 2.0  # sum of t for t=1..h; the ramp integral

    sees_grip = (config.prospect_sees_grip and grip_info is not None
                 and grip_info["intensity"] > 0.0
                 and config.storm_snare > 0.0)

    ev = np.zeros((n, 4, 5))

    # Energy. Seeking: pay movement until predicted arrival, then the
    # bite's relief persists for the remaining ticks.
    travel = np.ceil(dist_food / v_eff)
    if sees_grip:
        travel, food_outside_ticks = _grip_arrival(
            dist_food, grip_info["food_center_dist"], v_eff, config,
            grip_info["intensity"])
    ticks_fed = np.maximum(0.0, h - travel + 1.0)
    tc = np.minimum(travel, float(h))
    move_cost_seek = np.where(travel >= h, tri,
                              tc * (tc + 1) / 2.0 + tc * (h - tc))
    ev[:, ENERGY, SEEK_FOOD] = config.gain_eat * ticks_fed - config.move_burn * move_cost_seek
    ev[:, ENERGY, FLEE] = -config.move_burn * tri
    ev[:, ENERGY, WANDER] = (config.wander_gain - config.move_burn) * tri
    ev[:, ENERGY, RETURN_HOME] = -config.move_burn * tri

    # Safety. Danger along a straight path changes geometrically at a
    # rate set by the motion's projection onto the away-from-danger
    # direction: fleeing decays it, approaching a source grows it. This
    # is where the price of a path is felt.
    away_dx, away_dy = away_dir
    food_dx, food_dy = food_dir
    tgt_dx, tgt_dy = target_dir
    scale = np.maximum(danger_scale, 1e-9)
    proj_seek = food_dx * away_dx + food_dy * away_dy
    proj_ret = tgt_dx * away_dx + tgt_dy * away_dy
    arrive_tgt = np.ceil(dist_target / v_eff)
    # Fleeing never arrives anywhere; targeted motion stops changing
    # the danger at arrival and holds the arrival level thereafter.
    ev[:, SAFETY, FLEE] = _geom_relief(danger, np.exp(-v_eff / scale), h)
    if sees_grip:
        # Full sight: the outside leg is priced geometrically; every
        # tick after it (the gripped crawl plus the held remainder) is
        # priced at the danger at the destination, an overestimate of
        # the crawl, so the seen price errs high (specs/phase-13.md).
        intensity = grip_info["intensity"]
        ret_total, ret_outside = _grip_arrival(
            dist_target, grip_info["target_center_dist"], v_eff, config,
            intensity)
        danger_food_tgt = intensity * np.exp(
            -grip_info["food_center_dist"] / config.storm_radius)
        danger_bond_tgt = intensity * np.exp(
            -grip_info["target_center_dist"] / config.storm_radius)
        ev[:, SAFETY, SEEK_FOOD] = _geom_moving(
            danger, np.exp(-v_eff * proj_seek / scale),
            np.minimum(food_outside_ticks, float(h))
        ) + np.maximum(0.0, h - food_outside_ticks) * (danger - danger_food_tgt)
        ev[:, SAFETY, RETURN_HOME] = _geom_moving(
            danger, np.exp(-v_eff * proj_ret / scale),
            np.minimum(ret_outside, float(h))
        ) + np.maximum(0.0, h - ret_outside) * (danger - danger_bond_tgt)
        arrive_tgt = ret_total
    else:
        ev[:, SAFETY, SEEK_FOOD] = _geom_relief(
            danger, np.exp(-v_eff * proj_seek / scale), h, cap=travel)
        ev[:, SAFETY, RETURN_HOME] = _geom_relief(
            danger, np.exp(-v_eff * proj_ret / scale), h, cap=arrive_tgt)

    # Rest: fatigue floors at zero and saturates at one; both bounds
    # are respected in the integrals.
    move_fatigue = _ramp_relief(config.fatigue_rate, 1.0 - arrays.fatigue, h)
    for act in (SEEK_FOOD, FLEE, WANDER, RETURN_HOME):
        ev[:, REST, act] = -move_fatigue
    ev[:, REST, REST_ACT] = _ramp_relief(config.rest_rate, arrays.fatigue, h)

    # Bond: approaching the target shrinks distress along the way, and
    # arriving within the horizon buys its full relief for the
    # remaining ticks. An absent target (infinite distance) buys
    # nothing: grief has no destination, seen or unseen.
    # Per tick while approaching: u(t) = 1 - exp(-(d0 - v t)/r_bond),
    # so relief vs now is base*(ratio^t - 1); sum it in closed form,
    # then add the settled ticks after arrival.
    d0 = dist_target
    arrive = arrive_tgt
    u_now = 1.0 - np.exp(-d0 / config.r_bond)
    # The distress can only shrink for as long as the distance does:
    # the shrink clock is unstretched even when the arrival clock is
    # grip-stretched; only the settled relief waits for true arrival.
    shrink = np.ceil(d0 / v_eff)
    steps = np.minimum(np.where(np.isfinite(shrink), shrink, 0.0), h)
    ratio = np.exp(v_eff / config.r_bond)
    base = np.exp(-d0 / config.r_bond)
    with np.errstate(over="ignore", invalid="ignore"):
        geo = base * ratio * (ratio ** steps - 1.0) / (ratio - 1.0)
    geo = np.where(np.isfinite(geo), geo, 0.0)
    approach_relief = geo - steps * base
    settled = np.maximum(0.0, h - np.where(np.isfinite(arrive), arrive, np.inf))
    settled = np.where(np.isfinite(settled), settled, 0.0)
    ev[:, BOND, RETURN_HOME] = arrays.bond * (
        approach_relief + settled * u_now
    )

    values = np.einsum("nd,nda->na", arrays.weights, ev)
    return np.argmax(values, axis=1)
