"""Phase 15 addendum 3: grief geometry. Artifacts:

  results/phase-15-geometry.json              G0-G2 on seeds 1-24
  results/phase-15-geometry-replication.json  fresh seeds 31-54

The arms are byte-identical reruns of the distant-death cells with one
live measurement added: each new mourner's distance to the nearest
active food source at the moment of loss, then whether they starved.

Run:
  uv run python scripts/validate_phase15_geometry.py main
  uv run python scripts/validate_phase15_geometry.py replicate
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
from core.world import perceive_food  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

DISTANT = {"bond_target": "leader", "n_leaders": 10, "n_agents": 400,
           "n_hazard": 0, "storm_nest": 0, "storm_onset": 2000,
           "storm_ramp": 1, "storm_snare": 0.95, "storm_damage": 0.01,
           "n_food": 40, "attention_floor": 0.01}


def geometry_cell(mode, seed):
    arena = dict(DISTANT)
    arena["bond_target"] = mode
    if mode == "partner":
        arena["n_leaders"] = 1
    cfg = replace(Config(), **arena, bond_init=0.8, attention_sharpness=2.0)
    m = Model(cfg, seed)
    n = cfg.n_agents
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)

    loss_tick = np.full(n, -1, dtype=np.int64)
    loss_dist = np.full(n, np.nan)
    death_tick = np.full(n, -1, dtype=np.int64)
    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()

    for _ in range(3500):
        m.step()
        alive = m.arrays.alive
        died_now = prev_alive & ~alive
        if died_now.any():
            death_tick[died_now] = m.tick
            death_energy[died_now] = m.arrays.energy[died_now]
            target_died = has & died_now[pidx] & alive & (loss_tick < 0)
            if target_died.any():
                dist_food, _, _, _ = perceive_food(m.arrays, m.world, cfg)
                loss_tick[target_died] = m.tick
                loss_dist[target_died] = dist_food[target_died]
        prev_alive = alive.copy()

    bereaved = loss_tick >= 0
    starved = bereaved & (death_tick >= loss_tick) & (death_energy <= 0.0)
    return {"mode": mode, "seed": seed, "config_hash": cfg.config_hash(),
            "bereaved": int(bereaved.sum()),
            "loss_dist": [round(float(d), 4) for d in loss_dist[bereaved]],
            "starved": [bool(s) for s in starved[bereaved]]}


def _cell(args):
    return geometry_cell(args[0], args[1])


def tercile_rates(dists, starved):
    lo, hi = np.quantile(dists, [1 / 3, 2 / 3])
    out = {}
    for name, mask in (("near", dists <= lo),
                       ("mid", (dists > lo) & (dists <= hi)),
                       ("far", dists > hi)):
        out[name] = {"n": int(mask.sum()),
                     "rate": float(starved[mask].mean()) if mask.any() else None}
    return out, float(lo), float(hi)


def run_stage(seeds, out_path):
    jobs = [(m, s) for m in ("leader", "partner") for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-15.md addendum 3",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    pooled = {}
    for m in ("leader", "partner"):
        d = np.concatenate([np.array(r["loss_dist"]) for r in rows
                            if r["mode"] == m and r["bereaved"] > 0] or [np.array([])])
        s = np.concatenate([np.array(r["starved"], dtype=bool) for r in rows
                            if r["mode"] == m and r["bereaved"] > 0] or [np.array([], dtype=bool)])
        pooled[m] = (d, s)
        art[m] = {"bereaved": int(d.size),
                  "median_loss_dist": float(np.median(d)) if d.size else None,
                  "neglect_rate": float(s.mean()) if d.size else None}
        print(f"{m}: bereaved {d.size}, median loss-dist "
              f"{art[m]['median_loss_dist']}, neglect {art[m]['neglect_rate']}")

    g0 = (art["leader"]["median_loss_dist"] is not None
          and art["partner"]["median_loss_dist"] is not None
          and art["leader"]["median_loss_dist"] < art["partner"]["median_loss_dist"])
    art["G0"] = {"passed": bool(g0)}
    print(f"G0 manipulation check (leader median < partner median): {g0}")

    pd, ps = pooled["partner"]
    terc, lo, hi = tercile_rates(pd, ps)
    near, far = terc["near"]["rate"], terc["far"]["rate"]
    g1 = far is not None and near is not None and far >= 2.0 * max(near, 1e-9)
    art["G1"] = {"terciles": terc, "cut_lo": lo, "cut_hi": hi,
                 "ratio": (far / max(near, 1e-9)) if far is not None else None,
                 "passed": bool(g1)}
    print(f"G1 partner terciles: near {near} (n {terc['near']['n']}), "
          f"mid {terc['mid']['rate']}, far {far} (n {terc['far']['n']}): {g1}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)
    return pooled


def judge_g2(pool_main, pool_rep):
    both = {}
    for m in ("leader", "partner"):
        d = np.concatenate([pool_main[m][0], pool_rep[m][0]])
        s = np.concatenate([pool_main[m][1], pool_rep[m][1]])
        both[m] = (d, s)
    alld = np.concatenate([both["leader"][0], both["partner"][0]])
    lo = float(np.quantile(alld, 1 / 3))
    rates = {}
    for m in ("leader", "partner"):
        d, s = both[m]
        near = d <= lo
        rates[m] = {"n_near": int(near.sum()),
                    "near_rate": float(s[near].mean()) if near.any() else None,
                    "uncond_rate": float(s.mean())}
    uncond_gap = rates["partner"]["uncond_rate"] - rates["leader"]["uncond_rate"]
    near_gap = (rates["partner"]["near_rate"] - rates["leader"]["near_rate"]
                if None not in (rates["partner"]["near_rate"],
                                rates["leader"]["near_rate"]) else None)
    g2 = near_gap is not None and abs(near_gap) <= 0.5 * abs(uncond_gap)
    art = {"spec": "specs/phase-15.md addendum 3", "cut_near": lo,
           "rates": rates, "uncond_gap_points": 100 * uncond_gap,
           "near_gap_points": 100 * near_gap if near_gap is not None else None,
           "passed": bool(g2)}
    print(f"G2 mediation: unconditioned gap {100 * uncond_gap:+.1f} pts, "
          f"near-food gap {art['near_gap_points']} pts "
          f"(leader n_near {rates['leader']['n_near']}): {g2}")
    (RESULTS / "phase-15-geometry-g2.json").write_text(
        json.dumps(art, indent=2) + "\n")
    print("written phase-15-geometry-g2.json")


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-15-geometry.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-15-geometry-replication.json")
    else:
        pm = run_stage(range(1, 25), RESULTS / "phase-15-geometry.json")
        pr = run_stage(range(31, 55),
                       RESULTS / "phase-15-geometry-replication.json")
        judge_g2(pm, pr)
