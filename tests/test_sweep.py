"""Sweep runner determinism (CLAUDE.md: parallelism across runs only;
specs/phase-4.md criterion 4). The same sweep produces byte-identical
output with 1 worker and with several.
"""

from core.sweep import run_sweep, sweep_digest

BASE = {
    "n_agents": 40,
    "n_hazard": 0,
    "storm_nest": 0,
    "storm_onset": 300,
    "storm_ramp": 1,
    "bond_init": 1.0,
    "tau_bond_spread": 0.5,
}
AXES = [("bond_init", [0.0, 1.0]), ("storm_ramp", [1, 100])]
SEEDS = [1, 2]


def test_sweep_parallel_matches_serial():
    serial = run_sweep(BASE, AXES, SEEDS, ticks=600, onset=300, window=300, workers=1)
    parallel = run_sweep(BASE, AXES, SEEDS, ticks=600, onset=300, window=300, workers=4)
    assert sweep_digest(serial) == sweep_digest(parallel)
    # And the sweep is reproducible outright.
    again = run_sweep(BASE, AXES, SEEDS, ticks=600, onset=300, window=300, workers=2)
    assert sweep_digest(serial) == sweep_digest(again)
