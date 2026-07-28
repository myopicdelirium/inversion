"""Phase 21: the quest. Artifacts:

  results/phase-21-quest.json              Q2-Q4 on seeds 1-24
  results/phase-21-quest-replication.json  fresh seeds 31-54

The pull-of-elsewhere arena at phase 20's best-powered coordinates
(bond 0.6, horizon 100, relief per arm), now with directed
exploration. Q1 lives in the golden suite.

Run:
  uv run python scripts/validate_phase21.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.drives import WONDER  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"r_sight": 12.0, "memory_slots": 8, "bond_target": "nest",
         "bond_init": 0.6, "n_nests": 5, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "storm_snare": 0.95, "storm_damage": 0.01,
         "storm_radius": 15.0}
ARMS = {"off": {"wonder_horizon": 0},
        "quiet": {"wonder_horizon": 100, "wonder_relief": 0.01},
        "loud": {"wonder_horizon": 100, "wonder_relief": 0.1}}
ONSET = 2000
TICKS = 3500


def cell(arm, seed):
    cfg = replace(Config(), **ARENA, **ARMS[arm])
    m = Model(cfg, seed)
    n = cfg.n_agents
    nonlocal_mask = (np.arange(n) % cfg.n_nests) != 0
    sx, sy = m.world.storm_x, m.world.storm_y

    def inside():
        return (np.hypot(_torus_delta(m.arrays.x - sx, cfg.world_size),
                         _torus_delta(m.arrays.y - sy, cfg.world_size))
                < cfg.storm_radius)

    for _ in range(ONSET):
        m.step()
    at_onset_alive = m.arrays.alive.copy()
    was_inside = inside()
    if m.memory is not None and cfg.wonder_horizon > 0:
        stale_onset = np.clip(
            (m.tick - m.memory.mem_last_novel) / cfg.wonder_horizon,
            0.0, 1.0)
    else:
        stale_onset = np.zeros(n)

    entered = np.zeros(n, dtype=bool)
    entry_energy = np.full(n, np.nan)
    entry_wonder_ruled = np.zeros(n, dtype=bool)
    for _ in range(TICKS - ONSET):
        m.step()
        now = inside()
        crossing = m.arrays.alive & now & ~was_inside & ~entered
        if crossing.any():
            entered[crossing] = True
            entry_energy[crossing] = m.arrays.energy[crossing]
            ruled = (m.arrays.weights[crossing].argmax(axis=1) == WONDER)
            entry_wonder_ruled[crossing] = ruled
        was_inside = now
    died = at_onset_alive & ~m.arrays.alive

    elig = nonlocal_mask & at_onset_alive
    ent = entered & elig
    wr = ent & entry_wonder_ruled & (entry_energy > 0.7)
    return {"arm": arm, "seed": seed, "config_hash": cfg.config_hash(),
            "n_eligible": int(elig.sum()),
            "entries": int(ent.sum()),
            "wonder_ruled": int(wr.sum()),
            "wonder_ruled_died": int((wr & died).sum()),
            "stale_onset": [round(float(s), 4) for s in stale_onset[elig]],
            "entered_flags": [bool(e) for e in ent[elig]]}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-21.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    def pooled(arm, field):
        sel = [r for r in rows if r["arm"] == arm]
        return sum(r[field] for r in sel), sum(r["n_eligible"] for r in sel)

    rates = {}
    for arm in ARMS:
        e, n = pooled(arm, "entries")
        rates[arm] = e / max(n, 1)
    art["Q4"] = {f"entry_rate_{a}": rates[a] for a in ARMS}
    print(f"Q4 entry rates: off {rates['off']:.4f}, quiet "
          f"{rates['quiet']:.4f}, loud {rates['loud']:.4f} (no bar)")

    wr_loud, _ = pooled("loud", "wonder_ruled")
    wr_off, _ = pooled("off", "wonder_ruled")
    wr_died, _ = pooled("loud", "wonder_ruled_died")
    q2 = wr_loud >= 50 and wr_loud >= 5 * max(wr_off, 1)
    art["Q2"] = {"wonder_ruled_loud": wr_loud, "wonder_ruled_off": wr_off,
                 "pilgrim_deaths_loud": wr_died,
                 "pilgrim_mortality": wr_died / max(wr_loud, 1),
                 "passed": bool(q2)}
    print(f"Q2 pilgrims: loud {wr_loud} (off {wr_off}), died {wr_died} "
          f"({art['Q2']['pilgrim_mortality']:.3f}), passed {q2}")

    loud_rows = [r for r in rows if r["arm"] == "loud"]
    st = np.concatenate([np.array(r["stale_onset"]) for r in loud_rows])
    en = np.concatenate([np.array(r["entered_flags"], dtype=bool)
                         for r in loud_rows])
    cut = np.quantile(st, 1 / 3)
    calm = st <= cut
    calm_rate = float(en[calm].mean()) if calm.any() else None
    q3 = calm_rate is not None and calm_rate <= 1.5 * max(rates["off"], 1e-9)
    art["Q3"] = {"calm_tercile_rate": calm_rate,
                 "off_rate": rates["off"], "cut": float(cut),
                 "n_calm": int(calm.sum()), "passed": bool(q3)}
    print(f"Q3 invariant guard: calm-tercile rate {calm_rate} vs off "
          f"{rates['off']:.4f} (bar 1.5x), passed {q3}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-21-quest.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-21-quest-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-21-quest.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-21-quest-replication.json")
