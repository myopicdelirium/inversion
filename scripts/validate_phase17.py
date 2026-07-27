"""Phase 17: the world you know. Artifacts:

  results/phase-17-private-world.json              V2-V4 on seeds 1-24
  results/phase-17-private-world-replication.json  fresh seeds 31-54

V1 (inertness) lives in the golden suite. V2: the private world
exists (knownness and overlap, default world, tick 2000). V3: memory
must earn its existence (famine arena, n_food 60). V4: depth shapes
the aggregate (spread vs no-spread at matched median sight 12).

Run:
  uv run python scripts/validate_phase17.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model, run  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

V3_SIGHTS = (0.0, 24.0, 12.0, 6.0)


def v2_cell(seed):
    cfg = replace(Config(), r_sight=12.0, memory_slots=8)
    m = Model(cfg, seed)
    for _ in range(2000):
        m.step()
    active = m.world.food_timer == 0
    fx, fy = m.world.food_x[active], m.world.food_y[active]
    n_active = int(active.sum())
    tree = cKDTree(np.column_stack([fx, fy]), boxsize=cfg.world_size)
    alive = np.flatnonzero(m.arrays.alive)

    known_fracs = []
    mem_sets = []
    for i in alive:
        dx = _torus_delta(fx - m.arrays.x[i], cfg.world_size)
        dy = _torus_delta(fy - m.arrays.y[i], cfg.world_size)
        visible = set(np.flatnonzero(np.hypot(dx, dy) <= m.arrays.r_sight[i]))
        valid = m.memory.mem_seen[i] >= 0
        remembered = set()
        if valid.any():
            pts = np.column_stack([m.memory.mem_x[i][valid] % cfg.world_size,
                                   m.memory.mem_y[i][valid] % cfg.world_size])
            d, idx = tree.query(pts)
            remembered = set(idx[d <= cfg.r_eat])
        known_fracs.append(len(visible | remembered) / max(n_active, 1))
        mem_sets.append(remembered)

    jac = []
    for a in range(len(mem_sets)):
        for b in range(a + 1, len(mem_sets)):
            union = mem_sets[a] | mem_sets[b]
            if union:
                jac.append(len(mem_sets[a] & mem_sets[b]) / len(union))
    return {"seed": seed, "config_hash": cfg.config_hash(),
            "mean_knownness": float(np.mean(known_fracs)),
            "mean_jaccard": float(np.mean(jac)) if jac else None,
            "jaccard_pairs": len(jac)}


def v3_cell(r_sight, slots, seed):
    kw = {"n_food": 60}
    if r_sight > 0:
        kw.update(r_sight=r_sight, memory_slots=slots)
    cfg = replace(Config(), **kw)
    traj = run(cfg, seed=seed, ticks=3000)
    alive = traj["alive"][-1]
    starved = (~alive) & (traj["energy"][-1] <= 0.0)
    return {"r_sight": r_sight, "slots": slots, "seed": seed,
            "config_hash": cfg.config_hash(), "n": cfg.n_agents,
            "starved": int(starved.sum())}


def v4_cell(spread, seed):
    cfg = replace(Config(), n_food=60, r_sight=12.0, memory_slots=8,
                  r_sight_spread=spread)
    m = Model(cfg, seed)
    intake = np.zeros(cfg.n_agents)
    death_energy = np.full(cfg.n_agents, np.nan)
    prev_e = m.arrays.energy.copy()
    prev_alive = m.arrays.alive.copy()
    for _ in range(3000):
        m.step()
        gained = np.clip(m.arrays.energy - prev_e, 0.0, None)
        intake += np.where(prev_alive, gained, 0.0)
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_e = m.arrays.energy.copy()
        prev_alive = m.arrays.alive.copy()
    starved = (~m.arrays.alive) & (death_energy <= 0.0)
    return {"spread": spread, "seed": seed,
            "config_hash": cfg.config_hash(), "n": cfg.n_agents,
            "starved": int(starved.sum()),
            "r_sight_i": [round(float(v), 4) for v in m.arrays.r_sight],
            "intake": [round(float(v), 4) for v in intake]}


def _cell(args):
    kind = args[0]
    if kind == "v2":
        return {"kind": "v2", **v2_cell(args[1])}
    if kind == "v3":
        return {"kind": "v3", **v3_cell(args[1], args[2], args[3])}
    return {"kind": "v4", **v4_cell(args[1], args[2])}


def run_stage(seeds, out_path):
    jobs = [("v2", s) for s in seeds]
    jobs += [("v3", rs, 8, s) for rs in V3_SIGHTS for s in seeds]
    jobs += [("v3", 12.0, 0, s) for s in seeds]
    jobs += [("v4", sp, s) for sp in (0.5, 0.0) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-17.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    v2 = [r for r in rows if r["kind"] == "v2"]
    know = float(np.mean([r["mean_knownness"] for r in v2]))
    jacs = [r["mean_jaccard"] for r in v2 if r["mean_jaccard"] is not None]
    jac = float(np.mean(jacs)) if jacs else None
    art["V2"] = {"mean_knownness": know, "mean_jaccard": jac,
                 "passed": bool(know < 0.2 and jac is not None and jac < 0.3)}
    print(f"V2 private world: knownness {know:.3f}, jaccard {jac}, "
          f"passed {art['V2']['passed']}")

    def v3_rate(rs, slots):
        sel = [r for r in rows if r["kind"] == "v3"
               and r["r_sight"] == rs and r["slots"] == slots]
        return sum(r["starved"] for r in sel) / sum(r["n"] for r in sel)

    rates_on = {rs: v3_rate(rs, 8) for rs in V3_SIGHTS}
    off12 = v3_rate(12.0, 0)
    mono = (rates_on[0.0] <= rates_on[24.0] <= rates_on[12.0]
            <= rates_on[6.0])
    dividend = (off12 - rates_on[12.0]) / max(off12, 1e-9)
    art["V3"] = {"starvation_by_sight_memory_on": {str(k): v for k, v in rates_on.items()},
                 "starvation_sight12_memoryless": off12,
                 "monotone": bool(mono),
                 "memory_dividend": dividend,
                 "passed": bool(mono and dividend >= 0.25)}
    print(f"V3 cost of blindness (memory on): "
          f"{[round(rates_on[k], 3) for k in V3_SIGHTS]}, memoryless at 12: "
          f"{off12:.3f}, dividend {100 * dividend:+.1f} pct, "
          f"passed {art['V3']['passed']}")

    v4s = [r for r in rows if r["kind"] == "v4" and r["spread"] == 0.5]
    v4n = [r for r in rows if r["kind"] == "v4" and r["spread"] == 0.0]
    sight = np.concatenate([np.array(r["r_sight_i"]) for r in v4s])
    intake = np.concatenate([np.array(r["intake"]) for r in v4s])
    rho = float(spearmanr(sight, intake).statistic)
    rate_sp = sum(r["starved"] for r in v4s) / sum(r["n"] for r in v4s)
    rate_ns = sum(r["starved"] for r in v4n) / sum(r["n"] for r in v4n)
    art["V4"] = {"spearman_rho": rho,
                 "starvation_spread": rate_sp,
                 "starvation_nospread": rate_ns,
                 "gap_points": 100 * (rate_sp - rate_ns),
                 "passed": bool(rho >= 0.3
                                and abs(rate_sp - rate_ns) >= 0.05)}
    print(f"V4 depth shapes the aggregate: rho {rho:.3f}, starvation "
          f"spread {rate_sp:.3f} vs equal {rate_ns:.3f} "
          f"(gap {art['V4']['gap_points']:+.1f} pts), passed {art['V4']['passed']}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-17-private-world.json")
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-17-private-world-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-17-private-world.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-17-private-world-replication.json")
