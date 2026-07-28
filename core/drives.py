"""The drive system: instant urgencies, lagged weights, one uniform law.

THIS IS THE ONLY FILE THAT MAY MUTATE DRIVE STATE (weights and
urgencies; time constants are read-only even here). See CLAUDE.md,
Prime Invariant and Amendment 1, and specs/phase-1.md, phase-2.md.

Body state enters the system here, through urgencies, as continuous
functions. Weights are written only from urgencies, taus, and
themselves, via the uniform lag. Nothing else, ever.
"""

import numpy as np

DRIVE_NAMES = ("energy", "safety", "rest", "bond", "wonder")
ENERGY, SAFETY, REST, BOND, WONDER = 0, 1, 2, 3, 4


def compute_urgencies(arrays, config, danger_at_agent, dist_home,
                      target_peril=None, social_danger=None,
                      staleness=None):
    """Per agent: hunger urgency is how empty the stomach is, safety
    urgency is the local danger level, rest urgency is the fatigue
    level, bond urgency is separation distress plus care for the
    living target's peril (Amendment 5): attachment level times how
    far from home and how endangered they are. Instant, continuous,
    no branches; an absent target has no location and so no peril.
    Testimony (phase 16) enters safety as evidence: danger heard from
    a credible neighbor competes with danger seen, and the loudest
    wins. The percept is computed in social.py; only this file writes
    the urgency."""
    arrays.urgency[:, ENERGY] = 1.0 - arrays.energy
    if social_danger is None:
        arrays.urgency[:, SAFETY] = danger_at_agent
    else:
        arrays.urgency[:, SAFETY] = np.maximum(
            danger_at_agent, config.testimony * social_danger
        )
    arrays.urgency[:, REST] = arrays.fatigue
    # Wonder (Amendment 6): the staleness of the private world, a
    # percept from the memory of places. None means no such world
    # exists and the drive is structurally inert.
    arrays.urgency[:, WONDER] = 0.0 if staleness is None else staleness
    separation = 1.0 - np.exp(-dist_home / config.r_bond)
    if target_peril is None:
        arrays.urgency[:, BOND] = arrays.bond * separation
    else:
        arrays.urgency[:, BOND] = arrays.bond * np.clip(
            separation + config.care * target_peril, 0.0, 1.0
        )


def update_weights(arrays, config, dt=1.0):
    """Per agent, per drive: the weight moves a fraction dt/tau of the
    way from where it is toward the HEARD urgency, on that agent's own
    clock. Attention is finite (Amendment 3): each drive is heard in
    proportion to its weight relative to the loudest weight, raised to
    the declared sharpness. At sharpness 0 the factor is exactly one
    and this is phase 1's law bit for bit. The law names no drive:
    whatever dominates, dominates uniformly."""
    live = arrays.alive
    current = arrays.weights[live]
    loudest = np.maximum(current.max(axis=1, keepdims=True), 1e-12)
    # The whisper floor (Amendment 3 addendum): no drive's hearing
    # falls below the declared floor. At floor 0 this clamp is inert
    # and the zero-trap regime holds exactly.
    ratio = np.maximum(current / loudest, config.attention_floor)
    heard = arrays.urgency[live] * ratio ** arrays.kappa[live, None]
    arrays.weights[live] = current + (dt / arrays.tau[live]) * (heard - current)


def init_timescales(arrays, config, z_safety=None, z_bond=None):
    """Per agent: time constants are drawn once at birth from the
    declared population distributions and never written again
    (CLAUDE.md Amendment 2). With zero spread every agent carries the
    declared value exactly; the declared value is the population
    median under spread."""
    arrays.tau[:, ENERGY] = config.tau_energy
    arrays.tau[:, SAFETY] = config.tau_safety
    arrays.tau[:, REST] = config.tau_rest
    arrays.tau[:, BOND] = config.tau_bond
    arrays.tau[:, WONDER] = config.tau_wonder
    if z_safety is not None:
        arrays.tau[:, SAFETY] = config.tau_safety * np.exp(
            config.tau_safety_spread * z_safety
        )
    if z_bond is not None:
        arrays.tau[:, BOND] = config.tau_bond * np.exp(
            config.tau_bond_spread * z_bond
        )


def init_drive_state(arrays, config, danger_at_agent, dist_home,
                     target_peril=None):
    """Per agent: at spawn, weights start exactly at the current
    urgencies; there is no initial gap to relax."""
    compute_urgencies(arrays, config, danger_at_agent, dist_home, target_peril)
    arrays.weights[:] = arrays.urgency
