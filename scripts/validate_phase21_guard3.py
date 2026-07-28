"""Phase 21 addendum: the third guard. Artifacts:

  results/phase-21-guard3.json              H2-H4 on seeds 1-24
  results/phase-21-guard3-replication.json  fresh seeds 31-54

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
        "loud": {"wonder_horizon": 100, "wonder_relief": 0.1,
                 "wonder_spread": 1.0}}
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
            "span": [round(float(v), 1) for v in m.arrays.wonder_span[elig]],
            "rim_dist": [round(float(v), 2) for v in rim_dist[elig]],
            "entered_flags": [bool(e) for e in ent[elig]]}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-21.md third-guard addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    off_rows = [r for r in rows if r["arm"] == "off"]
    r_off = (sum(r["entries"] for r in off_rows)
             / max(sum(r["n_eligible"] for r in off_rows), 1))
    loud_rows = [r for r in rows if r["arm"] == "loud"]
    w = np.concatenate([np.array(r["w_onset"]) for r in loud_rows])
    en = np.concatenate([np.array(r["entered_flags"], dtype=bool)
                         for r in loud_rows])
    span = np.concatenate([np.array(r["span"]) for r in loud_rows])
    lo, hi = np.quantile(w, [1 / 3, 2 / 3])
    terc = {}
    for name, mask in (("low", w <= lo), ("mid", (w > lo) & (w <= hi)),
                       ("high", w > hi)):
        terc[name] = {"n": int(mask.sum()),
                      "mean_w": float(w[mask].mean()),
                      "entry_rate": float(en[mask].mean()),
                      "median_span": float(np.median(span[mask]))}
    h2_ratio = terc["high"]["mean_w"] / max(terc["low"]["mean_w"], 1e-9)
    h2 = h2_ratio >= 3.0
    art["H2"] = {"tercile_mean_w": {k: v["mean_w"] for k, v in terc.items()},
                 "ratio": h2_ratio, "passed": bool(h2)}
    print(f"H2 contrast: mean w low {terc['low']['mean_w']:.4f}, high "
          f"{terc['high']['mean_w']:.4f} (ratio {h2_ratio:.1f}, bar 3), "
          f"passed {h2}")
    h3 = terc["low"]["entry_rate"] <= 1.5 * max(r_off, 1e-9)
    art["H3"] = {"low_tercile_rate": terc["low"]["entry_rate"],
                 "off_rate": r_off, "passed": bool(h3)}
    print(f"H3 THE GUARD: low-tercile {terc['low']['entry_rate']:.4f} vs "
          f"off {r_off:.4f} (bar 1.5x = {1.5 * r_off:.4f}), passed {h3}")
    art["H4"] = {k: {"entry_rate": v["entry_rate"],
                     "median_span": v["median_span"]}
                 for k, v in terc.items()}
    print(f"H4 gradient: low {terc['low']['entry_rate']:.3f} (span "
          f"{terc['low']['median_span']:.0f}), mid "
          f"{terc['mid']['entry_rate']:.3f} (span "
          f"{terc['mid']['median_span']:.0f}), high "
          f"{terc['high']['entry_rate']:.3f} (span "
          f"{terc['high']['median_span']:.0f}) (no bar)")
    wr = sum(r["wonder_ruled"] for r in loud_rows)
    wrd = sum(r["wonder_ruled_died"] for r in loud_rows)
    art["pilgrims_this_arena"] = {"wonder_ruled": wr, "died": wrd}
    print(f"pilgrims in the spread arena: {wr} wonder-ruled, {wrd} died "
          f"(claim gated on H3 both stages)")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-21-guard3.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-21-guard3-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-21-guard3.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-21-guard3-replication.json")
