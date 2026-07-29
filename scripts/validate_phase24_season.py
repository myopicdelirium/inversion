"""Phase 24 addendum: the storm season. Artifacts:

  results/phase-24-season.json              S2-S3 on seeds 1-24
  results/phase-24-season-replication.json  fresh seeds 31-54

Recurring sudden storms over a birthing population with heritable
fear clocks: the arena G4's refutation prescribed, at G4's unmoved
bar.

Run:
  uv run python scripts/validate_phase24_season.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"n_food": 90, "tau_safety_spread": 0.5, "n_hazard": 0,
         "birth_threshold": 0.9, "birth_cost": 0.4, "bond_init": 1.0,
         "storm_nest": 0, "storm_onset": 800, "storm_ramp": 1,
         "storm_season": 800, "storm_length": 400,
         "storm_damage": 0.05}
TICKS = 8000


def cell(seed):
    cfg = replace(Config(), **ARENA)
    m = Model(cfg, seed)
    tau0 = float(m.arrays.tau[m.arrays.alive, 1].mean())
    dead_tau, surv_tau = [], []
    prev_alive = m.arrays.alive.copy()
    prev_tau = m.arrays.tau[:, 1].copy()
    for _ in range(TICKS):
        m.step()
        if m._storm_intensity() > 0.0:
            # A death is an alive-flip OR a trait change on a
            # previously living slot: same-tick rebirth hides the
            # flip (the phase's twice-earned lesson).
            died = (prev_alive & ~m.arrays.alive) | (
                prev_alive & (m.arrays.tau[:, 1] != prev_tau))
            if died.any():
                dead_tau.extend(float(v) for v in prev_tau[died])
                alive_now = m.arrays.alive
                if alive_now.any():
                    surv_tau.append(
                        float(m.arrays.tau[alive_now, 1].mean()))
        prev_alive = m.arrays.alive.copy()
        prev_tau = m.arrays.tau[:, 1].copy()
    alive = m.arrays.alive
    tau_end = float(m.arrays.tau[alive, 1].mean()) if alive.any() else None
    return {"seed": seed, "config_hash": cfg.config_hash(),
            "tau_start": tau0, "tau_end": tau_end,
            "storm_dead_tau": dead_tau,
            "storm_survivor_means": surv_tau,
            "final_alive": int(alive.sum())}


def run_stage(seeds, out_path):
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell, seeds))
    art = {"spec": "specs/phase-24.md storm-season addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    dead = np.concatenate([np.array(r["storm_dead_tau"]) for r in rows])
    surv = np.concatenate([np.array(r["storm_survivor_means"])
                           for r in rows])
    d_mean = float(dead.mean()) if dead.size else None
    s_mean = float(surv.mean()) if surv.size else None
    s2 = (d_mean is not None and s_mean is not None
          and d_mean >= 1.10 * s_mean)
    art["S2"] = {"storm_dead_mean_tau": d_mean, "n_dead": int(dead.size),
                 "survivor_mean_tau": s_mean,
                 "ratio": (d_mean / s_mean) if s_mean else None,
                 "passed": bool(s2)}
    print(f"S2 the season kills selectively: storm dead mean tau "
          f"{d_mean} (n {dead.size}) vs survivors {s_mean} (ratio "
          f"{art['S2']['ratio'] and round(art['S2']['ratio'], 2)}, bar "
          f"1.10): passed {s2}")

    t0 = float(np.mean([r["tau_start"] for r in rows]))
    ends = [r["tau_end"] for r in rows if r["tau_end"] is not None]
    t1 = float(np.mean(ends)) if ends else None
    s3 = t1 is not None and t1 <= 0.9 * t0
    art["S3"] = {"tau_start": t0, "tau_end": t1,
                 "change_pct": (100 * (t1 - t0) / t0) if t1 else None,
                 "final_alive": sum(r["final_alive"] for r in rows),
                 "passed": bool(s3)}
    print(f"S3 the breeding claim: mean tau_safety {t0:.2f} -> "
          f"{t1 and round(t1, 2)} ({art['S3']['change_pct'] and round(art['S3']['change_pct'], 1)} pct, bar -10; "
          f"final alive {art['S3']['final_alive']}): passed {s3}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-24-season.json")
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-24-season-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-24-season.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-24-season-replication.json")
