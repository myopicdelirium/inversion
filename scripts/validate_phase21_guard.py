"""Phase 21 addendum: the second guard. Artifacts:

  results/phase-21-guard.json              G1-G4 on seeds 1-24
  results/phase-21-guard-replication.json  fresh seeds 31-54

Off and loud arms are byte-identical reruns of the phase 21 cells
with the disposition measured as w_wonder at onset; the amputated arm
is loud until onset, then wonder's pricing is cut by the instrument
(relief zero; histories, weights, positions untouched; no draws
consumed by the cut).

Run:
  uv run python scripts/validate_phase21_guard.py all
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
        "loud": {"wonder_horizon": 100, "wonder_relief": 0.1},
        "amputated": {"wonder_horizon": 100, "wonder_relief": 0.1}}
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
    w_onset = m.arrays.weights[:, WONDER].copy()
    rim_dist = np.maximum(
        np.hypot(_torus_delta(m.arrays.x - sx, cfg.world_size),
                 _torus_delta(m.arrays.y - sy, cfg.world_size))
        - cfg.storm_radius, 0.0)
    if arm == "amputated":
        # The surgical cut (spec addendum G4): pricing dies, nothing
        # else changes. Config is state the instrument may replace;
        # no core code path and no RNG stream is touched.
        m.config = replace(cfg, wonder_relief=0.0)

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
            "w_onset": [round(float(v), 5) for v in w_onset[elig]],
            "rim_dist": [round(float(v), 2) for v in rim_dist[elig]],
            "entered_flags": [bool(e) for e in ent[elig]]}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-21.md second-guard addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    def rate(arm):
        sel = [r for r in rows if r["arm"] == arm]
        return (sum(r["entries"] for r in sel)
                / max(sum(r["n_eligible"] for r in sel), 1))

    r_off, r_loud, r_amp = rate("off"), rate("loud"), rate("amputated")

    loud_rows = [r for r in rows if r["arm"] == "loud"]
    w = np.concatenate([np.array(r["w_onset"]) for r in loud_rows])
    en = np.concatenate([np.array(r["entered_flags"], dtype=bool)
                         for r in loud_rows])
    rim = np.concatenate([np.array(r["rim_dist"]) for r in loud_rows])
    lo, hi = np.quantile(w, [1 / 3, 2 / 3])
    terc = {}
    for name, mask in (("low", w <= lo), ("mid", (w > lo) & (w <= hi)),
                       ("high", w > hi)):
        terc[name] = {"n": int(mask.sum()),
                      "entry_rate": float(en[mask].mean()),
                      "median_rim_dist": float(np.median(rim[mask]))}
    g1 = terc["low"]["entry_rate"] <= 1.5 * max(r_off, 1e-9)
    art["G1"] = {"low_tercile_rate": terc["low"]["entry_rate"],
                 "off_rate": r_off, "cut_lo": float(lo),
                 "passed": bool(g1)}
    art["G2"] = {k: v["entry_rate"] for k, v in terc.items()}
    art["G3"] = {k: v["median_rim_dist"] for k, v in terc.items()}
    print(f"G1 guard (w_wonder disposition): low-tercile "
          f"{terc['low']['entry_rate']:.4f} vs off {r_off:.4f} "
          f"(bar 1.5x), passed {g1}")
    print(f"G2 gradient: low {terc['low']['entry_rate']:.3f}, mid "
          f"{terc['mid']['entry_rate']:.3f}, high "
          f"{terc['high']['entry_rate']:.3f} (no bar)")
    print(f"G3 rim distance at onset: low {terc['low']['median_rim_dist']:.1f}, "
          f"mid {terc['mid']['median_rim_dist']:.1f}, high "
          f"{terc['high']['median_rim_dist']:.1f} (no bar)")

    excess_loud = r_loud - r_off
    removed = (r_loud - r_amp) / max(excess_loud, 1e-9)
    g4 = excess_loud > 0 and removed >= 0.5
    art["G4"] = {"entry_rate_off": r_off, "entry_rate_loud": r_loud,
                 "entry_rate_amputated": r_amp,
                 "excess_removed_frac": removed, "passed": bool(g4)}
    print(f"G4 amputation: off {r_off:.4f}, loud {r_loud:.4f}, amputated "
          f"{r_amp:.4f}: cut removed {100 * removed:.0f} pct of the "
          f"excess, passed {g4}")

    wr_loud = sum(r["wonder_ruled"] for r in loud_rows)
    wr_died = sum(r["wonder_ruled_died"] for r in loud_rows)
    art["Q2_rejudgment"] = {"gate_G1": bool(g1),
                            "wonder_ruled_loud": wr_loud,
                            "pilgrim_deaths": wr_died,
                            "claimed": bool(g1)}
    print(f"Q2 re-judgment: gate {'HOLDS: pilgrims claimed' if g1 else 'FAILS: pilgrims remain unclaimed'} "
          f"({wr_loud} wonder-ruled, {wr_died} deaths this rerun)")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-21-guard.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-21-guard-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-21-guard.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-21-guard-replication.json")
