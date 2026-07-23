"""Golden-run regression (CLAUDE.md hard rules).

Never update a stored hash to make a test pass: a changed hash means
the dynamics changed, which needs human sign-off and a documented
justification in the commit body.

Configs are stored IN the golden files and replayed exactly
(docs/INCIDENT-2026-07-24-determinism.md): hand reconstruction of a
golden's config is abolished, because approximately remembering a
config was this project's only ever source of phantom nondeterminism.
"""

import json
import pathlib

import pytest

from core.config import Config
from core.model import array_hashes, golden_hash, run

GOLDEN = pathlib.Path(__file__).parent / "golden"
BEHAVIOURAL = ("x", "y", "energy", "integrity", "fatigue", "alive")
FULL = sorted(p.name for p in GOLDEN.glob("*.json") if p.name != "phase1_default.json")


def _load(filename):
    spec = json.loads((GOLDEN / filename).read_text())
    cfg = Config(**spec["config"])
    assert cfg.config_hash() == spec["config_hash"], (
        f"{filename}: stored config no longer hashes to its stored value; "
        f"Config gained or changed fields without a refresh"
    )
    return spec, cfg


def test_phase1_behaviour_preserved():
    """A world with no nests must behave bit-identically to phase 1."""
    spec, cfg = _load("phase1_default.json")
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    hashes = array_hashes(traj)
    for name in BEHAVIOURAL:
        assert hashes[name] == spec["array_sha256"][name], (
            f"behavioural array '{name}' diverged from the phase 1 golden "
            f"run: the dynamics changed. Report and stop (CLAUDE.md)."
        )


@pytest.mark.parametrize("filename", FULL)
def test_golden_trajectory(filename):
    spec, cfg = _load(filename)
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    assert golden_hash(traj) == spec["sha256"], (
        f"{filename}: golden trajectory hash changed: the dynamics "
        f"changed. Report and stop (CLAUDE.md)."
    )
