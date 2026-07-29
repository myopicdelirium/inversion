"""Birth (Amendment 10): slot rebirth with trait inheritance.

THIS IS THE THIRD SANCTIONED TRAIT WRITE SITE (with state.py
allocation and Model init; tests/test_trait_invariants.py enforces
the list). The child inherits its parent's clocks and senses under
lognormal mutation from the slot's dedicated birth stream, and is
born fresh-minded: the reset of memory and ledger state is requested
from the owning organs, never written here.
"""

import numpy as np

from .drives import inherit_drive_state


def apply_births(arrays, config, birth_rngs):
    """Lowest-index parent fills lowest-index cradle, one child per
    parent per tick. Returns the list of (parent, child) slot pairs
    so the model can ask the organs to make the minds fresh."""
    if config.birth_threshold <= 0.0:
        return []
    parents = np.flatnonzero(arrays.alive
                             & (arrays.energy >= config.birth_threshold))
    cradles = np.flatnonzero(~arrays.alive)
    pairs = []
    for p, c in zip(parents, cradles):
        gen = birth_rngs[c]
        # The dead stay dead (Amendment 10): anyone bonded to the
        # cradle's former occupant is widowed for good, not wedded to
        # a stranger's newborn. Grief semantics are preserved: a
        # severed partner is absent, which is what the dead already
        # were.
        arrays.partner[arrays.partner == c] = -1
        arrays.energy[p] -= config.birth_cost
        arrays.alive[c] = True
        arrays.energy[c] = config.birth_cost
        arrays.integrity[c] = 1.0
        arrays.fatigue[c] = 0.0
        arrays.x[c] = arrays.x[p]
        arrays.y[c] = arrays.y[p]
        arrays.heading[c] = arrays.heading[p]
        arrays.home_x[c] = arrays.home_x[p]
        arrays.home_y[c] = arrays.home_y[p]
        arrays.bond[c] = 0.0
        arrays.partner[c] = -1
        # Inheritance under mutation, one draw per trait, from the
        # slot's own stream: replays exactly, touches nothing else.
        # Drive state (tau, weights, urgency) is written by drives.py
        # alone; this file computes and asks (chokepoint preserved).
        m = config.birth_mutation
        child_clocks = arrays.tau[p] * np.exp(
            m * gen.standard_normal(arrays.tau.shape[1]))
        inherit_drive_state(arrays, c, child_clocks)
        arrays.kappa[c] = arrays.kappa[p] * np.exp(m * gen.standard_normal())
        arrays.horizon[c] = max(1.0, np.round(
            arrays.horizon[p] * np.exp(m * gen.standard_normal())))
        arrays.wonder_span[c] = max(1.0, np.round(
            arrays.wonder_span[p] * np.exp(m * gen.standard_normal())))
        sight = arrays.r_sight[p] * np.exp(m * gen.standard_normal())
        if np.isfinite(sight):
            sight = max(sight, config.r_eat + 1e-9)
        arrays.r_sight[c] = sight
        pairs.append((int(p), int(c)))
    return pairs
