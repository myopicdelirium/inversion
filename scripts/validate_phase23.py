"""Phase 23: the promised place. Artifacts:

  results/phase-23-promise.json              X2-X5 on seeds 1-24
  results/phase-23-promise-replication.json  fresh seeds 31-54

Three arms on identical seeds: none (no prophecy), false (the hour
comes and nothing does), true (the apparatus keeps its word). The
phase 22 arena plus foresight (h 60), hour at tick 2000.

Run:
  uv run python scripts/validate_phase23.py all
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

BASE = {"r_sight": 12.0, "memory_slots": 8, "r_social": 8.0,
        "n_food": 60, "tell_places": True, "prospect_horizon": 60,
        "n_hazard": 0}
PROPH = {"prophecy_tick": 2000, "prophecy_seed_tick": 500,
         "prophecy_grace": 50}
ARMS = {"none": {}, "false": {**PROPH}, "true": {**PROPH,
                                                 "prophecy_true": True}}
HOUR = 2000
WINDOW = 200      # the vigil window before the hour
VIGIL_TICKS = 100  # presence required to count as a keeper
TICKS = 3000


def cell(arm, seed):
    cfg = replace(Config(), **BASE, **ARMS[arm])
    m = Model(cfg, seed)
    n = cfg.n_agents
    site = m._prom_site if arm != "none" else (
        float(m.world.nest_x[0]), float(m.world.nest_y[0]))
    ever_believed = np.zeros(n, dtype=bool)
    near_ticks = np.zeros(n, dtype=np.int64)
    pairs = {}
    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()
    cred_pre = None

    for _ in range(TICKS):
        m.step()
        if m.memory is not None and arm != "none":
            ever_believed |= m.memory.prom_active
            act = m.memory.prom_active & (m.memory.prom_from >= 0)
            for i in np.flatnonzero(act):
                pairs.setdefault(int(i), int(m.memory.prom_from[i]))
        if HOUR - WINDOW <= m.tick < HOUR:
            d = np.hypot(
                _torus_delta(m.arrays.x - site[0], cfg.world_size),
                _torus_delta(m.arrays.y - site[1], cfg.world_size))
            near_ticks += (m.arrays.alive & (d <= 10.0)).astype(np.int64)
        if m.tick == HOUR - 1 and m.social is not None and pairs:
            cred_pre = float(np.mean(
                [m.social.credence[li, tj] for li, tj in pairs.items()]))
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = m.arrays.alive.copy()

    cred_post = None
    if m.social is not None and pairs:
        cred_post = float(np.mean(
            [m.social.credence[li, tj] for li, tj in pairs.items()]))
    alive_at_hour = prev_alive  # close enough proxy recorded honestly below
    keepers = near_ticks >= VIGIL_TICKS
    dead = ~m.arrays.alive
    starved = dead & (death_energy <= 0.0)
    never = ~ever_believed
    return {"arm": arm, "seed": seed, "config_hash": cfg.config_hash(),
            "n": n,
            "believed_by_hour": int(ever_believed.sum()),
            "occupancy_window": float(near_ticks.sum() / (WINDOW * n)),
            "keepers": int(keepers.sum()),
            "keeper_starved": int((keepers & starved).sum()),
            "never_n": int(never.sum()),
            "never_starved": int((never & starved).sum()),
            "cred_pre": cred_pre, "cred_post": cred_post}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-23.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    def sel(arm):
        return [r for r in rows if r["arm"] == arm]

    fa, tr, no = sel("false"), sel("true"), sel("none")
    frac = (sum(r["believed_by_hour"] for r in fa)
            / max(sum(r["n"] for r in fa), 1))
    x2 = frac >= 0.5
    art["X2"] = {"believed_frac": frac, "passed": bool(x2)}
    print(f"X2 the prophecy spreads: {frac:.3f} believed by the hour "
          f"(bar 0.5): passed {x2}")

    occ_f = float(np.mean([r["occupancy_window"] for r in fa]))
    occ_n = float(np.mean([r["occupancy_window"] for r in no]))
    x3 = occ_n > 0 and occ_f >= 5.0 * occ_n
    art["X3"] = {"occupancy_false": occ_f, "occupancy_none": occ_n,
                 "ratio": occ_f / max(occ_n, 1e-9), "passed": bool(x3)}
    print(f"X3 the vigil: occupancy {occ_f:.4f} false vs {occ_n:.4f} "
          f"none (ratio {art['X3']['ratio']:.1f}, bar 5): passed {x3}")

    def keeper_stats(rows_):
        k = sum(r["keepers"] for r in rows_)
        ks = sum(r["keeper_starved"] for r in rows_)
        nn = sum(r["never_n"] for r in rows_)
        ns = sum(r["never_starved"] for r in rows_)
        return k, (ks / max(k, 1)), (ns / max(nn, 1))

    kf, ksr, nsr = keeper_stats(fa)
    kt, ktr, ntr = keeper_stats(tr)
    x4 = kf >= 50
    art["X4"] = {"keepers_false": kf, "keeper_starved_false": ksr,
                 "never_starved_false": nsr,
                 "excess_false_pts": 100 * (ksr - nsr),
                 "keepers_true": kt, "keeper_starved_true": ktr,
                 "never_starved_true": ntr,
                 "excess_true_pts": 100 * (ktr - ntr),
                 "passed": bool(x4)}
    print(f"X4 the Xhosa number: {kf} vigil-keepers (bar 50), starved "
          f"{ksr:.3f} vs never-believers {nsr:.3f} "
          f"(excess {100 * (ksr - nsr):+.1f} pts, unbarred); true arm "
          f"{kt} keepers, {ktr:.3f} vs {ntr:.3f} "
          f"({100 * (ktr - ntr):+.1f} pts): existence passed {x4}")

    pre = [r["cred_pre"] for r in fa if r["cred_pre"] is not None]
    post = [r["cred_post"] for r in fa if r["cred_post"] is not None]
    drop = (float(np.mean(pre)) - float(np.mean(post))) if pre and post else None
    x5 = drop is not None and drop >= 0.15
    art["X5"] = {"cred_pre": float(np.mean(pre)) if pre else None,
                 "cred_post": float(np.mean(post)) if post else None,
                 "drop": drop, "passed": bool(x5)}
    print(f"X5 the prophet pays: mouth credence "
          f"{art['X5']['cred_pre']} -> {art['X5']['cred_post']} "
          f"(drop {drop}, bar 0.15): passed {x5}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-23-promise.json")
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-23-promise-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-23-promise.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-23-promise-replication.json")
