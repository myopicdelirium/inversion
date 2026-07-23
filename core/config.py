"""Model configuration. Frozen. The config hash goes in every manifest.

Drive time constants are declared here and written nowhere else in the
codebase (CLAUDE.md, Amendment 1). They are read by core/drives.py and
swept by the Phase 4 batch runner; no code path may modify them from
circumstance.
"""

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Config:
    # World
    world_size: float = 100.0
    n_agents: int = 200
    n_food: int = 150
    r_eat: float = 2.0
    gain_eat: float = 0.3
    food_respawn: int = 10
    n_hazard: int = 3
    r_hazard: float = 8.0
    damage_rate: float = 0.02
    regen_rate: float = 0.001
    hazard_drift: float = 0.2
    hazard_onset: int = 0
    # Body
    basal_burn: float = 0.002
    move_burn: float = 0.003
    fatigue_rate: float = 0.004
    rest_rate: float = 0.02
    speed: float = 1.0
    init_energy: float = 0.8
    # Action
    wander_gain: float = 0.004
    # Recording
    record_every: int = 10
    # Nests and attachment (phase 2); bond target type (phase 6):
    # "nest" bonds to the birth nest, "partner" bonds to another agent,
    # who moves and can die.
    bond_target: str = "nest"
    n_nests: int = 5
    r_nest: float = 3.0
    bond_init: float = 0.5
    bond_grow: float = 0.002
    bond_decay: float = 0.0002
    r_bond: float = 25.0
    # Storm (phase 3): experimental apparatus, a hazard aimed at a nest.
    # Disabled by default; enabling it changes nothing before onset.
    storm_nest: int = -1
    storm_onset: int = 2000
    storm_ramp: int = 1
    storm_radius: float = 10.0
    storm_damage: float = 0.05
    # Supplementary apparatus (phase 3 deviations): when true, the ramp
    # is warning only. Danger signal rises as usual but damage starts
    # only once the ramp completes. Distinguishes advance warning from
    # gradual arrival of harm.
    storm_ramp_harmless: bool = False
    # Drive time constants, in ticks. Declared once, never reassigned.
    tau_energy: float = 20.0
    tau_safety: float = 12.0
    tau_rest: float = 30.0
    tau_bond: float = 60.0
    # Population spreads (phase 4, CLAUDE.md Amendment 2). Drawn once
    # per agent at spawn; zero means every agent carries the declared
    # value exactly and no draw is consumed.
    tau_safety_spread: float = 0.0
    tau_bond_spread: float = 0.0
    bond_init_spread: float = 0.0

    def config_hash(self) -> str:
        # Canonical JSON with sorted keys, so the hash is stable across
        # field declaration order and platforms.
        payload = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
