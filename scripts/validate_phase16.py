"""Phase 16: the rumor of danger. Artifacts:

  results/phase-16-rumor.json              R2-R3 on seeds 1-24
  results/phase-16-rumor-replication.json  fresh seeds 31-54

R1 lives in tests/test_social.py as a kill switch. R2 measures the
cry-wolf ledger (credence converges to empirical alarm accuracy) in
the default drifting-hazard world. R3 measures the social cure in the
phase 5 boiling-frog inversion cell (testimony 1.0 vs 0.0, same
seeds). The pariah census (cred_floor 0 vs 0.01) is exploratory,
declared seeds only, no bar.

Run:
  uv run python scripts/validate_phase16.py all
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
from core.model import Model, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

FROG = {"bond_target": "nest", "bond_init": 0.6, "storm_nest": 0,
        "storm_onset": 2000, "storm_ramp": 200}
MIN_WINDOWS = 8


def ledger_cell(seed, cred_floor=0.01):
    """R2: step the default social arena, counting closed windows and
    hits per pair by replaying the close mask outside the organ."""
    cfg = replace(Config(), r_social=8.0, testimony=1.0,
                  cred_floor=cred_floor, n_hazard=9, hazard_drift=0.02)
    m = Model(cfg, seed)
    n = cfg.n_agents
    windows = np.zeros((n, n), dtype=np.int64)
    hits = np.zeros((n, n), dtype=np.int64)
    for _ in range(5000):
        prev_open = m.social.window_open.copy()
        m.step()
        tick = m.tick - 1
        closed = (prev_open >= 0) & (prev_open == tick - cfg.verify_window)
        if closed.any():
            rows, cols = np.nonzero(closed)
            score = m.social.last_peril[rows] > prev_open[rows, cols]
            windows[rows, cols] += 1
            hits[rows, cols] += score
    qual = windows >= MIN_WINDOWS
    acc = hits[qual] / windows[qual]
    cred = m.social.credence[qual]
    pariah = int(((m.social.credence < 0.05) & (windows > 0)).sum())
    return {"seed": seed, "cred_floor": cred_floor,
            "config_hash": cfg.config_hash(),
            "n_qualifying": int(qual.sum()),
            "gaps": [round(float(g), 4) for g in np.abs(cred - acc)],
            "accuracies": [round(float(a), 4) for a in acc],
            "pariah_pairs": pariah,
            "scored_pairs": int((windows > 0).sum())}


def frog_cell(testimony, seed):
    """R3: the boiling-frog inversion cell, nest-0 cohort window
    mortality, phase 5 accounting."""
    cfg = replace(Config(), **FROG, r_social=8.0, testimony=testimony)
    traj = run(cfg, seed=seed, ticks=3000)
    ticks = np.array(traj["tick"])
    alive = traj["alive"]
    k_on = int(np.argmax(ticks >= cfg.storm_onset))
    cohort = (np.arange(cfg.n_agents) % cfg.n_nests == 0) & alive[k_on]
    dead = cohort & ~alive[-1]
    return {"testimony": testimony, "seed": seed,
            "config_hash": cfg.config_hash(),
            "cohort": int(cohort.sum()), "window_deaths": int(dead.sum())}


def _cell(args):
    kind = args[0]
    if kind == "ledger":
        return {"kind": "ledger", **ledger_cell(args[1], cred_floor=args[2])}
    return {"kind": "frog", **frog_cell(args[1], args[2])}


def run_stage(seeds, out_path, with_pariah):
    jobs = [("ledger", s, 0.01) for s in seeds]
    jobs += [("frog", t, s) for t in (0.0, 1.0) for s in seeds]
    if with_pariah:
        jobs += [("ledger", s, 0.0) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-16.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    led = [r for r in rows if r["kind"] == "ledger" and r["cred_floor"] == 0.01]
    gaps = np.concatenate([np.array(r["gaps"]) for r in led] or [np.array([])])
    accs = np.concatenate([np.array(r["accuracies"]) for r in led] or [np.array([])])
    nq = int(gaps.size)
    med = float(np.median(gaps)) if nq else None
    art["R2"] = {"qualifying_pairs": nq,
                 "median_gap": med,
                 "accuracy_mean": float(accs.mean()) if nq else None,
                 "accuracy_below_half": int((accs < 0.5).sum()),
                 "underpowered": bool(nq < 50),
                 "passed": bool(nq >= 50 and med is not None and med <= 0.10)}
    print(f"R2 cry-wolf ledger: {nq} qualifying pairs, median |credence - "
          f"accuracy| {med}, mean accuracy {art['R2']['accuracy_mean']}, "
          f"passed {art['R2']['passed']} (underpowered {art['R2']['underpowered']})")

    frog = [r for r in rows if r["kind"] == "frog"]
    rates = {}
    for t in (0.0, 1.0):
        sel = [r for r in frog if r["testimony"] == t]
        coh = sum(r["cohort"] for r in sel)
        dth = sum(r["window_deaths"] for r in sel)
        rates[t] = dth / max(coh, 1)
        art[f"frog_mortality_t{t}"] = {"cohort": coh, "deaths": dth,
                                       "rate": rates[t]}
    rel = (rates[0.0] - rates[1.0]) / max(rates[0.0], 1e-9)
    art["R3"] = {"mortality_off": rates[0.0], "mortality_on": rates[1.0],
                 "relative_reduction": rel, "passed": bool(rel >= 0.25)}
    print(f"R3 social cure: mortality off {rates[0.0]:.3f} vs on "
          f"{rates[1.0]:.3f}, relative reduction {100 * rel:+.1f} pct, "
          f"passed {art['R3']['passed']}")

    if with_pariah:
        for fl in (0.01, 0.0):
            sel = [r for r in rows if r["kind"] == "ledger"
                   and r["cred_floor"] == fl]
            art[f"pariah_floor_{fl}"] = {
                "pariah_pairs": sum(r["pariah_pairs"] for r in sel),
                "scored_pairs": sum(r["scored_pairs"] for r in sel)}
            print(f"pariah census floor {fl}: "
                  f"{art[f'pariah_floor_{fl}']['pariah_pairs']} pariah pairs "
                  f"of {art[f'pariah_floor_{fl}']['scored_pairs']} scored")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-16-rumor.json", True)
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-16-rumor-replication.json", False)
    else:
        run_stage(range(1, 25), RESULTS / "phase-16-rumor.json", True)
        run_stage(range(31, 55),
                  RESULTS / "phase-16-rumor-replication.json", False)
