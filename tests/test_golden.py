"""Golden-run regression (CLAUDE.md hard rules).

Never update a stored hash to make a test pass: a changed hash means
the dynamics changed, which needs human sign-off and a documented
justification in the commit body.

Phase 2 note, with that justification on record (see the phase 2
commit body and specs/phase-2.md): adding the bond drive extended the
recorded weight/urgency arrays by one column, which supersedes the
phase 1 *combined* hash by shape alone. The preserved quantity is
behavioural: under a no-nest config, every behavioural array must
still match the phase 1 per-array hashes bit for bit. That check is
permanent.
"""

import json
import pathlib
from dataclasses import replace

from core.config import Config
from core.model import array_hashes, golden_hash, run

GOLDEN = pathlib.Path(__file__).parent / "golden"

# The arrays that define behaviour, independent of how many drives the
# model carries.
BEHAVIOURAL = ("x", "y", "energy", "integrity", "fatigue", "alive")


def test_phase1_behaviour_preserved():
    """A world with no nests must behave bit-identically to phase 1."""
    spec = json.loads((GOLDEN / "phase1_default.json").read_text())
    cfg = replace(Config(), n_nests=0)
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    hashes = array_hashes(traj)
    for name in BEHAVIOURAL:
        assert hashes[name] == spec["array_sha256"][name], (
            f"behavioural array '{name}' diverged from the phase 1 golden "
            f"run: the dynamics changed. Report and stop (CLAUDE.md)."
        )


def test_phase3_regime_goldens():
    """Both regimes are findings: the inversion cell and the null cell
    each get a frozen trajectory (CLAUDE.md Amendment 1)."""
    from scripts.validate_phase3 import cell_config

    for filename, cfg in (
        ("phase3_inversion.json", cell_config(1.0, 1, False)),
        ("phase3_null.json", cell_config(1.0, 1600, True)),
    ):
        spec = json.loads((GOLDEN / filename).read_text())
        assert cfg.config_hash() == spec["config_hash"], (
            f"{filename}: cell config no longer matches the golden run"
        )
        traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
        assert golden_hash(traj) == spec["sha256"], (
            f"{filename}: golden trajectory hash changed: the dynamics "
            f"changed. Report and stop (CLAUDE.md)."
        )


def test_phase2_default_golden():
    spec = json.loads((GOLDEN / "phase2_default.json").read_text())
    cfg = Config()
    assert cfg.config_hash() == spec["config_hash"], (
        "default Config no longer matches the phase 2 golden run's config; "
        "dynamics-affecting defaults changed"
    )
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    assert golden_hash(traj) == spec["sha256"], (
        "phase 2 golden trajectory hash changed: the dynamics changed. "
        "Report and stop (CLAUDE.md)."
    )
