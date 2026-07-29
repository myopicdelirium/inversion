"""Phase 22 addendum: the synchronization measurement. Artifacts:

  results/phase-22-sync.json              C1-C3 on seeds 1-24
  results/phase-22-sync-replication.json  fresh seeds 31-54

Byte-identical reruns of the B2 cells with the crowd made visible:
nearest-neighbor distances each tick, and co-presence at every food
consumption.

Run:
  uv run python scripts/validate_phase22_sync.py all
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
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"r_sight": 12.0, "memory_slots": 8, "r_social": 8.0,
         "n_food": 60, "testimony": 0.0}
TICKS = 3000


def cell(telling, seed):
    cfg = replace(Config(), **ARENA, tell_places=telling)
    m = Model(cfg, seed)
    n = cfg.n_agents
    nn_sum = 0.0
    nn_ticks = 0
    consumptions = 0
    crowded = 0
    prev_timer = m.world.food_timer.copy()
    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()

    for _ in range(TICKS):
        m.step()
        alive = m.arrays.alive
        if alive.sum() >= 2:
            ax, ay = m.arrays.x[alive], m.arrays.y[alive]
            dx = _torus_delta(ax[None, :] - ax[:, None], cfg.world_size)
            dy = _torus_delta(ay[None, :] - ay[:, None], cfg.world_size)
            d = np.hypot(dx, dy)
            np.fill_diagonal(d, np.inf)
            nn_sum += float(d.min(axis=1).mean())
            nn_ticks += 1
        # A consumption is a food timer jumping from 0 to the respawn
        # clock this tick.
        eaten = (prev_timer == 0) & (m.world.food_timer > 0)
        if eaten.any():
            for fid in np.flatnonzero(eaten):
                fx, fy = m.world.food_x[fid], m.world.food_y[fid]
                fd = np.hypot(
                    _torus_delta(m.arrays.x[alive] - fx, cfg.world_size),
                    _torus_delta(m.arrays.y[alive] - fy, cfg.world_size))
                consumptions += 1
                if int((fd <= 2.0 * cfg.r_eat).sum()) >= 2:
                    crowded += 1
        prev_timer = m.world.food_timer.copy()
        died = prev_alive & ~alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = alive.copy()

    dead = ~m.arrays.alive
    starved = int((dead & (death_energy <= 0.0)).sum())
    return {"telling": telling, "seed": seed,
            "config_hash": cfg.config_hash(), "n": n,
            "mean_nn": nn_sum / max(nn_ticks, 1),
            "consumptions": consumptions, "crowded": crowded,
            "starved": starved}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(t, s) for t in (True, False) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-22.md synchronization addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}
    on = [r for r in rows if r["telling"]]
    off = [r for r in rows if not r["telling"]]

    nn_on = float(np.mean([r["mean_nn"] for r in on]))
    nn_off = float(np.mean([r["mean_nn"] for r in off]))
    c1 = nn_on <= 0.85 * nn_off
    art["C1"] = {"mean_nn_on": nn_on, "mean_nn_off": nn_off,
                 "reduction_pct": 100 * (1 - nn_on / nn_off),
                 "passed": bool(c1)}
    print(f"C1 the crowd: nearest-neighbor {nn_on:.2f} telling vs "
          f"{nn_off:.2f} off ({art['C1']['reduction_pct']:+.1f} pct, "
          f"bar -15): passed {c1}")

    def crowd_rate(rows_):
        return (sum(r["crowded"] for r in rows_)
                / max(sum(r["consumptions"] for r in rows_), 1))

    cr_on, cr_off = crowd_rate(on), crowd_rate(off)
    c2 = cr_off > 0 and cr_on >= 1.5 * cr_off
    art["C2"] = {"crowded_rate_on": cr_on, "crowded_rate_off": cr_off,
                 "ratio": cr_on / max(cr_off, 1e-9), "passed": bool(c2)}
    print(f"C2 packed patches: crowded-consumption {cr_on:.3f} telling "
          f"vs {cr_off:.3f} off (ratio {art['C2']['ratio']:.2f}, bar "
          f"1.5): passed {c2}")

    nn = np.array([r["mean_nn"] for r in on])
    st = np.array([r["starved"] / r["n"] for r in on])
    rho = float(np.corrcoef(nn, st)[0, 1]) if len(on) > 2 else None
    art["C3"] = {"per_seed_corr_nn_starvation": rho}
    print(f"C3 dose link: per-seed corr(nearest-neighbor, starvation) "
          f"= {rho} (no bar; negative means tighter crowds starve "
          f"more)")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-22-sync.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-22-sync-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-22-sync.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-22-sync-replication.json")
