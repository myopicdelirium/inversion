"""Phase 18 addendum: mapping the step. Artifacts:

  results/phase-18-step.json              K1-K3 on seeds 1-24
  results/phase-18-step-replication.json  fresh seeds 31-54

The T2 grief arena with the population astride the suspected
threshold: attention_sharpness median 1.0, attention_spread 0.8.
Protocol only: no mechanism, no golden.

Run:
  uv run python scripts/validate_phase18_step.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "bond_init": 0.8, "attention_sharpness": 1.0,
         "attention_spread": 0.8}
BINS = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, np.inf)
TICKS = 3500


def cell(seed):
    cfg = replace(Config(), **ARENA)
    m = Model(cfg, seed)
    kappa = m.arrays.kappa.copy()
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    n = cfg.n_agents

    loss_tick = np.full(n, -1, dtype=np.int64)
    death_tick = np.full(n, -1, dtype=np.int64)
    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()
    for _ in range(TICKS):
        m.step()
        alive = m.arrays.alive
        died_now = prev_alive & ~alive
        if died_now.any():
            death_tick[died_now] = m.tick
            death_energy[died_now] = m.arrays.energy[died_now]
            target_died = has & died_now[pidx] & alive & (loss_tick < 0)
            loss_tick[target_died] = m.tick
        prev_alive = alive.copy()

    bereaved = loss_tick >= 0
    starved = bereaved & (death_tick >= loss_tick) & (death_energy <= 0.0)
    return {"seed": seed, "config_hash": cfg.config_hash(),
            "bereaved_kappa": [round(float(k), 4) for k in kappa[bereaved]],
            "bereaved_starved": [bool(s) for s in starved[bereaved]]}


def run_stage(seeds, out_path):
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell, seeds))
    kap = np.concatenate([np.array(r["bereaved_kappa"]) for r in rows])
    stv = np.concatenate([np.array(r["bereaved_starved"], dtype=bool)
                          for r in rows])
    art = {"spec": "specs/phase-18.md step addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows,
           "n_bereaved": int(kap.size)}

    profile = []
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        mask = (kap >= lo) & (kap < hi)
        profile.append({"bin": f"[{lo}, {hi})", "n": int(mask.sum()),
                        "rate": float(stv[mask].mean()) if mask.any() else None})
    art["K2_profile"] = profile

    below = (kap < 1.0)
    mid = (kap >= 1.0) & (kap < 1.5)
    above = (kap >= 1.5)
    r_below = float(stv[below].mean()) if below.any() else None
    r_mid = float(stv[mid].mean()) if mid.any() else None
    r_above = float(stv[above].mean()) if above.any() else None
    k1 = (None not in (r_below, r_mid, r_above)
          and r_above >= 5.0 * max(r_below, 1e-9)
          and r_below <= r_mid <= r_above)
    art["K1"] = {"rate_below_1": r_below, "n_below": int(below.sum()),
                 "rate_1_to_1p5": r_mid, "n_mid": int(mid.sum()),
                 "rate_above_1p5": r_above, "n_above": int(above.sum()),
                 "ratio": (r_above / max(r_below, 1e-9)
                           if None not in (r_above, r_below) else None),
                 "passed": bool(k1)}
    print(f"K1 step: below-1 {r_below} (n {int(below.sum())}), "
          f"[1,1.5) {r_mid} (n {int(mid.sum())}), above-1.5 {r_above} "
          f"(n {int(above.sum())}), ratio "
          f"{art['K1']['ratio'] and round(art['K1']['ratio'], 1)}, "
          f"passed {k1}")

    top = kap >= 2.0
    n_top = int(top.sum())
    rho = (float(spearmanr(kap[top], stv[top]).statistic)
           if n_top > 1 else None)
    k3_valid = n_top >= 300
    k3 = k3_valid and rho is not None and abs(rho) <= 0.1
    art["K3"] = {"n_top": n_top, "rho_above_2": rho,
                 "valid": bool(k3_valid), "passed": bool(k3)}
    print(f"K3 saturation: n {n_top}, rho {rho}, valid {k3_valid}, "
          f"passed {k3}")
    print("K2 profile:", [(b["bin"], b["n"],
                           b["rate"] and round(b["rate"], 3))
                          for b in profile])
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-18-step.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-18-step-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-18-step.json")
        run_stage(range(31, 55), RESULTS / "phase-18-step-replication.json")
