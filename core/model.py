"""The model: owns the RNG streams, wires drives, action, and world
together in the tick order fixed by specs/phase-1.md, and records
trajectories for golden hashing.
"""

import hashlib

import numpy as np

from .action import select_actions
from .birth import apply_births
from .memory import (has_believers, hear_places, make_memory, memory_step,
                     novel_percept, promise_percept, promise_step,
                     take_events)
from .memory import reset_agent as reset_memory_agent
from .social import (apply_belief_feedback, eligible_tellers, make_social,
                     social_step)
from .social import reset_agent as reset_social_agent
from .config import Config
from .drives import (
    compute_urgencies,
    init_drive_state,
    init_timescales,
    update_weights,
)
from .rng import spawn_birth_streams, spawn_streams
from .state import allocate
from .world import (
    apply_actions,
    apply_bond,
    apply_damage_and_deaths,
    apply_eating,
    deliver_promise,
    perceive_danger,
    perceive_food,
    perceive_home,
    perceive_partner,
    peril_at,
    spawn_world,
    storm_grip,
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
        # Birth (Amendment 10): dedicated per-slot streams, consumed
        # only on rebirth; the tick-stream discipline is untouched.
        self.birth_rngs = (spawn_birth_streams(seed, config.n_agents)
                           if config.birth_threshold > 0.0 else None)
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
        z_sight = (np.zeros(config.n_agents)
                   if config.r_sight > 0 and config.r_sight_spread > 0 else None)
        z_kappa = (np.zeros(config.n_agents)
                   if config.attention_spread > 0 else None)
        z_horizon = (np.zeros(config.n_agents)
                     if config.prospect_horizon > 0
                     and config.prospect_spread > 0 else None)
        z_span = (np.zeros(config.n_agents)
                  if config.wonder_horizon > 0
                  and config.wonder_spread > 0 else None)
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
            if z_sight is not None:
                z_sight[i] = gen.standard_normal()
            if z_kappa is not None:
                z_kappa[i] = gen.standard_normal()
            if z_horizon is not None:
                z_horizon[i] = gen.standard_normal()
            if z_span is not None:
                z_span[i] = gen.standard_normal()
        init_timescales(self.arrays, config, z_safety, z_bond)
        # Sight (phase 17): personal radii, written once, inf when the
        # axis is off (the shipped omniscience).
        if config.r_sight > 0:
            if config.r_sight <= config.r_eat:
                raise ValueError("r_sight must exceed r_eat when sight "
                                 "is finite, or agents cannot see what "
                                 "they eat")
            if z_sight is not None:
                self.arrays.r_sight[:] = config.r_sight * np.exp(
                    config.r_sight_spread * z_sight)
            else:
                self.arrays.r_sight[:] = config.r_sight
        # The shapes of minds (phase 18): written once, here, never
        # again (tests/test_trait_invariants.py).
        self.arrays.kappa[:] = config.attention_sharpness
        if z_kappa is not None:
            self.arrays.kappa[:] = config.attention_sharpness * np.exp(
                config.attention_spread * z_kappa)
        self.arrays.horizon[:] = float(config.prospect_horizon)
        if z_horizon is not None:
            self.arrays.horizon[:] = np.maximum(1.0, np.round(
                config.prospect_horizon * np.exp(
                    config.prospect_spread * z_horizon)))
        self.arrays.wonder_span[:] = float(config.wonder_horizon)
        if z_span is not None:
            self.arrays.wonder_span[:] = np.maximum(1.0, np.round(
                config.wonder_horizon * np.exp(
                    config.wonder_spread * z_span)))
        if config.bond_target == "leader":
            # Authority as topology (phase 15): agents 0..n_leaders-1
            # are unbonded leaders; every other agent's bond points at
            # leader (i mod n_leaders). One-sided by design; every law
            # downstream is unchanged.
            if not 0 < config.n_leaders < config.n_agents:
                raise ValueError("bond_target 'leader' requires "
                                 "0 < n_leaders < n_agents")
            idx = np.arange(config.n_agents)
            self.arrays.partner[:] = np.where(
                idx < config.n_leaders, -1, idx % config.n_leaders)
            self.arrays.bond[self.arrays.partner < 0] = 0.0
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
        if (config.birth_threshold > 0.0
                and config.birth_threshold < config.birth_cost):
            raise ValueError("birth_threshold must cover birth_cost, or "
                             "parents survive a tick at negative energy")
        self._draw_block = None
        self._draw_cursor = 0
        self.tick = 0
        # The promised place (phase 23): the site is a nest, the
        # storm's placement convention; resolved once at spawn.
        self._prom_site = (0.0, 0.0)
        if config.prophecy_tick >= 0:
            if config.prophecy_nest >= config.n_nests:
                raise ValueError("prophecy_nest requires n_nests > "
                                 f"{config.prophecy_nest}")
            self._prom_site = (
                float(self.world.nest_x[config.prophecy_nest]),
                float(self.world.nest_y[config.prophecy_nest]))
        # The social organ (phase 16): absent at r_social 0, bit-inert.
        self.social = (make_social(config.n_agents, config)
                       if config.r_social > 0 else None)
        # The memory of places (phase 17): absent at r_sight 0, and
        # absent at memory_slots 0 (sighted but memoryless: the V3
        # control arm).
        self.memory = (make_memory(config.n_agents, config)
                       if config.r_sight > 0 and config.memory_slots > 0
                       else None)
        danger, _, _, _ = perceive_danger(
            self.arrays, self.world, config, self._hazards_active(),
            self._storm_intensity(),
        )
        dist_target, _, _ = self._bond_distances()
        peril0 = self._target_peril(self._hazards_active(), self._storm_intensity())
        init_drive_state(self.arrays, config, danger, dist_target, peril0)

    def _hazards_active(self) -> bool:
        return self.tick >= self.config.hazard_onset

    def _storm_intensity(self) -> float:
        """Pure function of the tick: 0 before onset, then a linear
        ramp to 1 over storm_ramp ticks (ramp 1 = a step). With a
        storm season (phase 24 addendum), the same profile recurs
        every storm_season ticks and holds storm_length ticks per
        arrival before dying back to zero: at season 0 the arithmetic
        below reduces to the single storm bit for bit."""
        cfg = self.config
        if cfg.storm_nest < 0 or self.tick < cfg.storm_onset:
            return 0.0
        since = self.tick - cfg.storm_onset
        if cfg.storm_season > 0:
            since = since % cfg.storm_season
            if since >= cfg.storm_length:
                return 0.0
        ramp = max(cfg.storm_ramp, 1)
        return min(1.0, (since + 1) / ramp)

    def _storm_damage_intensity(self, signal: float) -> float:
        """With a harmless ramp, the signal carries no damage until the
        ramp completes; otherwise damage tracks the signal."""
        if self.config.storm_ramp_harmless and signal < 1.0:
            return 0.0
        return signal

    def _bond_distances(self):
        """Distance and direction to whatever this world's bond target
        is: the birth nest, or the living partner."""
        if self.config.bond_target in ("partner", "leader"):
            return perceive_partner(self.arrays, self.config)
        return perceive_home(self.arrays, self.config)

    def _grip_percepts(self, food_ids):
        """Full sight (phase 13): storm-center distances of the current
        food target and bond target, for grip-aware pricing."""
        cfg = self.config
        n = cfg.n_agents

        def center_dist(xs, ys):
            dx = (xs - self.world.storm_x + cfg.world_size / 2.0) % cfg.world_size - cfg.world_size / 2.0
            dy = (ys - self.world.storm_y + cfg.world_size / 2.0) % cfg.world_size - cfg.world_size / 2.0
            return np.hypot(dx, dy)

        ok = food_ids >= 0
        fx = np.where(ok, self.world.food_x[np.maximum(food_ids, 0)], np.inf)
        fy = np.where(ok, self.world.food_y[np.maximum(food_ids, 0)], np.inf)
        food_cd = np.where(ok, center_dist(np.where(ok, fx, 0.0),
                                           np.where(ok, fy, 0.0)), np.inf)
        if cfg.bond_target in ("partner", "leader"):
            p = self.arrays.partner
            has = p >= 0
            pidx = np.where(has, p, 0)
            present = has & self.arrays.alive[pidx]
            tx = np.where(present, self.arrays.x[pidx], 0.0)
            ty = np.where(present, self.arrays.y[pidx], 0.0)
            tgt_cd = np.where(present, center_dist(tx, ty), np.inf)
        else:
            hh = np.isfinite(self.arrays.home_x)
            tgt_cd = np.where(hh, center_dist(np.where(hh, self.arrays.home_x, 0.0),
                                              np.where(hh, self.arrays.home_y, 0.0)), np.inf)
        return {"intensity": self._storm_damage_intensity(self._storm_intensity()),
                "food_center_dist": food_cd, "target_center_dist": tgt_cd}

    def _target_peril(self, active, storm):
        """The danger field at the living bond target's location; zero
        for places and absent targets (care needs a living beloved)."""
        cfg = self.config
        if cfg.bond_target not in ("partner", "leader"):
            return np.zeros(cfg.n_agents)
        p = self.arrays.partner
        has = p >= 0
        pidx = np.where(has, p, 0)
        present = has & self.arrays.alive[pidx]
        px = np.where(present, self.arrays.x[pidx], 0.0)
        py = np.where(present, self.arrays.y[pidx], 0.0)
        level = peril_at(px, py, self.world, cfg, active, storm)
        return np.where(present, level, 0.0)

    def step(self):
        """One tick, in the order fixed by the spec: perceive,
        urgencies, weights, select, move, eat, damage and deaths,
        world updates."""
        cfg = self.config
        # The apparatus keeps its word (Amendment 9): delivery wakes
        # the dormant burst at the foretold hour, true arm only.
        if (cfg.prophecy_tick >= 0 and cfg.prophecy_true
                and self.tick == cfg.prophecy_tick
                and cfg.tell_places and self.social is not None
                and self.memory is not None):
            # Delivery is gated on the organs (review fix): the
            # apparatus keeps its word only in worlds where anyone
            # could have believed it.
            deliver_promise(self.world, cfg, *self._prom_site)
        active = self._hazards_active()
        storm = self._storm_intensity()
        danger, away_dx, away_dy, danger_scale = perceive_danger(
            self.arrays, self.world, cfg, active, storm
        )
        dist_food, food_dx, food_dy, food_ids = perceive_food(self.arrays, self.world, cfg)
        staleness = None
        if self.memory is not None:
            dist_food, food_dx, food_dy, food_ids, staleness = memory_step(
                self.memory, self.arrays, self.world, cfg,
                dist_food, food_dx, food_dy, food_ids, self.tick)
        dist_target, target_dx, target_dy = self._bond_distances()

        grip_info = None
        if cfg.prospect_sees_grip and cfg.prospect_horizon > 0 \
                and cfg.storm_nest >= 0 and cfg.storm_snare > 0.0:
            grip_info = self._grip_percepts(food_ids)
        peril = self._target_peril(active, storm)
        social_danger = None
        if self.social is not None:
            social_danger = social_step(self.social, self.arrays, cfg,
                                        danger, self.tick)
        # The told place (Amendment 8) and the promised place
        # (Amendment 9): one eligibility mask serves both channels,
        # then the settlements this tick produced flow back through
        # the credence law.
        organs = self.social is not None and self.memory is not None
        eligible = None
        if organs and cfg.tell_places:
            eligible = eligible_tellers(self.social, self.arrays, cfg)
            hear_places(self.memory, self.arrays, cfg, eligible, self.tick)
        promise = None
        if organs and cfg.tell_places and cfg.prophecy_tick >= 0:
            promise_step(self.memory, self.arrays, self.world, cfg,
                         eligible, self._prom_site[0],
                         self._prom_site[1], self.tick)
            if has_believers(self.memory):
                pd, pdx, pdy = promise_percept(
                    self.memory, self.arrays, cfg, *self._prom_site)
                promise = (pd, pdx, pdy,
                           max(0, cfg.prophecy_tick - self.tick))
        if self.memory is not None:
            events = take_events(self.memory)
            if events and self.social is not None:
                apply_belief_feedback(self.social, events, cfg)
        compute_urgencies(self.arrays, cfg, danger, dist_target, peril,
                          social_danger=social_danger, staleness=staleness)
        update_weights(self.arrays, cfg)
        novel = None
        if self.memory is not None and cfg.wonder_horizon > 0:
            novel = novel_percept(self.memory, self.arrays, cfg)
        actions = select_actions(
            self.arrays, cfg, danger, dist_food, dist_target,
            food_dir=(food_dx, food_dy), away_dir=(away_dx, away_dy),
            target_dir=(target_dx, target_dy), danger_scale=danger_scale,
            grip_info=grip_info, partner_peril=peril, novel=novel,
            promise=promise,
        )

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
        grip = storm_grip(self.arrays, self.world, cfg,
                          self._storm_damage_intensity(storm))
        apply_actions(
            self.arrays, cfg, actions,
            (food_dx, food_dy), (away_dx, away_dy), (target_dx, target_dy),
            (redraw_p, redraw_angle), grip,
            novel_dir=None if novel is None else (novel[1], novel[2]),
            promise_dir=None if promise is None else (promise[1], promise[2]),
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
        # Birth (Amendment 10): dead slots become cradles; each child
        # gets a fresh mind from the owning organs.
        if self.birth_rngs is not None:
            for _, child in apply_births(self.arrays, cfg, self.birth_rngs):
                if self.memory is not None:
                    reset_memory_agent(self.memory, child, self.tick)
                if self.social is not None:
                    reset_social_agent(self.social, child, cfg)
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
