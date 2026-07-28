"""Phase 19: wonder. Artifacts:

  results/phase-19-wonder.json              N2-N3 on seeds 1-24
  results/phase-19-wonder-replication.json  fresh seeds 31-54

N1a/N1b live in the golden suite and tests/test_wonder.py. N2: the
drive must move behavior (lifetime discoveries up at least 25 percent
with wonder on, hazardless sighted world). N3: curiosity's price
(default hazards restored, mortality and starvation on vs off,
reported with sign, no desired direction).

Run:
  uv run python scripts/validate_phase19.py all
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

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SIGHTED = {"r_sight": 12.0, "memory_slots": 8, "wonder_relief": 0.01}
TICKS = 3000


def cell(kind, horizon, seed):
    arena = dict(SIGHTED, wonder_horizon=horizon)
    if kind == "calm":
        arena["n_hazard"] = 0
    cfg = replace(Config(), **arena)
    m = Model(cfg, seed)
    n = cfg.n_agents
    novel = np.zeros(n, dtype=np.int64)
    death_energy = np.full(n, np.nan)
    prev_novel = m.memory.mem_last_novel.copy()
    prev_alive = m.arrays.alive.copy()
    for _ in range(TICKS):
        m.step()
        novel += (m.memory.mem_last_novel != prev_novel)
        prev_novel = m.memory.mem_last_novel.copy()
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = m.arrays.alive.copy()
    dead = ~m.arrays.alive
    return {"kind": kind, "horizon": horizon, "seed": seed,
            "config_hash": cfg.config_hash(), "n": n,
            "discoveries": int(novel.sum()),
            "deaths": int(dead.sum()),
            "starved": int((dead & (death_energy <= 0.0)).sum())}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(k, h, s) for k in ("calm", "hazard") for h in (400, 0)
            for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-19.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    def pool_stat(kind, horizon, field):
        sel = [r for r in rows if r["kind"] == kind
               and r["horizon"] == horizon]
        return sum(r[field] for r in sel), sum(r["n"] for r in sel)

    d_on, _ = pool_stat("calm", 400, "discoveries")
    d_off, _ = pool_stat("calm", 0, "discoveries")
    n2 = d_off > 0 and d_on >= 1.25 * d_off
    art["N2"] = {"discoveries_on": d_on, "discoveries_off": d_off,
                 "ratio": d_on / max(d_off, 1), "passed": bool(n2)}
    print(f"N2 discovery: on {d_on} vs off {d_off} "
          f"(ratio {art['N2']['ratio']:.2f}), passed {n2}")

    n3 = {}
    for field in ("deaths", "starved"):
        on, tot = pool_stat("hazard", 400, field)
        off, _ = pool_stat("hazard", 0, field)
        n3[field] = {"on": on / tot, "off": off / tot,
                     "gap_points": 100 * (on - off) / tot}
        print(f"N3 {field}: on {n3[field]['on']:.3f} vs off "
              f"{n3[field]['off']:.3f} (gap {n3[field]['gap_points']:+.1f} "
              f"pts, no bar)")
    art["N3"] = n3
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-19-wonder.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-19-wonder-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-19-wonder.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-19-wonder-replication.json")
