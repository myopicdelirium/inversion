"""Structure-of-arrays agent state. Allocation only: drive state is
mutated exclusively in core/drives.py (CLAUDE.md chokepoint rule).
"""

from dataclasses import dataclass

import numpy as np

from .drives import DRIVE_NAMES


@dataclass
class AgentArrays:
    alive: np.ndarray      # (n,) bool
    x: np.ndarray          # (n,) position
    y: np.ndarray          # (n,)
    energy: np.ndarray     # (n,) in [0, 1]; death at 0
    integrity: np.ndarray  # (n,) in [0, 1]; death at 0
    fatigue: np.ndarray    # (n,) in [0, 1]; slows movement, not lethal
    heading: np.ndarray    # (n,) radians, persistent wander direction
    bond: np.ndarray       # (n,) attachment level in [0, 1]
    home_x: np.ndarray     # (n,) home nest position; inf when homeless
    home_y: np.ndarray
    weights: np.ndarray    # (n, n_drives) lagged drive weights
    urgency: np.ndarray    # (n, n_drives) instant urgencies


def allocate(n: int, init_energy: float) -> AgentArrays:
    # Every agent starts alive, fed to init_energy, intact, rested, and
    # homeless with zero attachment. Positions, headings, homes, bond,
    # and initial drive state are set by the model.
    d = len(DRIVE_NAMES)
    return AgentArrays(
        alive=np.ones(n, dtype=bool),
        x=np.zeros(n),
        y=np.zeros(n),
        energy=np.full(n, init_energy),
        integrity=np.ones(n),
        fatigue=np.zeros(n),
        heading=np.zeros(n),
        bond=np.zeros(n),
        home_x=np.full(n, np.inf),
        home_y=np.full(n, np.inf),
        weights=np.zeros((n, d)),
        urgency=np.zeros((n, d)),
    )
