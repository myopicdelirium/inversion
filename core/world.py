"""The arena: food, hazards, movement, eating, damage, death.

This file mutates body state and positions only. Drive state (weights,
urgencies) is out of bounds here (CLAUDE.md chokepoint rule).
"""

from dataclasses import dataclass

import numpy as np

from .action import FLEE, REST_ACT, SEEK_FOOD, WANDER


@dataclass
class World:
    food_x: np.ndarray    # (n_food,) positions
    food_y: np.ndarray
    food_timer: np.ndarray  # (n_food,) ticks until respawn; 0 = active
    hazard_x: np.ndarray  # (n_hazard,)
    hazard_y: np.ndarray


def spawn_world(config, world_rng):
    return World(
        food_x=world_rng.random(config.n_food) * config.world_size,
        food_y=world_rng.random(config.n_food) * config.world_size,
        food_timer=np.zeros(config.n_food, dtype=np.int64),
        hazard_x=world_rng.random(config.n_hazard) * config.world_size,
        hazard_y=world_rng.random(config.n_hazard) * config.world_size,
    )


def _torus_delta(dx, size):
    # Shortest signed displacement on the torus.
    return (dx + size / 2.0) % size - size / 2.0


def perceive_danger(arrays, world, config, hazards_active):
    """Per agent: danger is exp(-distance to nearest hazard center /
    r_hazard); the flee direction is straight away from that center.
    Returns (danger, away_dx, away_dy), all zero before hazard onset
    or with no hazards."""
    n = arrays.x.shape[0]
    if world.hazard_x.shape[0] == 0 or not hazards_active:
        return np.zeros(n), np.zeros(n), np.zeros(n)
    dx = _torus_delta(arrays.x[:, None] - world.hazard_x[None, :], config.world_size)
    dy = _torus_delta(arrays.y[:, None] - world.hazard_y[None, :], config.world_size)
    dist = np.hypot(dx, dy)  # (n, n_hazard)
    nearest = np.argmin(dist, axis=1)
    idx = np.arange(n)
    d_near = dist[idx, nearest]
    level = np.exp(-d_near / config.r_hazard)
    # Unit vector away from the nearest center; at the exact center the
    # caller falls back to the agent's heading.
    safe = np.maximum(d_near, 1e-12)
    return level, dx[idx, nearest] / safe, dy[idx, nearest] / safe


def perceive_food(arrays, world, config):
    """Per agent: distance and unit direction to the nearest active
    food source; infinite distance when none is active (global
    perception is a declared Phase 1 simplification)."""
    n = arrays.x.shape[0]
    active = world.food_timer == 0
    if not active.any():
        return np.full(n, np.inf), np.zeros(n), np.zeros(n), np.full(n, -1)
    fx, fy = world.food_x[active], world.food_y[active]
    active_ids = np.flatnonzero(active)
    dx = _torus_delta(fx[None, :] - arrays.x[:, None], config.world_size)
    dy = _torus_delta(fy[None, :] - arrays.y[:, None], config.world_size)
    dist = np.hypot(dx, dy)  # (n, n_active)
    nearest = np.argmin(dist, axis=1)
    idx = np.arange(n)
    d_near = dist[idx, nearest]
    safe = np.maximum(d_near, 1e-12)
    return (
        d_near,
        dx[idx, nearest] / safe,
        dy[idx, nearest] / safe,
        active_ids[nearest],
    )


def apply_actions(arrays, config, actions, food_dir, away_dir, heading_draws):
    """Per agent: redraw the wander heading with probability 0.05, then
    move one tick in the chosen action's direction at fatigue-scaled
    speed. Resting agents do not move. Movement costs energy and builds
    fatigue; resting sheds fatigue; everyone pays the basal burn."""
    redraw_p, redraw_angle = heading_draws
    new_heading = redraw_p < 0.05
    arrays.heading[new_heading] = redraw_angle[new_heading] * 2.0 * np.pi

    v_eff = config.speed * (1.0 - arrays.fatigue / 2.0)
    head_dx, head_dy = np.cos(arrays.heading), np.sin(arrays.heading)
    food_dx, food_dy = food_dir
    away_dx, away_dy = away_dir
    # Seeking with no active food and fleeing from the exact hazard
    # center both fall back to the heading direction.
    no_food_target = (food_dx == 0.0) & (food_dy == 0.0)
    food_dx = np.where(no_food_target, head_dx, food_dx)
    food_dy = np.where(no_food_target, head_dy, food_dy)
    no_away = (away_dx == 0.0) & (away_dy == 0.0)
    away_dx = np.where(no_away, head_dx, away_dx)
    away_dy = np.where(no_away, head_dy, away_dy)

    dir_x = np.select(
        [actions == SEEK_FOOD, actions == FLEE, actions == WANDER],
        [food_dx, away_dx, head_dx],
        default=0.0,
    )
    dir_y = np.select(
        [actions == SEEK_FOOD, actions == FLEE, actions == WANDER],
        [food_dy, away_dy, head_dy],
        default=0.0,
    )
    moving = arrays.alive & (actions != REST_ACT)
    arrays.x[moving] = (arrays.x[moving] + v_eff[moving] * dir_x[moving]) % config.world_size
    arrays.y[moving] = (arrays.y[moving] + v_eff[moving] * dir_y[moving]) % config.world_size

    arrays.energy[arrays.alive] -= config.basal_burn
    arrays.energy[moving] -= config.move_burn
    arrays.fatigue[moving] = np.minimum(arrays.fatigue[moving] + config.fatigue_rate, 1.0)
    resting = arrays.alive & (actions == REST_ACT)
    arrays.fatigue[resting] = np.maximum(arrays.fatigue[resting] - config.rest_rate, 0.0)


def apply_eating(arrays, world, config, dist_food, nearest_food_id):
    """Per agent: if the nearest active source is within reach, eat it.
    Everyone within reach of the same source eats it in the same tick;
    the source is then consumed and its respawn clock starts."""
    eaters = arrays.alive & (dist_food < config.r_eat) & (nearest_food_id >= 0)
    if not eaters.any():
        return
    arrays.energy[eaters] = np.minimum(arrays.energy[eaters] + config.gain_eat, 1.0)
    consumed = np.unique(nearest_food_id[eaters])
    world.food_timer[consumed] = config.food_respawn


def apply_damage_and_deaths(arrays, world, config, hazards_active):
    """Per agent: standing inside a hazard erodes integrity; outside,
    integrity slowly heals toward full, so damage is an equilibrium
    rather than a one-way ratchet. An agent whose energy or integrity
    reaches zero dies, permanently."""
    n = arrays.x.shape[0]
    if hazards_active and world.hazard_x.shape[0] > 0:
        dx = _torus_delta(arrays.x[:, None] - world.hazard_x[None, :], config.world_size)
        dy = _torus_delta(arrays.y[:, None] - world.hazard_y[None, :], config.world_size)
        inside = (np.hypot(dx, dy) < config.r_hazard).any(axis=1)
    else:
        inside = np.zeros(n, dtype=bool)
    hit = arrays.alive & inside
    arrays.integrity[hit] = np.maximum(arrays.integrity[hit] - config.damage_rate, 0.0)
    heal = arrays.alive & ~inside
    arrays.integrity[heal] = np.minimum(arrays.integrity[heal] + config.regen_rate, 1.0)
    arrays.alive &= (arrays.energy > 0.0) & (arrays.integrity > 0.0)


def update_world(world, config, world_rng):
    """Hazards drift by a small random-walk step; consumed food clocks
    tick down and expired sources respawn at fresh random locations.
    All randomness from the world stream, in fixed order."""
    n_hazard = world.hazard_x.shape[0]
    if n_hazard > 0 and config.hazard_drift > 0.0:
        step = world_rng.normal(0.0, config.hazard_drift, size=(2, n_hazard))
        world.hazard_x = (world.hazard_x + step[0]) % config.world_size
        world.hazard_y = (world.hazard_y + step[1]) % config.world_size
    respawning = world.food_timer == 1
    world.food_timer = np.maximum(world.food_timer - 1, 0)
    k = int(respawning.sum())
    if k > 0:
        world.food_x[respawning] = world_rng.random(k) * config.world_size
        world.food_y[respawning] = world_rng.random(k) * config.world_size
