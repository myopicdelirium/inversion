"""Phase 14: the other in the ledger. Artifacts:

  results/phase-14-wager.json        W1/W2 grid, W3, W4
  results/phase-14-replication.json  the W1 grid on fresh seeds

Run:
  uv run python scripts/validate_phase14.py main
  uv run python scripts/validate_phase14.py replicate
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.action import RETURN_HOME  # noqa: E402
from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model, run  # noqa: E402
from core.world import _torus_delta, perceive_partner  # noqa: E402
from scripts.validate_phase13 import grip_exposure  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "storm_snare": 0.95, "storm_damage": 0.01, "tau_safety": 12.0,
         "prospect_horizon": 60, "prospect_sees_grip": True}

CARES = (0.0, 0.5, 1.0)
HELPS = (0.0, 0.5, 1.0)
SEEDS = tuple(range(1, 13))
FRESH = tuple(range(31, 43))


def cell_run(args):
    care, helps, seed = args
    cfg = replace(Config(), **ARENA, care=care, help_strength=helps)
    m = Model(cfg, seed)
    n = cfg.n_agents
    for _ in range(2050):
        m.step()
    sx, sy = m.world.storm_x, m.world.storm_y

    def storm_dist():
        return np.hypot(_torus_delta(m.arrays.x - sx, cfg.world_size),
                        _torus_delta(m.arrays.y - sy, cfg.world_size))

    inside = storm_dist() < cfg.storm_radius
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    trapped = m.arrays.alive & inside          # anyone caught inside
    g_pull = m.arrays.alive & ~inside & has & m.arrays.alive[pidx] & inside[pidx]
    g_safe = m.arrays.alive & ~inside & has & m.arrays.alive[pidx] & ~inside[pidx]
    pull_idx = np.flatnonzero(g_pull)

    entered = np.zeros(n, dtype=bool)
    clear_eyed = np.zeros(n, dtype=bool)
    up_front = np.zeros(n, dtype=bool)
    for _ in range(1200):
        actions = m.step()
        sd_all = storm_dist()
        entered |= m.arrays.alive & (sd_all < cfg.storm_radius)
        if pull_idx.size:
            sub = pull_idx[m.arrays.alive[pull_idx]
                           & (actions[pull_idx] == RETURN_HOME)]
            if sub.size:
                d_t, _, _ = perceive_partner(m.arrays, cfg)
                fin = sub[np.isfinite(d_t[sub])]
                if fin.size:
                    sd = sd_all[fin]
                    danger = m._storm_intensity() * np.exp(-sd / cfg.storm_radius)
                    sdx = _torus_delta(m.arrays.x[fin] - sx, cfg.world_size)
                    sdy = _torus_delta(m.arrays.y[fin] - sy, cfg.world_size)
                    sn = np.maximum(np.hypot(sdx, sdy), 1e-12)
                    tdx = _torus_delta(m.arrays.x[pidx[fin]] - m.arrays.x[fin], cfg.world_size)
                    tdy = _torus_delta(m.arrays.y[pidx[fin]] - m.arrays.y[fin], cfg.world_size)
                    tn = np.maximum(np.hypot(tdx, tdy), 1e-12)
                    proj = (tdx / tn) * (sdx / sn) + (tdy / tn) * (sdy / sn)
                    v_eff = cfg.speed * (1.0 - m.arrays.fatigue[fin] / 2.0)
                    pc = np.hypot(
                        _torus_delta(m.arrays.x[pidx[fin]] - sx, cfg.world_size),
                        _torus_delta(m.arrays.y[pidx[fin]] - sy, cfg.world_size))
                    exposure = grip_exposure(cfg, danger, v_eff, proj,
                                             d_t[fin], pc, cfg.prospect_horizon)
                    lethal = exposure * cfg.storm_damage >= m.arrays.integrity[fin]
                    hit = fin[lethal]
                    clear_eyed[hit] = True
                    up_front[hit[m.arrays.integrity[hit] >= 0.8]] = True
    died = ~m.arrays.alive
    now_inside = storm_dist() < cfg.storm_radius
    extracted = trapped & m.arrays.alive & ~now_inside
    starved = died & (m.arrays.energy <= 0.0)
    return {"care": care, "help": helps, "seed": seed,
            "config_hash": cfg.config_hash(),
            "n_trapped": int(trapped.sum()),
            "extracted": int(extracted.sum()),
            "trapped_alive_end": int((trapped & m.arrays.alive).sum()),
            "n_pull": int(g_pull.sum()), "n_safe": int(g_safe.sum()),
            "deaths_pull": int((died & g_pull).sum()),
            "deaths_safe": int((died & g_safe).sum()),
            "pull_dead_entered": int((died & g_pull & entered).sum()),
            "pull_dead_starved": int((starved & g_pull).sum()),
            "pull_dead_clear_eyed": int((died & g_pull & entered & clear_eyed).sum()),
            "pull_dead_up_front": int((died & g_pull & entered & up_front).sum())}


def run_grid(seeds, out_path):
    jobs = [(c, hs, sd) for c in CARES for hs in HELPS for sd in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell_run, jobs))
    cells = []
    for c in CARES:
        for hs in HELPS:
            sel = [r for r in rows if (r["care"], r["help"]) == (c, hs)]
            nt = sum(r["n_trapped"] for r in sel)
            np_ = sum(r["n_pull"] for r in sel)
            ns = sum(r["n_safe"] for r in sel)
            dp = sum(r["deaths_pull"] for r in sel)
            ds = sum(r["deaths_safe"] for r in sel)
            cell = {"care": c, "help": hs,
                    "extraction_rate": sum(r["extracted"] for r in sel) / max(nt, 1),
                    "trapped_survival": sum(r["trapped_alive_end"] for r in sel) / max(nt, 1),
                    "mortality_pull": dp / max(np_, 1),
                    "mortality_safe": ds / max(ns, 1),
                    "n_pull": np_, "n_trapped": nt, "deaths_pull": dp,
                    "entered_share": sum(r["pull_dead_entered"] for r in sel) / max(dp, 1),
                    "starved_share": sum(r["pull_dead_starved"] for r in sel) / max(dp, 1),
                    "clear_eyed": sum(r["pull_dead_clear_eyed"] for r in sel),
                    "up_front": sum(r["pull_dead_up_front"] for r in sel),
                    "runs": sel}
            cells.append(cell)
            print(f"  care {c} help {hs}: extraction {cell['extraction_rate']:.2f} "
                  f"(trapped n {nt}), pull mort {cell['mortality_pull']:.2f} "
                  f"(n {np_}) vs safe {cell['mortality_safe']:.2f}, entered "
                  f"{cell['entered_share']:.2f}, clear-eyed {cell['clear_eyed']}, "
                  f"up-front {cell['up_front']}")
    artifact = {"spec": "specs/phase-14.md",
                "manifest": build_manifest(seed=0, config=Config()),
                "seeds": list(seeds), "cells": cells}
    out_path.write_text(json.dumps(artifact, indent=2) + "\n")


def w3_and_w4():
    print("W3: the everyday tax")
    out = {}
    for c in (0.0, 1.0):
        vals = [float(run(replace(Config(), bond_target="partner", care=c),
                          seed=s, ticks=5000)["alive"][-1].mean())
                for s in range(1, 6)]
        out[str(c)] = float(np.mean(vals))
        print(f"  care {c}: survival {out[str(c)]:.3f}")
    out["passed"] = bool(abs(out["0.0"] - out["1.0"]) <= 0.03)

    print("W4: care urgency identity")
    cfg = replace(Config(), **ARENA, care=0.7, help_strength=0.5, record_every=1)
    seed = 5
    traj = run(cfg, seed=seed, ticks=2600)
    m0 = Model(cfg, seed)
    p = m0.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    sx, sy = m0.world.storm_x, m0.world.storm_y
    x, y, b, alive = traj["x"], traj["y"], traj["bond"], traj["alive"]
    px, py = x[:, pidx], y[:, pidx]
    present = has[None, :] & alive[:, pidx]
    dx = _torus_delta(px - x, cfg.world_size)
    dy = _torus_delta(py - y, cfg.world_size)
    d = np.where(present, np.hypot(dx, dy), np.inf)
    sep = 1.0 - np.exp(-d / cfg.r_bond)
    ticks = np.array(traj["tick"])
    intensity = np.where(ticks >= cfg.storm_onset, 1.0, 0.0)
    sd = np.hypot(_torus_delta(px - sx, cfg.world_size),
                  _torus_delta(py - sy, cfg.world_size))
    peril = np.where(present, intensity[:, None] * np.exp(-sd / cfg.storm_radius), 0.0)
    expected = b[:-1] * np.clip(sep[:-1] + cfg.care * peril[:-1], 0.0, 1.0)
    live = alive[1:]
    residual = float(np.max(np.abs(traj["urgency"][1:, :, 3][live] - expected[live])))
    print(f"  max residual {residual:.1e}")
    return out, {"seed": seed, "config_hash": cfg.config_hash(),
                 "max_abs_residual": residual, "passed": bool(residual < 1e-9)}


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_grid(SEEDS, RESULTS / "phase-14-wager.json")
        w3, w4 = w3_and_w4()
        a = json.loads((RESULTS / "phase-14-wager.json").read_text())
        a["W3_everyday_tax"] = w3
        a["W4_identity"] = w4
        (RESULTS / "phase-14-wager.json").write_text(json.dumps(a, indent=2) + "\n")
    else:
        run_grid(FRESH, RESULTS / "phase-14-replication.json")
