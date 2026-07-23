"""Phase 13: full sight. Artifacts:

  results/phase-13-search.json       the grid, G1-G3 judged
  results/phase-13-replication.json  the full grid on fresh seeds

Run:
  uv run python scripts/validate_phase13.py search
  uv run python scripts/validate_phase13.py replicate
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
from scripts.validate_phase12 import seen_exposure  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

MIRE = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
        "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
        "storm_snare": 0.95, "storm_damage": 0.01}

TAUS_S = (12.0, 48.0)
KAPPAS = (0.0, 0.75)
HORIZONS = (60, 120)
SEES = (False, True)
SEEDS = tuple(range(1, 13))
FRESH = tuple(range(31, 43))


def grip_exposure(cfg, danger, v_eff, proj, dist_target, target_center, h):
    """The grip-aware seen exposure, mirroring core/action.py: outside
    leg geometric, then every remaining tick at the destination's
    danger."""
    inside_leg = np.maximum(0.0, cfg.storm_radius - target_center)
    outside_leg = np.maximum(0.0, dist_target - inside_leg)
    out_ticks = np.minimum(np.ceil(outside_leg / v_eff), float(h))
    factor = np.exp(-v_eff * proj / cfg.storm_radius)
    near_one = np.isclose(factor, 1.0)
    safe = np.where(near_one, 0.5, factor)
    with np.errstate(over="ignore", invalid="ignore"):
        series = safe * (1.0 - safe ** out_ticks) / (1.0 - safe)
    series = np.where(near_one, out_ticks, series)
    moving = danger * series
    danger_tgt = np.exp(-target_center / cfg.storm_radius)
    return moving + np.maximum(0.0, h - out_ticks) * danger_tgt


def cell_run(args):
    tau_s, kappa, h, sees, bond_init, seed = args
    floor = 0.05 if kappa > 0 else 0.0
    cfg = replace(Config(), **MIRE, tau_safety=tau_s, attention_sharpness=kappa,
                  attention_floor=floor, bond_init=bond_init,
                  prospect_horizon=h, prospect_sees_grip=sees)
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
                    if sees:
                        pc = np.hypot(
                            _torus_delta(m.arrays.x[pidx[fin]] - sx, cfg.world_size),
                            _torus_delta(m.arrays.y[pidx[fin]] - sy, cfg.world_size))
                        exposure = grip_exposure(cfg, danger, v_eff, proj,
                                                 d_t[fin], pc, h)
                    else:
                        exposure = seen_exposure(
                            cfg, danger, v_eff, proj, cfg.storm_radius,
                            np.ceil(d_t[fin] / v_eff), h)
                    lethal = exposure * cfg.storm_damage >= m.arrays.integrity[fin]
                    hit = fin[lethal]
                    clear_eyed[hit] = True
                    up_front[hit[m.arrays.integrity[hit] >= 0.8]] = True
    died = ~m.arrays.alive
    starved = died & (m.arrays.energy <= 0.0)
    return {"tau_safety": tau_s, "kappa": kappa, "h": h, "sees": sees,
            "bond_init": bond_init, "seed": seed,
            "config_hash": cfg.config_hash(),
            "n_pull": int(g_pull.sum()), "n_safe": int(g_safe.sum()),
            "deaths_pull": int((died & g_pull).sum()),
            "deaths_safe": int((died & g_safe).sum()),
            "pull_dead_entered": int((died & g_pull & entered).sum()),
            "pull_dead_starved": int((starved & g_pull).sum()),
            "safe_dead_starved": int((starved & g_safe).sum()),
            "pull_dead_clear_eyed": int((died & g_pull & entered & clear_eyed).sum()),
            "pull_dead_up_front": int((died & g_pull & entered & up_front).sum())}


def run_grid(seeds, out_path):
    jobs = [(ts, k, h, s, b, sd) for ts in TAUS_S for k in KAPPAS
            for h in HORIZONS for s in SEES for b in (1.0, 0.0)
            for sd in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell_run, jobs))

    def pooled(sel):
        np_ = sum(r["n_pull"] for r in sel)
        ns = sum(r["n_safe"] for r in sel)
        dp = sum(r["deaths_pull"] for r in sel)
        ds = sum(r["deaths_safe"] for r in sel)
        return {"n_pull": np_, "mortality_pull": dp / max(np_, 1),
                "mortality_safe": ds / max(ns, 1), "deaths_pull": dp,
                "entered_share": sum(r["pull_dead_entered"] for r in sel) / max(dp, 1),
                "clear_eyed_share": sum(r["pull_dead_clear_eyed"] for r in sel) / max(dp, 1),
                "up_front_deaths": sum(r["pull_dead_up_front"] for r in sel),
                "starved_share_pull": sum(r["pull_dead_starved"] for r in sel) / max(dp, 1),
                "starved_share_safe": sum(r["safe_dead_starved"] for r in sel) / max(ds, 1)}

    cells = []
    for ts in TAUS_S:
        for k in KAPPAS:
            for h in HORIZONS:
                for s in SEES:
                    key = lambda b: [r for r in rows if
                                     (r["tau_safety"], r["kappa"], r["h"], r["sees"], r["bond_init"]) == (ts, k, h, s, b)]
                    agg, ctrl = pooled(key(1.0)), pooled(key(0.0))
                    wager = (agg["mortality_pull"] >= 2.0 * max(ctrl["mortality_pull"], 0.01)
                             and agg["entered_share"] >= 0.7
                             and agg["clear_eyed_share"] >= 0.5
                             and agg["deaths_pull"] >= 4
                             and agg["up_front_deaths"] >= 1)
                    cells.append({"tau_safety": ts, "kappa": k, "h": h, "sees": s,
                                  "pooled": agg, "control": ctrl,
                                  "wager_cell": bool(wager), "runs": key(1.0) + key(0.0)})
                    print(f"  tau {ts:>4} kappa {k} h {h:>3} sees {int(s)}: pull "
                          f"{agg['mortality_pull']:.2f} (n {agg['n_pull']}) vs ctrl "
                          f"{ctrl['mortality_pull']:.2f}, entered {agg['entered_share']:.2f}, "
                          f"clear-eyed {agg['clear_eyed_share']:.2f}, up-front "
                          f"{agg['up_front_deaths']}, starved {agg['starved_share_pull']:.2f}"
                          f"{'  <== WAGER CELL' if wager else ''}")
    found = [c for c in cells if c["wager_cell"]]
    artifact = {"spec": "specs/phase-13.md",
                "manifest": build_manifest(seed=0, config=Config()),
                "seeds": list(seeds), "cells": cells,
                "G1_wager_cells_found": len(found)}
    out_path.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"wager cells found: {len(found)}")


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    if sys.argv[1] == "search":
        run_grid(SEEDS, RESULTS / "phase-13-search.json")
    else:
        run_grid(FRESH, RESULTS / "phase-13-replication.json")
