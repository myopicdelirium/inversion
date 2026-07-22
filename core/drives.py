"""The drive system: instant urgencies, lagged weights, one uniform law.

THIS IS THE ONLY FILE THAT MAY MUTATE DRIVE STATE (weights and
urgencies; time constants are read-only even here). See CLAUDE.md,
Prime Invariant and Amendment 1, and specs/phase-1.md.

Body state enters the system here, through urgencies, as continuous
functions. Weights are written only from urgencies, taus, and
themselves, via the uniform lag. Nothing else, ever.
"""

import numpy as np

DRIVE_NAMES = ("energy", "safety", "rest")
ENERGY, SAFETY, REST = 0, 1, 2


def compute_urgencies(arrays, danger_at_agent):
    """Per agent: hunger urgency is how empty the stomach is, safety
    urgency is the local danger level, rest urgency is the fatigue
    level. Instant, continuous, no branches."""
    arrays.urgency[:, ENERGY] = 1.0 - arrays.energy
    arrays.urgency[:, SAFETY] = danger_at_agent
    arrays.urgency[:, REST] = arrays.fatigue


def update_weights(arrays, config, dt=1.0):
    """Per agent, per drive: the weight moves a fraction dt/tau of the
    way from where it is toward the current urgency. This one line is
    the entire inertia mechanism; every drive obeys it and nothing
    bypasses it."""
    live = arrays.alive
    arrays.weights[live] += (
        dt / np.array([config.tau_energy, config.tau_safety, config.tau_rest])
    ) * (arrays.urgency[live] - arrays.weights[live])


def init_drive_state(arrays, danger_at_agent):
    """Per agent: at spawn, weights start exactly at the current
    urgencies; there is no initial gap to relax."""
    compute_urgencies(arrays, danger_at_agent)
    arrays.weights[:] = arrays.urgency
