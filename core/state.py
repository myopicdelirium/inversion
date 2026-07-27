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
    partner: np.ndarray    # (n,) index of the bonded agent; -1 = none
    weights: np.ndarray    # (n, n_drives) lagged drive weights
    urgency: np.ndarray    # (n, n_drives) instant urgencies
    tau: np.ndarray        # (n, n_drives) per-agent time constants,
                           # written once at spawn (CLAUDE.md Amendment 2)
    r_sight: np.ndarray    # (n,) personal sight radius, written once at
                           # spawn (phase 17); inf = unlimited
    kappa: np.ndarray      # (n,) personal attention sharpness, written
                           # once at spawn (phase 18)
    horizon: np.ndarray    # (n,) personal foresight depth, written once
                           # at spawn (phase 18)


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
        partner=np.full(n, -1, dtype=np.int64),
        weights=np.zeros((n, d)),
        urgency=np.zeros((n, d)),
        tau=np.zeros((n, d)),
        r_sight=np.full(n, np.inf),
        kappa=np.zeros(n),
        horizon=np.zeros(n),
    )
