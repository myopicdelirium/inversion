"""Phase 22 addendum: the travel ledger. Artifacts:

  results/phase-22-travel.json              T1-T3 on seeds 1-24
  results/phase-22-travel-replication.json  fresh seeds 31-54

Byte-identical reruns of the B2 cells billing every meal with the
distance walked since the previous one. Told-origin meals are eaten
within an eating radius of a told site confirmed (converted) within
the shadow window.

Run:
  uv run python scripts/validate_phase22_travel.py all
"""

import json
import pathlib
import sys
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"r_sight": 12.0, "memory_slots": 8, "r_social": 8.0,
         "n_food": 60, "testimony": 0.0}
TICKS = 3000
SHADOW = 100  # ticks a confirmed told site stays attributable


def cell(telling, seed):
    cfg = replace(Config(), **ARENA, tell_places=telling)
    m = Model(cfg, seed)
    n = cfg.n_agents
    k = cfg.memory_slots
    prev_told = np.zeros((n, k), dtype=bool)
    prev_x = np.zeros((n, k))
    prev_y = np.zeros((n, k))
    prev_ax = m.arrays.x.copy()
    prev_ay = m.arrays.y.copy()
    prev_energy = m.arrays.energy.copy()
    dist_since_meal = np.zeros(n)
    ticks_since_meal = np.zeros(n, dtype=np.int64)
    shadows = [deque() for _ in range(n)]  # (x, y, tick) of conversions

    told_dist, own_dist = [], []
    told_gap, own_gap = [], []

    for _ in range(TICKS):
        m.step()
        mem = m.memory
        now_told = mem.mem_told
        now_valid = mem.mem_seen >= 0
        stamp = mem.mem_seen == m.tick - 1
        near_prev = np.hypot(
            _torus_delta(mem.mem_x - prev_x, cfg.world_size),
            _torus_delta(mem.mem_y - prev_y, cfg.world_size)
        ) <= cfg.r_eat
        confirmed = prev_told & now_valid & ~now_told & stamp & near_prev
        for li, sj in zip(*np.nonzero(confirmed)):
            shadows[li].append((mem.mem_x[li, sj], mem.mem_y[li, sj],
                                m.tick))
        # Travel accounting.
        step_d = np.hypot(
            _torus_delta(m.arrays.x - prev_ax, cfg.world_size),
            _torus_delta(m.arrays.y - prev_ay, cfg.world_size))
        dist_since_meal += np.where(m.arrays.alive, step_d, 0.0)
        ticks_since_meal += m.arrays.alive.astype(np.int64)
        # Meals: energy jumped by more than half a bite.
        ate = m.arrays.alive & (m.arrays.energy - prev_energy
                                > cfg.gain_eat / 2.0)
        for i in np.flatnonzero(ate):
            sh = shadows[i]
            while sh and m.tick - sh[0][2] > SHADOW:
                sh.popleft()
            is_told = any(
                np.hypot(_torus_delta(m.arrays.x[i] - sx, cfg.world_size),
                         _torus_delta(m.arrays.y[i] - sy, cfg.world_size))
                <= cfg.r_eat for sx, sy, _ in sh)
            (told_dist if is_told else own_dist).append(
                float(dist_since_meal[i]))
            (told_gap if is_told else own_gap).append(
                int(ticks_since_meal[i]))
            dist_since_meal[i] = 0.0
            ticks_since_meal[i] = 0
        prev_told = now_told.copy()
        prev_x = mem.mem_x.copy()
        prev_y = mem.mem_y.copy()
        prev_ax = m.arrays.x.copy()
        prev_ay = m.arrays.y.copy()
        prev_energy = m.arrays.energy.copy()

    agent_ticks = TICKS * n  # denominator convention, declared
    return {"telling": telling, "seed": seed,
            "config_hash": cfg.config_hash(),
            "told_dist_sum": float(np.sum(told_dist)),
            "told_meals": len(told_dist),
            "own_dist_sum": float(np.sum(own_dist)),
            "own_meals": len(own_dist),
            "told_gap_sum": int(np.sum(told_gap)),
            "own_gap_sum": int(np.sum(own_gap)),
            "agent_ticks": agent_ticks}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(t, s) for t in (True, False) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-22.md travel-ledger addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}
    on = [r for r in rows if r["telling"]]
    off = [r for r in rows if not r["telling"]]

    td = sum(r["told_dist_sum"] for r in on)
    tm = sum(r["told_meals"] for r in on)
    od = sum(r["own_dist_sum"] for r in on)
    om = sum(r["own_meals"] for r in on)
    mean_told = td / max(tm, 1)
    mean_own = od / max(om, 1)
    t1 = om > 0 and tm > 0 and mean_told >= 1.5 * mean_own
    art["T1"] = {"mean_dist_told": mean_told, "mean_dist_own": mean_own,
                 "ratio": mean_told / max(mean_own, 1e-9),
                 "told_meals": tm, "own_meals": om, "passed": bool(t1)}
    print(f"T1 the conviction: told meals cost {mean_told:.1f} per "
          f"meal (n {tm}) vs own {mean_own:.1f} (n {om}), ratio "
          f"{art['T1']['ratio']:.2f} (bar 1.5): passed {t1}")

    all_on = (td + od) / max(tm + om, 1)
    all_off = (sum(r["own_dist_sum"] + r["told_dist_sum"] for r in off)
               / max(sum(r["own_meals"] + r["told_meals"] for r in off), 1))
    t2 = all_on >= 1.15 * all_off
    art["T2"] = {"mean_dist_all_on": all_on, "mean_dist_all_off": all_off,
                 "ratio": all_on / max(all_off, 1e-9), "passed": bool(t2)}
    print(f"T2 the economy: telling {all_on:.1f} per meal vs off "
          f"{all_off:.1f} (ratio {art['T2']['ratio']:.2f}, bar 1.15): "
          f"passed {t2}")

    def throughput(rows_):
        meals = sum(r["told_meals"] + r["own_meals"] for r in rows_)
        return 1000.0 * meals / sum(r["agent_ticks"] for r in rows_)

    art["T3"] = {"meals_per_1000_on": throughput(on),
                 "meals_per_1000_off": throughput(off),
                 "mean_gap_told": (sum(r["told_gap_sum"] for r in on)
                                   / max(tm, 1)),
                 "mean_gap_own": (sum(r["own_gap_sum"] for r in on)
                                  / max(om, 1))}
    print(f"T3 throughput: {art['T3']['meals_per_1000_on']:.1f} meals "
          f"per 1000 agent-ticks telling vs "
          f"{art['T3']['meals_per_1000_off']:.1f} off; meal gap told "
          f"{art['T3']['mean_gap_told']:.0f} vs own "
          f"{art['T3']['mean_gap_own']:.0f} ticks (no bar)")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-22-travel.json")
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-22-travel-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-22-travel.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-22-travel-replication.json")
