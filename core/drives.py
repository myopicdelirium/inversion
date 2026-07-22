"""The drive system: instant urgencies, lagged weights, one uniform law.

THIS IS THE ONLY FILE THAT MAY MUTATE DRIVE STATE (weights and
urgencies; time constants are read-only even here). See CLAUDE.md,
Prime Invariant and Amendment 1, and specs/phase-1.md, phase-2.md.

Body state enters the system here, through urgencies, as continuous
functions. Weights are written only from urgencies, taus, and
themselves, via the uniform lag. Nothing else, ever.
"""

import numpy as np

DRIVE_NAMES = ("energy", "safety", "rest", "bond")
ENERGY, SAFETY, REST, BOND = 0, 1, 2, 3


def compute_urgencies(arrays, config, danger_at_agent, dist_home):
    """Per agent: hunger urgency is how empty the stomach is, safety
    urgency is the local danger level, rest urgency is the fatigue
    level, bond urgency is separation distress: attachment level times
    how far from home. Instant, continuous, no branches."""
    arrays.urgency[:, ENERGY] = 1.0 - arrays.energy
    arrays.urgency[:, SAFETY] = danger_at_agent
    arrays.urgency[:, REST] = arrays.fatigue
    arrays.urgency[:, BOND] = arrays.bond * (
        1.0 - np.exp(-dist_home / config.r_bond)
    )


def update_weights(arrays, config, dt=1.0):
    """Per agent, per drive: the weight moves a fraction dt/tau of the
    way from where it is toward the current urgency, on that agent's
    own clock. This one line is the entire inertia mechanism; every
    drive obeys it and nothing bypasses it."""
    live = arrays.alive
    arrays.weights[live] += (
        dt / arrays.tau[live]
    ) * (arrays.urgency[live] - arrays.weights[live])


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
    if z_safety is not None:
        arrays.tau[:, SAFETY] = config.tau_safety * np.exp(
            config.tau_safety_spread * z_safety
        )
    if z_bond is not None:
        arrays.tau[:, BOND] = config.tau_bond * np.exp(
            config.tau_bond_spread * z_bond
        )


def init_drive_state(arrays, config, danger_at_agent, dist_home):
    """Per agent: at spawn, weights start exactly at the current
    urgencies; there is no initial gap to relax."""
    compute_urgencies(arrays, config, danger_at_agent, dist_home)
    arrays.weights[:] = arrays.urgency
