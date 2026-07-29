"""Phase 24: birth. Artifacts:

  results/phase-24-birth.json              G2-G4 on seeds 1-24
  results/phase-24-birth-replication.json  fresh seeds 31-54

G1 lives in the golden suite. G2: the loop lives (famine arena,
births vs birthless twin). G3: heritability (parent-child tau_safety
rho). G4: the world breeds its minds (hazard-rich, heritable fear
clocks, 6000 ticks: does mean tau_safety fall?).

Run:
  uv run python scripts/validate_phase24.py all
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

FAMINE = {"r_sight": 12.0, "memory_slots": 8, "n_food": 60,
          "n_hazard": 0}
SELECT = {"n_food": 90, "tau_safety_spread": 0.5}
BIRTH = {"birth_threshold": 0.9, "birth_cost": 0.4}


def famine_cell(births, seed):
    kw = dict(FAMINE)
    if births:
        kw.update(BIRTH)
    cfg = replace(Config(), **kw)
    m = Model(cfg, seed)
    born = 0
    prev_tau = m.arrays.tau[:, 1].copy()
    for _ in range(3000):
        m.step()
        # A birth is a trait change: traits change nowhere else (the
        # write-site tripwires are the instrument's ground truth).
        born += int((m.arrays.tau[:, 1] != prev_tau).sum())
        prev_tau = m.arrays.tau[:, 1].copy()
    return {"kind": "famine", "births": births, "seed": seed,
            "config_hash": cfg.config_hash(), "n": cfg.n_agents,
            "born": born, "final_alive": int(m.arrays.alive.sum())}


def select_cell(seed, ticks=6000):
    cfg = replace(Config(), **SELECT, **BIRTH)
    m = Model(cfg, seed)
    tau0 = float(m.arrays.tau[m.arrays.alive, 1].mean())
    parent_tau, child_tau = [], []
    prev_tau = m.arrays.tau[:, 1].copy()
    for _ in range(ticks):
        m.step()
        born = m.arrays.tau[:, 1] != prev_tau
        # Parent attribution: births pair lowest parent to lowest
        # cradle in-order; recover by re-running the same rule on the
        # pre-step state is overkill here, so G3 uses the mutation
        # channel directly: a child's tau is its parent's times a
        # lognormal, so regressing child on the POPULATION of eligible
        # parents is noisy; instead record (child tau, nearest agent's
        # tau at birth position), declared as the kinship proxy.
        for c in np.flatnonzero(born):
            d = np.hypot(m.arrays.x - m.arrays.x[c],
                         m.arrays.y - m.arrays.y[c])
            d[c] = np.inf
            d[~m.arrays.alive] = np.inf
            p = int(np.argmin(d))
            parent_tau.append(float(prev_tau[p]))
            child_tau.append(float(m.arrays.tau[c, 1]))
        prev_tau = m.arrays.tau[:, 1].copy()
    alive = m.arrays.alive
    tau_end = float(m.arrays.tau[alive, 1].mean()) if alive.any() else None
    return {"kind": "select", "seed": seed,
            "config_hash": cfg.config_hash(),
            "tau_safety_start": tau0, "tau_safety_end": tau_end,
            "births": len(child_tau),
            "parent_tau": parent_tau, "child_tau": child_tau,
            "final_alive": int(alive.sum())}


def _cell(args):
    kind = args[0]
    if kind == "famine":
        return famine_cell(args[1], args[2])
    return select_cell(args[1])


def run_stage(seeds, out_path):
    jobs = [("famine", b, s) for b in (True, False) for s in seeds]
    jobs += [("select", s) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-24.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    fon = [r for r in rows if r["kind"] == "famine" and r["births"]]
    foff = [r for r in rows if r["kind"] == "famine" and not r["births"]]
    born = sum(r["born"] for r in fon)
    pop_on = sum(r["final_alive"] for r in fon)
    pop_off = sum(r["final_alive"] for r in foff)
    g2 = born >= 500 and pop_on >= 1.2 * pop_off
    art["G2"] = {"births": born, "final_pop_on": pop_on,
                 "final_pop_off": pop_off,
                 "pop_ratio": pop_on / max(pop_off, 1), "passed": bool(g2)}
    print(f"G2 the loop lives: {born} births (floor 500), final pop "
          f"{pop_on} vs birthless {pop_off} (ratio "
          f"{art['G2']['pop_ratio']:.2f}, bar 1.2): passed {g2}")

    sel = [r for r in rows if r["kind"] == "select"]
    pt = np.concatenate([np.array(r["parent_tau"]) for r in sel])
    ct = np.concatenate([np.array(r["child_tau"]) for r in sel])
    rho = float(spearmanr(pt, ct).statistic) if pt.size > 2 else None
    g3 = pt.size >= 300 and rho is not None and rho >= 0.8
    art["G3"] = {"recorded_births": int(pt.size), "rho": rho,
                 "passed": bool(g3)}
    print(f"G3 heritability: {pt.size} births, parent-child rho {rho} "
          f"(bar 0.8 at n>=300): passed {g3}")

    starts = [r["tau_safety_start"] for r in sel]
    ends = [r["tau_safety_end"] for r in sel if r["tau_safety_end"]]
    t0, t1 = float(np.mean(starts)), float(np.mean(ends))
    g4 = t1 <= 0.9 * t0
    art["G4"] = {"tau_safety_start": t0, "tau_safety_end": t1,
                 "change_pct": 100 * (t1 - t0) / t0, "passed": bool(g4)}
    print(f"G4 the world breeds its minds: mean tau_safety {t0:.2f} -> "
          f"{t1:.2f} ({art['G4']['change_pct']:+.1f} pct, bar -10): "
          f"passed {g4}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-24-birth.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-24-birth-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-24-birth.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-24-birth-replication.json")
