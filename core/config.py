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
    # Farsight (phase 11, CLAUDE.md Amendment 4): action values
    # integrate predicted world consequences over this many ticks,
    # under frozen current weights. 0 = the phase 1 closed forms,
    # bit for bit.
    prospect_horizon: int = 0
    # Full sight (phase 13): when true, the farsighted rollout prices
    # the storm's grip at destinations. What an agent knows about the
    # world is itself an axis. False is bit-inert.
    prospect_sees_grip: bool = False
    # Recording
    record_every: int = 10
    # Nests and attachment (phase 2); bond target type (phase 6, 15):
    # "nest" bonds to the birth nest, "partner" bonds to another agent
    # who moves and can die, "leader" points many agents at one:
    # authority as topology (phase 15), no new mechanism.
    bond_target: str = "nest"
    n_leaders: int = 1
    n_nests: int = 5
    r_nest: float = 3.0
    bond_init: float = 0.5
    bond_grow: float = 0.002
    bond_decay: float = 0.0002
    r_bond: float = 25.0
    # The other in the ledger (phase 14, Amendment 5). All default 0,
    # bit-inert: care prices the living bond target's peril into bond
    # urgency; assistance lends a gripped partner speed at close range.
    care: float = 0.0
    r_help: float = 2.0
    help_strength: float = 0.0
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
    # The snare (phase 8): grip strength in [0, 1]. Inside the storm,
    # movement speed is scaled by 1 - snare * damage_intensity: danger
    # that can hold what it is killing. 0 = no grip, bit-inert.
    storm_snare: float = 0.0
    # Drive time constants, in ticks. Declared once, never reassigned.
    tau_energy: float = 20.0
    tau_safety: float = 12.0
    tau_rest: float = 30.0
    tau_bond: float = 60.0
    # Bounded attention (phase 7, CLAUDE.md Amendment 3). At 0 every
    # drive is fully heard and the law is phase 1's bit for bit.
    attention_sharpness: float = 0.0
    # The whisper floor (phase 10, Amendment 3 addendum): the heard
    # ratio is clamped below by this. At 0 the zero-trap regime of
    # phase 9 holds exactly: a never-felt drive stays unhearable.
    attention_floor: float = 0.0
    # Population spreads (phase 4, CLAUDE.md Amendment 2). Drawn once
    # per agent at spawn; zero means every agent carries the declared
    # value exactly and no draw is consumed.
    tau_safety_spread: float = 0.0
    tau_bond_spread: float = 0.0
    bond_init_spread: float = 0.0
    # The social organ (phase 16): honest displays, earned credence,
    # testimony. r_social 0 means the organ is absent: no state, no
    # arithmetic, bit-inert. Displays are the previous tick's safety
    # urgency; credence moves only at window close by the integrated
    # one law; testimony enters u_safety as evidence in drives.py.
    r_social: float = 0.0
    tau_cred: float = 24.0
    # The world you know (phase 17): sight and the memory of places.
    # r_sight 0 means unlimited, the shipped omniscience, bit-inert.
    # When positive, agents see food only within their own radius
    # (personal, via r_sight_spread, lognormal, drawn once at birth),
    # remember up to memory_slots sites they have actually seen, and
    # forget by calendar (memory_horizon) or by disappointment.
    r_sight: float = 0.0
    r_sight_spread: float = 0.0
    # The shapes of minds (phase 18): personal attention sharpness and
    # foresight depth, lognormal around the declared medians, drawn
    # once at birth. Zero spreads are bit-inert.
    attention_spread: float = 0.0
    prospect_spread: float = 0.0
    # Wonder (phase 19, Amendment 6): the fifth drive. wonder_horizon
    # 0 means the drive is off, the corpus's inert-by-default
    # convention; and in any world without sight and memory it is
    # structurally inert regardless, because nothing is ever novel.
    tau_wonder: float = 45.0
    wonder_horizon: int = 0
    wonder_relief: float = 0.01
    # The personal boredom clock (phase 21 third guard): lognormal
    # spread on wonder_horizon, drawn once at birth. 0 is bit-inert.
    wonder_spread: float = 0.0
    memory_slots: int = 8
    memory_horizon: int = 600
    alarm_threshold: float = 0.6
    verify_window: int = 30
    verify_level: float = 0.1
    testimony: float = 0.0
    cred_init: float = 0.5
    cred_floor: float = 0.01
    # The told place (phase 22, Amendment 8): socially settable
    # knowledge. False is bit-inert; the intake also requires the
    # social organ, sight, and memory to exist at all.
    tell_places: bool = False
    tell_threshold: float = 0.5
    # The promised place (phase 23, Amendment 9): the prophecy as
    # apparatus, the storm's informational twin. tick -1 is off,
    # bit-inert; the mechanism also requires telling, social, sight,
    # and memory to exist at all.
    prophecy_tick: int = -1
    prophecy_nest: int = 0
    prophecy_size: float = 0.3
    prophecy_seed_tick: int = 500
    prophecy_seeds: int = 5
    prophecy_true: bool = False
    prophecy_burst: int = 20
    prophecy_grace: int = 50
    # Birth (phase 24, Amendment 10): slot rebirth with trait
    # inheritance. threshold 0.0 is off, bit-inert.
    birth_threshold: float = 0.0
    birth_cost: float = 0.4
    birth_mutation: float = 0.1

    def config_hash(self) -> str:
        # Canonical JSON with sorted keys, so the hash is stable across
        # field declaration order and platforms.
        payload = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
