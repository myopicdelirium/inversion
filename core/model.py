"""The model: owns the RNG streams, wires drives, action, and world
together in the tick order fixed by specs/phase-1.md, and records
trajectories for golden hashing.
"""

import hashlib

import numpy as np

from .action import select_actions
from .config import Config
from .drives import compute_urgencies, init_drive_state, update_weights
from .rng import spawn_streams
from .state import allocate
from .world import (
    apply_actions,
    apply_damage_and_deaths,
    apply_eating,
    perceive_danger,
    perceive_food,
    spawn_world,
    update_world,
)

# Arrays recorded for the golden trajectory, in hashing order.
# urgency is recorded so the lag validation can check the uniform law
# transition by transition against what the model actually computed.
RECORDED = ("x", "y", "energy", "integrity", "fatigue", "weights", "urgency")


class Model:
    def __init__(self, config: Config, seed: int):
        self.config = config
        self.seed = seed
        self.world_rng, self.agent_rngs = spawn_streams(seed, config.n_agents)
        self.arrays = allocate(config.n_agents, config.init_energy)
        # Per agent: spawn position and initial heading come from the
        # agent's own stream, so adding agent n+1 never shifts another
        # agent's spawn.
        for i, gen in enumerate(self.agent_rngs):
            self.arrays.x[i] = gen.random() * config.world_size
            self.arrays.y[i] = gen.random() * config.world_size
            self.arrays.heading[i] = gen.random() * 2.0 * np.pi
        self.world = spawn_world(config, self.world_rng)
        self.tick = 0
        danger, _, _ = perceive_danger(
            self.arrays, self.world, config, self._hazards_active()
        )
        init_drive_state(self.arrays, danger)

    def _hazards_active(self) -> bool:
        return self.tick >= self.config.hazard_onset

    def step(self):
        """One tick, in the order fixed by the spec: perceive,
        urgencies, weights, select, move, eat, damage and deaths,
        world updates."""
        cfg = self.config
        active = self._hazards_active()
        danger, away_dx, away_dy = perceive_danger(self.arrays, self.world, cfg, active)
        dist_food, food_dx, food_dy, _ = perceive_food(self.arrays, self.world, cfg)

        compute_urgencies(self.arrays, danger)
        update_weights(self.arrays, cfg)
        actions = select_actions(self.arrays, cfg, danger, dist_food)

        # Per agent: two draws per tick from the agent's own stream,
        # consumed by every agent every tick regardless of action, so
        # stream consumption never depends on behaviour.
        redraw_p = np.array([gen.random() for gen in self.agent_rngs])
        redraw_angle = np.array([gen.random() for gen in self.agent_rngs])
        apply_actions(
            self.arrays, cfg, actions,
            (food_dx, food_dy), (away_dx, away_dy), (redraw_p, redraw_angle),
        )
        # Eating uses post-move positions.
        dist_after, _, _, food_id_after = perceive_food(self.arrays, self.world, cfg)
        apply_eating(self.arrays, self.world, cfg, dist_after, food_id_after)
        apply_damage_and_deaths(self.arrays, self.world, cfg, active)
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
