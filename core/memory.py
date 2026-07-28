"""The memory of places: a private, partial, sometimes wrong world.

THIS IS THE ONLY FILE THAT MAY TOUCH THE REMEMBERED-PLACE ARRAYS
(phase 17 chokepoint rule, tests/test_memory_invariants.py). The organ
holds places only: no drive state, no social ledger, no action table.

An agent remembers up to memory_slots food sites it has actually
seen, each with the tick it was last true. Memories expire after
memory_horizon ticks; a remembered site the agent can currently see
to be empty is cleared on sight: disappointment outruns the
calendar. The composite percept returned here is priced by the
action layer exactly as a seen food would be: ignorance changes what
the agent knows, never how it wants. No RNG anywhere in this file.
"""

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

from .world import _torus_delta


@dataclass
class PlaceMemory:
    mem_x: np.ndarray     # (n, slots) remembered site positions
    mem_y: np.ndarray
    mem_seen: np.ndarray  # (n, slots) tick last seen true; -1 = empty
    mem_last_novel: np.ndarray  # (n,) tick a NEW place last entered
                                # memory; staleness feeds wonder
                                # (Amendment 6)
    mem_visited: np.ndarray     # (n, g, g) lifetime visited-cell grid:
                                # novelty is judged against everywhere
                                # the agent has EVER known, not its
                                # working slots (phase 19 review fix:
                                # familiarity is not discovery)


def _grid_size(config):
    # Cell edge is one eating diameter: two sites in the same cell are
    # the same place for novelty purposes.
    return max(1, int(np.ceil(config.world_size / (2.0 * config.r_eat))))


def make_memory(n, config):
    k = config.memory_slots
    g = _grid_size(config)
    return PlaceMemory(
        mem_x=np.zeros((n, k)),
        mem_y=np.zeros((n, k)),
        mem_seen=np.full((n, k), -1, dtype=np.int64),
        mem_last_novel=np.zeros(n, dtype=np.int64),
        mem_visited=np.zeros((n, g, g), dtype=bool),
    )


def _site_dist(memory, arrays, config):
    dx = _torus_delta(memory.mem_x - arrays.x[:, None], config.world_size)
    dy = _torus_delta(memory.mem_y - arrays.y[:, None], config.world_size)
    return np.hypot(dx, dy), dx, dy


def memory_step(memory, arrays, world, config, dist_food, food_dx,
                food_dy, food_ids, tick):
    """One tick of the memory organ, fed the sighted food percept.
    Returns the composite percept: the seen food if any, else the
    freshest remembered site, else nothing."""
    # Novelty is occupancy (Amendment 7): standing in a cell makes it
    # known, and first knowings reset wonder's clock. Insertion
    # marking below is subsumed but kept: seeing food in a distant
    # new cell is also a first knowing.
    n = arrays.alive.size
    g = memory.mem_visited.shape[1]
    cell = 2.0 * config.r_eat
    ax = np.minimum((arrays.x % config.world_size) // cell, g - 1).astype(np.int64)
    ay = np.minimum((arrays.y % config.world_size) // cell, g - 1).astype(np.int64)
    rows_all = np.arange(n)
    first = arrays.alive & ~memory.mem_visited[rows_all, ax, ay]
    if first.any():
        memory.mem_visited[rows_all[first], ax[first], ay[first]] = True
        memory.mem_last_novel[first] = tick
    valid = memory.mem_seen >= 0

    # Forgetting by calendar.
    expired = valid & (tick - memory.mem_seen > config.memory_horizon)
    memory.mem_seen[expired] = -1
    valid &= ~expired

    # Forgetting by disappointment: a remembered site the agent can
    # see right now, with no active food standing at it, is cleared.
    if valid.any():
        site_d, _, _ = _site_dist(memory, arrays, config)
        visible_site = valid & (site_d <= arrays.r_sight[:, None])
        if visible_site.any():
            active = world.food_timer == 0
            if active.any():
                fx, fy = world.food_x[active], world.food_y[active]
                tree = cKDTree(np.column_stack([fx, fy]),
                               boxsize=config.world_size)
                pts = np.column_stack([
                    memory.mem_x[visible_site] % config.world_size,
                    memory.mem_y[visible_site] % config.world_size])
                d_near, _ = tree.query(pts)
                empty = d_near > config.r_eat
            else:
                empty = np.ones(int(visible_site.sum()), dtype=bool)
            rows, cols = np.nonzero(visible_site)
            memory.mem_seen[rows[empty], cols[empty]] = -1
            valid = memory.mem_seen >= 0

    # Remembering: the nearest seen food refreshes its slot or takes
    # the emptiest, then stalest, one. Deterministic, one site a tick.
    seen = arrays.alive & (food_ids >= 0)
    if seen.any():
        idx = np.flatnonzero(seen)
        fid = food_ids[idx]
        sx = world.food_x[fid]
        sy = world.food_y[fid]
        ddx = _torus_delta(memory.mem_x[idx] - sx[:, None], config.world_size)
        ddy = _torus_delta(memory.mem_y[idx] - sy[:, None], config.world_size)
        slot_d = np.where(memory.mem_seen[idx] >= 0,
                          np.hypot(ddx, ddy), np.inf)
        match = slot_d.min(axis=1) <= config.r_eat
        mcol = slot_d.argmin(axis=1)
        # Refresh matched slots.
        r = idx[match]
        c = mcol[match]
        memory.mem_x[r, c] = sx[match]
        memory.mem_y[r, c] = sy[match]
        memory.mem_seen[r, c] = tick
        # Insert into the emptiest-then-stalest slot elsewhere.
        ins = ~match
        if ins.any():
            r2 = idx[ins]
            c2 = memory.mem_seen[r2].argmin(axis=1)
            memory.mem_x[r2, c2] = sx[ins]
            memory.mem_y[r2, c2] = sy[ins]
            memory.mem_seen[r2, c2] = tick
            # Novelty is a lifetime judgment (phase 19 review fix): an
            # insertion resets wonder's clock only if the agent has
            # never known this cell of the world. Re-learning a place
            # it forgot, or shuttling among more familiar sites than
            # it has slots, is not discovery.
            g = memory.mem_visited.shape[1]
            cell = 2.0 * config.r_eat
            cx = np.minimum((sx[ins] % config.world_size) // cell,
                            g - 1).astype(np.int64)
            cy = np.minimum((sy[ins] % config.world_size) // cell,
                            g - 1).astype(np.int64)
            fresh = ~memory.mem_visited[r2, cx, cy]
            memory.mem_visited[r2, cx, cy] = True
            memory.mem_last_novel[r2[fresh]] = tick
        valid = memory.mem_seen >= 0

    # The composite percept: seen beats remembered beats nothing.
    site_d, site_dx, site_dy = _site_dist(memory, arrays, config)
    freshest = np.where(valid, memory.mem_seen, -1).argmax(axis=1)
    rows = np.arange(arrays.alive.size)
    has_mem = valid[rows, freshest] & arrays.alive
    md = site_d[rows, freshest]
    safe = np.maximum(md, 1e-12)
    mdx = site_dx[rows, freshest] / safe
    mdy = site_dy[rows, freshest] / safe
    seen_now = food_ids >= 0
    out_d = np.where(seen_now, dist_food, np.where(has_mem, md, np.inf))
    out_dx = np.where(seen_now, food_dx, np.where(has_mem, mdx, 0.0))
    out_dy = np.where(seen_now, food_dy, np.where(has_mem, mdy, 0.0))
    # Staleness of the private world in [0, 1]: how long since
    # anything new, over the declared horizon (Amendment 6).
    # wonder_horizon 0 means the drive is off and no percept exists.
    staleness = None
    if config.wonder_horizon > 0:
        # Each agent's own boredom clock (phase 21 third guard);
        # uniform spans are the scalar arithmetic bit for bit.
        staleness = np.clip((tick - memory.mem_last_novel)
                            / arrays.wonder_span, 0.0, 1.0)
    return out_d, out_dx, out_dy, food_ids, staleness


def novel_percept(memory, arrays, config):
    """Per agent: distance and unit direction to the nearest cell of
    the world it has never known; infinite distance and zero direction
    when its world is complete (and for the dead, who quest nowhere).
    Computed here so the action layer never learns why a cell is
    unknown (Amendment 7). Cell centers are the true midpoints of the
    possibly-truncated cells, so a target always lies inside the cell
    it names (phase 21 review: the phantom-center defect at world
    sizes that do not divide by the cell edge)."""
    n = arrays.alive.size
    g = memory.mem_visited.shape[1]
    cell = 2.0 * config.r_eat
    lo = np.arange(g) * cell
    hi = np.minimum(lo + cell, config.world_size)
    centers = (lo + hi) / 2.0
    dxm = _torus_delta(centers[None, :] - arrays.x[:, None], config.world_size)
    dym = _torus_delta(centers[None, :] - arrays.y[:, None], config.world_size)
    d2 = dxm[:, :, None] ** 2 + dym[:, None, :] ** 2
    d2 = np.where(memory.mem_visited, np.inf, d2)
    flat = d2.reshape(n, -1)
    idx = flat.argmin(axis=1)
    best = flat[rows_ := np.arange(n), idx]
    ix, iy = idx // g, idx % g
    nd = np.sqrt(best)
    none = ~np.isfinite(nd) | ~arrays.alive
    safe = np.maximum(np.where(none, 1.0, nd), 1e-12)
    ndx = np.where(none, 0.0, dxm[rows_, ix] / safe)
    ndy = np.where(none, 0.0, dym[rows_, iy] / safe)
    return np.where(none, np.inf, nd), ndx, ndy
