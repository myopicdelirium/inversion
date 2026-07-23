"""Phase 12: the search for the clear-eyed region. Artifacts:

  results/phase-12-search.json       the full grid, S1-S3 judged
  results/phase-12-replication.json  fresh-seed rerun of headline cells

Run:
  uv run python scripts/validate_phase12.py search
  uv run python scripts/validate_phase12.py replicate
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
from core.model import Model  # noqa: E402
from core.world import _torus_delta, perceive_partner  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

MIRE = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
        "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
        "storm_snare": 0.95, "storm_damage": 0.01}

TAUS_S = (12.0, 24.0, 48.0)
KAPPAS = (0.0, 0.75)
BONDS = (0.8, 1.0)
HORIZONS = (20, 60)
SEEDS = tuple(range(1, 13))
FRESH = tuple(range(31, 43))


def seen_exposure(cfg, danger, v_eff, proj, scale, arrive, h):
    """The agent's own safety-row cost for a held approach: cumulative
    predicted danger along the path, motion capped at arrival, the
    arrival level held thereafter. Mirrors core/action.py's integral
    (analysis copy, exposure as a positive number)."""
    factor = np.exp(-v_eff * proj / np.maximum(scale, 1e-9))
    steps = np.minimum(np.where(np.isfinite(arrive), arrive, float(h)), float(h))
    near_one = np.isclose(factor, 1.0)
    safe = np.where(near_one, 0.5, factor)
    with np.errstate(over="ignore", invalid="ignore"):
        series = safe * (1.0 - safe ** steps) / (1.0 - safe)
        at_cap = factor ** steps
    series = np.where(near_one, steps, series)
    at_cap = np.where(near_one, 1.0, at_cap)
    # Total predicted danger integrated over h ticks along this path.
    return danger * series + (h - steps) * danger * at_cap


def search_cell(args):
    tau_s, kappa, bond_init, h, seed = args
    floor = 0.05 if kappa > 0 else 0.0
    cfg = replace(Config(), **MIRE, tau_safety=tau_s, attention_sharpness=kappa,
                  attention_floor=floor, bond_init=bond_init, prospect_horizon=h)
    m = Model(cfg, seed)
    n = cfg.n_agents
    for _ in range(2050):
        m.step()
    sx, sy = m.world.storm_x, m.world.storm_y

    def inside_now():
        dx = _torus_delta(m.arrays.x - sx, cfg.world_size)
        dy = _torus_delta(m.arrays.y - sy, cfg.world_size)
        return np.hypot(dx, dy) < cfg.storm_radius

    inside = inside_now()
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    trapped = has & m.arrays.alive[pidx] & inside[pidx]
    outside = m.arrays.alive & ~inside
    g_pull = outside & trapped
    g_safe = outside & has & m.arrays.alive[pidx] & ~inside[pidx]

    entered = np.zeros(n, dtype=bool)
    clear_eyed = np.zeros(n, dtype=bool)
    pull_idx = np.flatnonzero(g_pull)
    for _ in range(1200):
        actions = m.step()
        alive_in = m.arrays.alive & inside_now()
        entered |= alive_in
        if pull_idx.size and h > 0:
            # Was this tick's return choice clear-eyed? Reprice the
            # chosen path with the agent's own integral, against the
            # agent's remaining life.
            sub = pull_idx[m.arrays.alive[pull_idx]
                           & (actions[pull_idx] == RETURN_HOME)]
            if sub.size:
                dx = _torus_delta(m.arrays.x[sub] - sx, cfg.world_size)
                dy = _torus_delta(m.arrays.y[sub] - sy, cfg.world_size)
                sd = np.hypot(dx, dy)
                danger = m._storm_intensity() * np.exp(-sd / cfg.storm_radius)
                sdir_x, sdir_y = dx / np.maximum(sd, 1e-12), dy / np.maximum(sd, 1e-12)
                d_t, tdir_x, tdir_y = perceive_partner(m.arrays, cfg)
                v_eff = cfg.speed * (1.0 - m.arrays.fatigue[sub] / 2.0)
                proj = tdir_x[sub] * sdir_x + tdir_y[sub] * sdir_y
                arrive = np.ceil(d_t[sub] / v_eff)
                exp_seen = seen_exposure(cfg, danger, v_eff, proj,
                                         cfg.storm_radius, arrive, h)
                lethal = exp_seen * cfg.storm_damage >= m.arrays.integrity[sub]
                clear_eyed[sub[lethal]] = True
    died = ~m.arrays.alive
    return {
        "tau_safety": tau_s, "kappa": kappa, "bond_init": bond_init,
        "h": h, "seed": seed, "config_hash": cfg.config_hash(),
        "n_pull": int(g_pull.sum()), "n_safe": int(g_safe.sum()),
        "deaths_pull": int((died & g_pull).sum()),
        "deaths_safe": int((died & g_safe).sum()),
        "pull_dead_entered": int((died & g_pull & entered).sum()),
        "pull_dead_clear_eyed": int((died & g_pull & entered & clear_eyed).sum()),
    }


def pool_cells(rows):
    np_ = sum(r["n_pull"] for r in rows)
    ns = sum(r["n_safe"] for r in rows)
    dp = sum(r["deaths_pull"] for r in rows)
    ds = sum(r["deaths_safe"] for r in rows)
    ent = sum(r["pull_dead_entered"] for r in rows)
    ce = sum(r["pull_dead_clear_eyed"] for r in rows)
    mp, ms = dp / max(np_, 1), ds / max(ns, 1)
    return {"n_pull": np_, "n_safe": ns, "deaths_pull": dp,
            "mortality_pull": mp, "mortality_safe": ms,
            "ratio": mp / max(ms, 1e-9),
            "entered_share": ent / max(dp, 1),
            "clear_eyed_share": ce / max(dp, 1)}


def run_grid(seeds, out_path, workers=6):
    jobs = [(ts, k, b, h, s) for ts in TAUS_S for k in KAPPAS
            for b in (*BONDS, 0.0) for h in HORIZONS for s in seeds]
    # bond 0 arms are the controls, one per (tau_s, kappa, h).
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(search_cell, jobs))
    cells = []
    for ts in TAUS_S:
        for k in KAPPAS:
            for h in HORIZONS:
                ctrl = pool_cells([r for r in rows if
                                   (r["tau_safety"], r["kappa"], r["bond_init"], r["h"]) == (ts, k, 0.0, h)])
                for b in BONDS:
                    cell_rows = [r for r in rows if
                                 (r["tau_safety"], r["kappa"], r["bond_init"], r["h"]) == (ts, k, b, h)]
                    agg = pool_cells(cell_rows)
                    ratio_vs_ctrl = agg["mortality_pull"] / max(ctrl["mortality_pull"], 1e-9) \
                        if ctrl["mortality_pull"] > 0 else float("inf") if agg["mortality_pull"] > 0 else 0.0
                    clear = (agg["mortality_pull"] >= 2.0 * max(ctrl["mortality_pull"], 0.01)
                             and agg["entered_share"] >= 0.7
                             and agg["clear_eyed_share"] >= 0.5
                             and agg["deaths_pull"] >= 4)
                    cells.append({"tau_safety": ts, "kappa": k, "bond_init": b,
                                  "h": h, "pooled": agg, "control": ctrl,
                                  "clear_eyed_cell": bool(clear), "runs": cell_rows})
                    print(f"  tau_s {ts:>4} kappa {k} bond {b} h {h:>2}: pull "
                          f"{agg['mortality_pull']:.2f} (n {agg['n_pull']}) vs ctrl "
                          f"{ctrl['mortality_pull']:.2f}, entered {agg['entered_share']:.2f}, "
                          f"clear-eyed {agg['clear_eyed_share']:.2f}"
                          f"{'  <== CLEAR-EYED CELL' if clear else ''}")
    found = [c for c in cells if c["clear_eyed_cell"]]
    artifact = {"spec": "specs/phase-12.md",
                "manifest": build_manifest(seed=0, config=Config()),
                "seeds": list(seeds), "cells": cells,
                "S1_clear_eyed_cells_found": len(found),
                "S1_locations": [{k: c[k] for k in ("tau_safety", "kappa", "bond_init", "h")}
                                 for c in found]}
    out_path.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"clear-eyed cells found: {len(found)}")
    return artifact


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "search":
        run_grid(SEEDS, RESULTS / "phase-12-search.json")
    else:
        run_grid(FRESH, RESULTS / "phase-12-replication.json")
