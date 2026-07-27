"""Phase 18: the shapes of minds. Artifacts:

  results/phase-18-minds.json              T2-T4 on seeds 1-24
  results/phase-18-minds-replication.json  fresh seeds 31-54

T1 (inertness) lives in the golden suite. T2: grief sorts on
attention style (phase 7 origin arena, attention_spread 0.5). T3:
the storm sorts on foresight (phase 11 mire arena, prospect_spread
0.5 at median 60). T4: mixed vs uniform composition, reported
without bar.

Run:
  uv run python scripts/validate_phase18.py all
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
from core.model import Model, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# The phase 7 origin arena: partner grief at sharp attention, floor 0.
GRIEF = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "bond_init": 0.8, "attention_sharpness": 2.0}
# The phase 11 mire: the storm that holds what it is killing.
MIRE = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
        "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
        "storm_snare": 0.95, "storm_damage": 0.01, "bond_init": 0.8,
        "prospect_horizon": 60}
ONSET_TICK = 2000
TICKS = 3500


def grief_cell(spread, seed):
    cfg = replace(Config(), **GRIEF, attention_spread=spread)
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
    return {"kind": "grief", "spread": spread, "seed": seed,
            "config_hash": cfg.config_hash(),
            "n": n, "deaths": int((~m.arrays.alive).sum()),
            "bereaved_kappa": [round(float(k), 4) for k in kappa[bereaved]],
            "bereaved_starved": [bool(s) for s in starved[bereaved]]}


def mire_cell(spread, seed):
    cfg = replace(Config(), **MIRE, prospect_spread=spread)
    m = Model(cfg, seed)
    horizon = m.arrays.horizon.copy()
    for _ in range(ONSET_TICK):
        m.step()
    at_onset = m.arrays.alive.copy()
    for _ in range(TICKS - ONSET_TICK):
        m.step()
    died_window = at_onset & ~m.arrays.alive
    return {"kind": "mire", "spread": spread, "seed": seed,
            "config_hash": cfg.config_hash(),
            "n": cfg.n_agents, "n_at_onset": int(at_onset.sum()),
            "onset_horizon": [round(float(h), 1) for h in horizon[at_onset]],
            "onset_died": [bool(d) for d in died_window[at_onset]]}


def _cell(args):
    kind, spread, seed = args
    return grief_cell(spread, seed) if kind == "grief" else mire_cell(spread, seed)


def run_stage(seeds, out_path):
    jobs = [(k, sp, s) for k in ("grief", "mire") for sp in (0.5, 0.0)
            for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-18.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    g = [r for r in rows if r["kind"] == "grief" and r["spread"] == 0.5]
    kap = np.concatenate([np.array(r["bereaved_kappa"]) for r in g])
    stv = np.concatenate([np.array(r["bereaved_starved"], dtype=bool)
                          for r in g])
    rho_g = float(spearmanr(kap, stv).statistic) if kap.size > 1 else None
    art["T2"] = {"n_bereaved": int(kap.size),
                 "neglect_rate": float(stv.mean()) if kap.size else None,
                 "spearman_rho": rho_g,
                 "passed": bool(rho_g is not None and rho_g >= 0.3)}
    print(f"T2 grief sorts on attention: n_bereaved {kap.size}, "
          f"neglect {art['T2']['neglect_rate']}, rho {rho_g}, "
          f"passed {art['T2']['passed']}")

    mrows = [r for r in rows if r["kind"] == "mire" and r["spread"] == 0.5]
    hor = np.concatenate([np.array(r["onset_horizon"]) for r in mrows])
    dd = np.concatenate([np.array(r["onset_died"], dtype=bool)
                         for r in mrows])
    rho_m = float(spearmanr(hor, dd).statistic) if hor.size > 1 else None
    art["T3"] = {"n_at_onset": int(hor.size),
                 "window_mortality": float(dd.mean()) if hor.size else None,
                 "spearman_rho": rho_m,
                 "passed": bool(rho_m is not None and rho_m <= -0.3)}
    print(f"T3 storm sorts on foresight: n_at_onset {hor.size}, "
          f"mortality {art['T3']['window_mortality']}, rho {rho_m}, "
          f"passed {art['T3']['passed']}")

    comp = {}
    for kind in ("grief", "mire"):
        by = {}
        for sp in (0.5, 0.0):
            sel = [r for r in rows if r["kind"] == kind and r["spread"] == sp]
            if kind == "grief":
                dead = sum(r["deaths"] for r in sel)
                tot = sum(r["n"] for r in sel)
            else:
                dead = sum(sum(r["onset_died"]) for r in sel)
                tot = sum(r["n_at_onset"] for r in sel)
            by[str(sp)] = dead / max(tot, 1)
        comp[kind] = {"mixed": by["0.5"], "uniform": by["0.0"],
                      "gap_points": 100 * (by["0.5"] - by["0.0"])}
        print(f"T4 {kind}: mixed {by['0.5']:.3f} vs uniform "
              f"{by['0.0']:.3f} (gap {comp[kind]['gap_points']:+.1f} pts, "
              f"no bar)")
    art["T4"] = comp
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-18-minds.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-18-minds-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-18-minds.json")
        run_stage(range(31, 55), RESULTS / "phase-18-minds-replication.json")
