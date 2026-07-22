"""The arena: food, hazards, movement, eating, damage, death.

This file mutates body state and positions only. Drive state (weights,
urgencies) is out of bounds here (CLAUDE.md chokepoint rule).
"""

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

from .action import FLEE, REST_ACT, RETURN_HOME, SEEK_FOOD, WANDER


@dataclass
class World:
    food_x: np.ndarray    # (n_food,) positions
    food_y: np.ndarray
    food_timer: np.ndarray  # (n_food,) ticks until respawn; 0 = active
    hazard_x: np.ndarray  # (n_hazard,)
    hazard_y: np.ndarray
    nest_x: np.ndarray    # (n_nests,) static nest positions
    nest_y: np.ndarray
    storm_x: float        # storm center (on a nest); nan when disabled
    storm_y: float


def spawn_world(config, world_rng):
    food_x = world_rng.random(config.n_food) * config.world_size
    food_y = world_rng.random(config.n_food) * config.world_size
    hazard_x = world_rng.random(config.n_hazard) * config.world_size
    hazard_y = world_rng.random(config.n_hazard) * config.world_size
    # Nests are drawn after food and hazards; with n_nests = 0 the
    # branch draws nothing, so the world stream is identical to a
    # nest-free (phase 1) world.
    if config.n_nests > 0:
        nest_x = world_rng.random(config.n_nests) * config.world_size
        nest_y = world_rng.random(config.n_nests) * config.world_size
    else:
        nest_x = np.zeros(0)
        nest_y = np.zeros(0)
    # The storm sits exactly on its target nest. Placement consumes no
    # RNG draws, so the world stream is identical with the storm on or
    # off (specs/phase-3.md).
    if config.storm_nest >= 0:
        if config.storm_nest >= config.n_nests:
            raise ValueError(
                f"storm_nest {config.storm_nest} requires n_nests > "
                f"{config.storm_nest}, got {config.n_nests}"
            )
        storm_x = float(nest_x[config.storm_nest])
        storm_y = float(nest_y[config.storm_nest])
    else:
        storm_x = float("nan")
        storm_y = float("nan")
    return World(
        food_x=food_x,
        food_y=food_y,
        food_timer=np.zeros(config.n_food, dtype=np.int64),
        hazard_x=hazard_x,
        hazard_y=hazard_y,
        nest_x=nest_x,
        nest_y=nest_y,
        storm_x=storm_x,
        storm_y=storm_y,
    )


def _torus_delta(dx, size):
    # Shortest signed displacement on the torus.
    return (dx + size / 2.0) % size - size / 2.0


def perceive_danger(arrays, world, config, hazards_active, storm_intensity=0.0):
    """Per agent: danger is the strongest contribution among drifting
    hazards, exp(-d / r_hazard), and the storm,
    intensity * exp(-d / storm_radius); the flee direction is straight
    away from whichever source contributes the most. Returns
    (danger, away_dx, away_dy), all zero with no active sources."""
    n = arrays.x.shape[0]
    level = np.zeros(n)
    away_dx = np.zeros(n)
    away_dy = np.zeros(n)
    if world.hazard_x.shape[0] > 0 and hazards_active:
        dx = _torus_delta(arrays.x[:, None] - world.hazard_x[None, :], config.world_size)
        dy = _torus_delta(arrays.y[:, None] - world.hazard_y[None, :], config.world_size)
        dist = np.hypot(dx, dy)  # (n, n_hazard)
        nearest = np.argmin(dist, axis=1)
        idx = np.arange(n)
        d_near = dist[idx, nearest]
        level = np.exp(-d_near / config.r_hazard)
        # Unit vector away from the nearest center; at the exact center
        # the caller falls back to the agent's heading.
        safe = np.maximum(d_near, 1e-12)
        away_dx = dx[idx, nearest] / safe
        away_dy = dy[idx, nearest] / safe
    if storm_intensity > 0.0:
        sdx = _torus_delta(arrays.x - world.storm_x, config.world_size)
        sdy = _torus_delta(arrays.y - world.storm_y, config.world_size)
        sd = np.hypot(sdx, sdy)
        s_level = storm_intensity * np.exp(-sd / config.storm_radius)
        safe = np.maximum(sd, 1e-12)
        # Per agent: the stronger source dictates both the felt danger
        # and the direction of retreat.
        storm_wins = s_level > level
        away_dx = np.where(storm_wins, sdx / safe, away_dx)
        away_dy = np.where(storm_wins, sdy / safe, away_dy)
        level = np.maximum(level, s_level)
    return level, away_dx, away_dy


def perceive_food(arrays, world, config):
    """Per agent: distance and unit direction to the nearest active
    food source; infinite distance when none is active (global
    perception is a declared Phase 1 simplification).

    The periodic KD-tree selects only the *index* of the nearest
    source; distance and direction are recomputed with the same torus
    arithmetic as ever, so outputs are bit-identical to the old
    all-pairs argmin whenever the indices agree, and ties are
    measure-zero because respawn positions are continuous. The tree
    is what makes 10k+ agents affordable (specs/phase-5.md)."""
    n = arrays.x.shape[0]
    active = world.food_timer == 0
    if not active.any():
        return np.full(n, np.inf), np.zeros(n), np.zeros(n), np.full(n, -1)
    fx, fy = world.food_x[active], world.food_y[active]
    active_ids = np.flatnonzero(active)
    size = config.world_size
    # Food positions are strictly inside [0, size); agent positions can
    # land exactly on size through the float modulo, which is the same
    # torus point as 0. Canonicalize the query only; state is untouched.
    qx = np.where(arrays.x >= size, 0.0, arrays.x)
    qy = np.where(arrays.y >= size, 0.0, arrays.y)
    tree = cKDTree(np.column_stack([fx, fy]), boxsize=size)
    _, nearest = tree.query(np.column_stack([qx, qy]))
    dx = _torus_delta(fx[nearest] - arrays.x, size)
    dy = _torus_delta(fy[nearest] - arrays.y, size)
    d_near = np.hypot(dx, dy)
    safe = np.maximum(d_near, 1e-12)
    return d_near, dx / safe, dy / safe, active_ids[nearest]


def perceive_home(arrays, config):
    """Per agent: distance and unit direction to its own home nest;
    infinite distance and zero direction for homeless agents."""
    has_home = np.isfinite(arrays.home_x)
    # Substitute the agent's own position for missing homes so the
    # torus arithmetic stays finite, then mask the results.
    hx = np.where(has_home, arrays.home_x, arrays.x)
    hy = np.where(has_home, arrays.home_y, arrays.y)
    dx = _torus_delta(hx - arrays.x, config.world_size)
    dy = _torus_delta(hy - arrays.y, config.world_size)
    d = np.hypot(dx, dy)
    safe = np.maximum(d, 1e-12)
    dir_x = np.where(has_home, dx / safe, 0.0)
    dir_y = np.where(has_home, dy / safe, 0.0)
    return np.where(has_home, d, np.inf), dir_x, dir_y


def apply_bond(arrays, config, dist_home):
    """Per agent with a home: attachment grows while at the nest and
    fades while away. Both updates are contractions within [0, 1], so
    no clipping is needed and the declared rates hold exactly."""
    has_home = np.isfinite(dist_home)
    at_home = arrays.alive & has_home & (dist_home < config.r_nest)
    away = arrays.alive & has_home & ~(dist_home < config.r_nest)
    arrays.bond[at_home] += config.bond_grow * (1.0 - arrays.bond[at_home])
    arrays.bond[away] -= config.bond_decay * arrays.bond[away]


def apply_actions(arrays, config, actions, food_dir, away_dir, home_dir, heading_draws):
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
    home_dx, home_dy = home_dir
    # Seeking with no active food, fleeing from the exact hazard
    # center, and returning with no home all fall back to the heading
    # direction.
    no_food_target = (food_dx == 0.0) & (food_dy == 0.0)
    food_dx = np.where(no_food_target, head_dx, food_dx)
    food_dy = np.where(no_food_target, head_dy, food_dy)
    no_away = (away_dx == 0.0) & (away_dy == 0.0)
    away_dx = np.where(no_away, head_dx, away_dx)
    away_dy = np.where(no_away, head_dy, away_dy)
    no_home = (home_dx == 0.0) & (home_dy == 0.0)
    home_dx = np.where(no_home, head_dx, home_dx)
    home_dy = np.where(no_home, head_dy, home_dy)

    dir_x = np.select(
        [actions == SEEK_FOOD, actions == FLEE, actions == WANDER,
         actions == RETURN_HOME],
        [food_dx, away_dx, head_dx, home_dx],
        default=0.0,
    )
    dir_y = np.select(
        [actions == SEEK_FOOD, actions == FLEE, actions == WANDER,
         actions == RETURN_HOME],
        [food_dy, away_dy, head_dy, home_dy],
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


def apply_damage_and_deaths(arrays, world, config, hazards_active, storm_intensity=0.0):
    """Per agent: standing inside a hazard erodes integrity at the
    hazard rate, standing inside the storm erodes it at the storm rate
    times intensity, and the two add where they overlap; outside all
    damage zones, integrity slowly heals toward full, so damage is an
    equilibrium rather than a one-way ratchet. An agent whose energy or
    integrity reaches zero dies, permanently."""
    n = arrays.x.shape[0]
    if hazards_active and world.hazard_x.shape[0] > 0:
        dx = _torus_delta(arrays.x[:, None] - world.hazard_x[None, :], config.world_size)
        dy = _torus_delta(arrays.y[:, None] - world.hazard_y[None, :], config.world_size)
        inside = (np.hypot(dx, dy) < config.r_hazard).any(axis=1)
    else:
        inside = np.zeros(n, dtype=bool)
    if storm_intensity > 0.0:
        sdx = _torus_delta(arrays.x - world.storm_x, config.world_size)
        sdy = _torus_delta(arrays.y - world.storm_y, config.world_size)
        inside_storm = np.hypot(sdx, sdy) < config.storm_radius
    else:
        inside_storm = np.zeros(n, dtype=bool)
    hit = arrays.alive & inside
    arrays.integrity[hit] = np.maximum(arrays.integrity[hit] - config.damage_rate, 0.0)
    hit_storm = arrays.alive & inside_storm
    arrays.integrity[hit_storm] = np.maximum(
        arrays.integrity[hit_storm] - config.storm_damage * storm_intensity, 0.0
    )
    heal = arrays.alive & ~inside & ~inside_storm
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
