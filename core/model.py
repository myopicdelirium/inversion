"""The model: owns the RNG streams, wires drives, action, and world
together in the tick order fixed by specs/phase-1.md, and records
trajectories for golden hashing.
"""

import hashlib

import numpy as np

from .action import select_actions
from .config import Config
from .drives import (
    compute_urgencies,
    init_drive_state,
    init_timescales,
    update_weights,
)
from .rng import spawn_streams
from .state import allocate
from .world import (
    apply_actions,
    apply_bond,
    apply_damage_and_deaths,
    apply_eating,
    perceive_danger,
    perceive_food,
    perceive_home,
    perceive_partner,
    spawn_world,
    update_world,
)

# Arrays recorded for the golden trajectory, in hashing order.
# urgency is recorded so the lag validation can check the uniform law
# transition by transition against what the model actually computed;
# bond likewise for the accumulation identity.
RECORDED = ("x", "y", "energy", "integrity", "fatigue", "weights",
            "urgency", "bond")

# Per-agent draws are consumed from blocks of this many ticks.
# Generator.random(k) yields the identical stream values as k singles,
# so the block size cannot affect any trajectory (goldens verify).
_DRAW_BLOCK = 256


class Model:
    def __init__(self, config: Config, seed: int):
        self.config = config
        self.seed = seed
        self.world_rng, self.agent_rngs = spawn_streams(seed, config.n_agents)
        self.arrays = allocate(config.n_agents, config.init_energy)
        self.world = spawn_world(config, self.world_rng)
        # Per agent: spawn position and initial heading come from the
        # agent's own stream, so adding agent n+1 never shifts another
        # agent's spawn. With nests, agents are assigned a home
        # round-robin by index and born at it plus a small jitter; the
        # two position draws are consumed either way, so a nest-free
        # world spawns exactly as phase 1 did.
        # Per agent, in fixed draw order: spawn position, heading, then
        # the heterogeneity draws, each consumed only when its spread
        # knob is nonzero, so draw counts depend on config alone and
        # all-zero spreads reproduce prior phases bit for bit.
        z_safety = np.zeros(config.n_agents) if config.tau_safety_spread > 0 else None
        z_bond = np.zeros(config.n_agents) if config.tau_bond_spread > 0 else None
        for i, gen in enumerate(self.agent_rngs):
            if config.n_nests > 0:
                nest = i % config.n_nests
                self.arrays.home_x[i] = self.world.nest_x[nest]
                self.arrays.home_y[i] = self.world.nest_y[nest]
                angle = gen.random() * 2.0 * np.pi
                radius = gen.random() * config.r_nest
                self.arrays.x[i] = (self.arrays.home_x[i] + radius * np.cos(angle)) % config.world_size
                self.arrays.y[i] = (self.arrays.home_y[i] + radius * np.sin(angle)) % config.world_size
                self.arrays.bond[i] = config.bond_init
            else:
                self.arrays.x[i] = gen.random() * config.world_size
                self.arrays.y[i] = gen.random() * config.world_size
            self.arrays.heading[i] = gen.random() * 2.0 * np.pi
            if z_safety is not None:
                z_safety[i] = gen.standard_normal()
            if z_bond is not None:
                z_bond[i] = gen.standard_normal()
            if config.bond_init_spread > 0 and config.n_nests > 0:
                jitter = config.bond_init_spread * (2.0 * gen.random() - 1.0)
                self.arrays.bond[i] = min(max(config.bond_init + jitter, 0.0), 1.0)
        init_timescales(self.arrays, config, z_safety, z_bond)
        if config.bond_target == "partner":
            if config.n_nests <= 0:
                raise ValueError("bond_target 'partner' requires n_nests > 0")
            # Per agent: pair with the same-nest neighbour one block
            # away; partners share a birth nest and spawn adjacent.
            # Deterministic, no draws consumed. One-sided pairs at the
            # tail are broken; unpaired agents carry no bond, exactly
            # like homeless agents in phase 2.
            idx = np.arange(config.n_agents)
            block = idx // config.n_nests
            cand = np.where(block % 2 == 0, idx + config.n_nests,
                            idx - config.n_nests)
            valid = (cand >= 0) & (cand < config.n_agents)
            proposed = np.where(valid, cand, -1)
            mutual = (proposed >= 0) & (proposed[np.where(proposed >= 0, proposed, 0)] == idx)
            self.arrays.partner[:] = np.where(mutual, proposed, -1)
            self.arrays.bond[self.arrays.partner < 0] = 0.0
        self._draw_block = None
        self._draw_cursor = 0
        self.tick = 0
        danger, _, _ = perceive_danger(
            self.arrays, self.world, config, self._hazards_active(),
            self._storm_intensity(),
        )
        dist_target, _, _ = self._bond_distances()
        init_drive_state(self.arrays, config, danger, dist_target)

    def _hazards_active(self) -> bool:
        return self.tick >= self.config.hazard_onset

    def _storm_intensity(self) -> float:
        """Pure function of the tick: 0 before onset, then a linear
        ramp to 1 over storm_ramp ticks (ramp 1 = a step)."""
        cfg = self.config
        if cfg.storm_nest < 0 or self.tick < cfg.storm_onset:
            return 0.0
        ramp = max(cfg.storm_ramp, 1)
        return min(1.0, (self.tick - cfg.storm_onset + 1) / ramp)

    def _storm_damage_intensity(self, signal: float) -> float:
        """With a harmless ramp, the signal carries no damage until the
        ramp completes; otherwise damage tracks the signal."""
        if self.config.storm_ramp_harmless and signal < 1.0:
            return 0.0
        return signal

    def _bond_distances(self):
        """Distance and direction to whatever this world's bond target
        is: the birth nest, or the living partner."""
        if self.config.bond_target == "partner":
            return perceive_partner(self.arrays, self.config)
        return perceive_home(self.arrays, self.config)

    def step(self):
        """One tick, in the order fixed by the spec: perceive,
        urgencies, weights, select, move, eat, damage and deaths,
        world updates."""
        cfg = self.config
        active = self._hazards_active()
        storm = self._storm_intensity()
        danger, away_dx, away_dy = perceive_danger(
            self.arrays, self.world, cfg, active, storm
        )
        dist_food, food_dx, food_dy, _ = perceive_food(self.arrays, self.world, cfg)
        dist_target, target_dx, target_dy = self._bond_distances()

        compute_urgencies(self.arrays, cfg, danger, dist_target)
        update_weights(self.arrays, cfg)
        actions = select_actions(self.arrays, cfg, danger, dist_food, dist_target)

        # Per agent: two draws per tick from the agent's own stream,
        # consumed by every agent every tick regardless of action, so
        # stream consumption never depends on behaviour. Drawn in
        # blocks so population scale does not pay a Python loop per
        # tick; per-agent stream order is unchanged.
        if self._draw_block is None or self._draw_cursor >= 2 * _DRAW_BLOCK:
            self._draw_block = np.stack(
                [gen.random(2 * _DRAW_BLOCK) for gen in self.agent_rngs]
            )
            self._draw_cursor = 0
        redraw_p = self._draw_block[:, self._draw_cursor]
        redraw_angle = self._draw_block[:, self._draw_cursor + 1]
        self._draw_cursor += 2
        apply_actions(
            self.arrays, cfg, actions,
            (food_dx, food_dy), (away_dx, away_dy), (target_dx, target_dy),
            (redraw_p, redraw_angle),
        )
        # Eating and bond accumulation use post-move positions.
        dist_after, _, _, food_id_after = perceive_food(self.arrays, self.world, cfg)
        apply_eating(self.arrays, self.world, cfg, dist_after, food_id_after)
        dist_target_after, _, _ = self._bond_distances()
        apply_bond(self.arrays, cfg, dist_target_after)
        apply_damage_and_deaths(
            self.arrays, self.world, cfg, active,
            self._storm_damage_intensity(storm),
        )
        update_world(self.world, cfg, self.world_rng)
        self.tick += 1
        return actions


def run(config: Config, seed: int, ticks: int) -> dict:
    """Run and return the recorded trajectory: the initial state plus
    every record_every-th tick thereafter, as stacked arrays."""
    model = Model(config, seed)
    frames = {name: [] for name in RECORDED}
    frames["alive"] = []
    frames["tick"] = []

    def record():
        for name in RECORDED:
            frames[name].append(getattr(model.arrays, name).copy())
        frames["alive"].append(model.arrays.alive.copy())
        frames["tick"].append(model.tick)

    record()
    for _ in range(ticks):
        model.step()
        if model.tick % config.record_every == 0:
            record()
    return {name: np.stack(values) for name, values in frames.items()}


def array_hashes(trajectory: dict) -> dict:
    """Per-array sha256 (same rounding as golden_hash). The behavioural
    arrays (x, y, energy, integrity, fatigue, alive) let a later phase
    prove bit-identical behaviour even when drive arrays change shape."""
    out = {}
    for name in RECORDED:
        out[name] = hashlib.sha256(
            np.round(trajectory[name], 8).astype(np.float64).tobytes()
        ).hexdigest()
    out["alive"] = hashlib.sha256(
        trajectory["alive"].astype(np.uint8).tobytes()
    ).hexdigest()
    return out


def golden_hash(trajectory: dict) -> str:
    """sha256 over the recorded arrays rounded to 8 decimals (so the
    hash survives BLAS and platform noise), in the fixed order, with
    alive appended as uint8."""
    digest = hashlib.sha256()
    for name in RECORDED:
        digest.update(np.round(trajectory[name], 8).astype(np.float64).tobytes())
    digest.update(trajectory["alive"].astype(np.uint8).tobytes())
    return digest.hexdigest()
