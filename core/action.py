"""Action valuation and selection. Reads drive state, never writes it
(CLAUDE.md chokepoint rule). The E table is specified in
specs/phase-1.md and phase-2.md; entries may be negative; basal_burn is
omitted because it is common to every action and argmax ignores common
terms.
"""

import numpy as np

from .drives import BOND, ENERGY, REST, SAFETY

ACTION_NAMES = ("seek_food", "flee", "rest", "wander", "return_home")
SEEK_FOOD, FLEE, REST_ACT, WANDER, RETURN_HOME = 0, 1, 2, 3, 4


def select_actions(arrays, config, danger_at_agent, dist_food, dist_home):
    """Per agent: value each action as the weight-weighted sum of
    expected urgency reductions, then take the argmax; ties resolve by
    the frozen action order. Myopic: no lookahead, no anticipation of
    the drive dynamics."""
    n = arrays.alive.shape[0]
    # Per agent: tired bodies move slower.
    v_eff = config.speed * (1.0 - arrays.fatigue / 2.0)
    # Per agent: ticks of travel to the nearest active food source
    # (infinite when no food is active anywhere).
    travel = dist_food / v_eff

    ev = np.zeros((n, 4, 5))
    # Food's value is its per-tick gain attenuated by travel time;
    # every moving action pays the movement burn.
    ev[:, ENERGY, SEEK_FOOD] = config.gain_eat / (1.0 + travel) - config.move_burn
    ev[:, ENERGY, FLEE] = -config.move_burn
    ev[:, ENERGY, WANDER] = config.wander_gain - config.move_burn
    ev[:, ENERGY, RETURN_HOME] = -config.move_burn
    # One step down the exponential danger field reduces danger by
    # exactly this closed form.
    ev[:, SAFETY, FLEE] = danger_at_agent * (1.0 - np.exp(-v_eff / config.r_hazard))
    # Movement builds fatigue; resting sheds it.
    ev[:, REST, SEEK_FOOD] = -config.fatigue_rate
    ev[:, REST, FLEE] = -config.fatigue_rate
    ev[:, REST, REST_ACT] = config.rest_rate
    ev[:, REST, WANDER] = -config.fatigue_rate
    ev[:, REST, RETURN_HOME] = -config.fatigue_rate
    # One step toward home reduces separation distress by exactly this
    # closed form (zero for homeless agents, whose bond is zero).
    ev[:, BOND, RETURN_HOME] = arrays.bond * np.exp(-dist_home / config.r_bond) * (
        np.exp(v_eff / config.r_bond) - 1.0
    )

    # Per agent: V(a) = sum over drives of weight * expected reduction.
    values = np.einsum("nd,nda->na", arrays.weights, ev)
    return np.argmax(values, axis=1)
