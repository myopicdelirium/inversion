"""Phase 13 addendum: the severed twin. Artifacts:

  results/phase-13-twin.json              V1-V3 on seeds 1-24
  results/phase-13-twin-replication.json  fresh seeds 31-54

The threshold-vigil regime replayed from its own golden's embedded
config; per seed, a kept run and a severed twin, bit-identical to the
cut tick, where the instrument removes the vigil-keepers' bond and
partner pointer and nothing else.

Run:
  uv run python scripts/validate_phase13_twin.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

GOLDEN = json.loads(
    (ROOT / "tests" / "golden" / "phase13_threshold.json").read_text())
CUT = 2050
TICKS = 3500
RIM_BAND = 15.0


def cell(arm, seed):
    cfg = Config(**GOLDEN["config"])
    m = Model(cfg, seed)
    n = cfg.n_agents
    sx, sy = m.world.storm_x, m.world.storm_y
    for _ in range(CUT):
        m.step()

    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    sd = np.hypot(_torus_delta(m.arrays.x - sx, cfg.world_size),
                  _torus_delta(m.arrays.y - sy, cfg.world_size))
    psd = np.hypot(_torus_delta(m.arrays.x[pidx] - sx, cfg.world_size),
                   _torus_delta(m.arrays.y[pidx] - sy, cfg.world_size))
    vigil = (m.arrays.alive & has & m.arrays.alive[pidx]
             & (psd < cfg.storm_radius)
             & (sd >= cfg.storm_radius)
             & (sd < cfg.storm_radius + RIM_BAND))
    if arm == "severed":
        # The instrument's cut (spec addendum): the same agent, with
        # its love removed. Positions, energy, memories, the
        # seen-famine: untouched. No draws consumed.
        m.arrays.bond[vigil] = 0.0
        m.arrays.partner[vigil] = -1

    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()
    for _ in range(TICKS - CUT):
        m.step()
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = m.arrays.alive.copy()

    dead = vigil & ~m.arrays.alive
    starved = dead & (death_energy <= 0.0)
    return {"arm": arm, "seed": seed, "config_hash": cfg.config_hash(),
            "n_vigil": int(vigil.sum()),
            "vigil_dead": int(dead.sum()),
            "vigil_starved": int(starved.sum())}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ("kept", "severed") for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-13.md severed-twin addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    def pool_arm(arm, field):
        sel = [r for r in rows if r["arm"] == arm]
        return sum(r[field] for r in sel), sum(r["n_vigil"] for r in sel)

    n_kept = pool_arm("kept", "n_vigil")[1]
    n_sev = pool_arm("severed", "n_vigil")[1]
    assert n_kept == n_sev, "twin cohorts must be identical by construction"
    v1 = n_kept >= 150
    art["V1"] = {"n_vigil": n_kept, "passed": bool(v1)}
    print(f"V1 power: {n_kept} vigil-keepers pooled, passed {v1}")

    sk, _ = pool_arm("kept", "vigil_starved")
    ss, _ = pool_arm("severed", "vigil_starved")
    rate_k = sk / max(n_kept, 1)
    rate_s = ss / max(n_sev, 1)
    v2 = (rate_k - rate_s) >= 0.05
    art["V2"] = {"starved_kept": rate_k, "starved_severed": rate_s,
                 "excess_points": 100 * (rate_k - rate_s),
                 "passed": bool(v2)}
    print(f"V2 attributable excess: kept {rate_k:.3f} vs severed "
          f"{rate_s:.3f} (excess {100 * (rate_k - rate_s):+.1f} pts, "
          f"bar 5), passed {v2}")

    dk, _ = pool_arm("kept", "vigil_dead")
    ds, _ = pool_arm("severed", "vigil_dead")
    art["V3"] = {"dead_kept": dk / max(n_kept, 1),
                 "dead_severed": ds / max(n_sev, 1)}
    print(f"V3 all-cause: kept {dk / max(n_kept, 1):.3f} vs severed "
          f"{ds / max(n_sev, 1):.3f} (no bar)")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-13-twin.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-13-twin-replication.json")
    else:
        run_stage(range(1, 241), RESULTS / "phase-13-twin.json")
        run_stage(range(241, 481),
                  RESULTS / "phase-13-twin-replication.json")
