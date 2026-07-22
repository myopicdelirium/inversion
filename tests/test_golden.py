"""Golden-run regression (CLAUDE.md hard rules).

Reruns the recorded golden configuration and compares trajectory
hashes. Never update the stored hash to make this pass: a changed hash
means the dynamics changed, which needs human sign-off and a documented
justification in the commit body.
"""

import json
import pathlib

from core.config import Config
from core.model import golden_hash, run

GOLDEN = pathlib.Path(__file__).parent / "golden" / "phase1_default.json"


def test_phase1_default_golden():
    spec = json.loads(GOLDEN.read_text())
    cfg = Config()
    assert cfg.config_hash() == spec["config_hash"], (
        "default Config no longer matches the golden run's config; "
        "dynamics-affecting defaults changed"
    )
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    assert golden_hash(traj) == spec["sha256"], (
        "golden trajectory hash changed: the dynamics changed. "
        "Report and stop (CLAUDE.md)."
    )
