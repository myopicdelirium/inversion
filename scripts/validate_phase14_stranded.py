"""Phase 14 addendum: stranded pairs. CLOSED AT DESIGN STAGE, never run:
see the closure record in specs/phase-14.md. Kept as the record of what
was designed. Original header follows.

Artifacts (never produced):

  results/phase-14-stranded.json              S1-S3 on seeds 1-24
  results/phase-14-stranded-replication.json  fresh seeds 31-54

The W-arena verbatim plus n_food 40 (the scarcity separator validated
by the distant-death protocol), care fixed at 1.0. Stranded cohort at
tick 2050: caught, partner alive outside beyond r_help.

Run:
  uv run python scripts/validate_phase14_stranded.py all
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
from core.world import _torus_delta, perceive_partner  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "storm_snare": 0.95, "storm_damage": 0.01, "tau_safety": 12.0,
         "prospect_horizon": 60, "prospect_sees_grip": True,
         "n_food": 40}

HELPS = (0.0, 0.5, 1.0)


def cell_run(args):
    helps, seed = args
    cfg = replace(Config(), **ARENA, care=1.0, help_strength=helps)
    m = Model(cfg, seed)
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
    d_partner, _, _ = perceive_partner(m.arrays, cfg)
    stranded = (m.arrays.alive & inside & has & m.arrays.alive[pidx]
                & ~inside[pidx] & (d_partner > cfg.r_help))
    rescuers = np.zeros(cfg.n_agents, dtype=bool)
    rescuers[pidx[stranded]] = True

    for _ in range(1200):
        m.step()

    now_inside = storm_dist() < cfg.storm_radius
    extracted = stranded & m.arrays.alive & ~now_inside
    return {"help": helps, "seed": seed, "config_hash": cfg.config_hash(),
            "n_stranded": int(stranded.sum()),
            "extracted": int(extracted.sum()),
            "stranded_alive_end": int((stranded & m.arrays.alive).sum()),
            "n_rescuers": int(rescuers.sum()),
            "rescuer_deaths": int((rescuers & ~m.arrays.alive).sum())}


def _cell(args):
    return cell_run(args)


def run_stage(seeds, out_path):
    jobs = [(hs, sd) for hs in HELPS for sd in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-14.md stranded-pairs addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows, "cells": {}}
    ext = {}
    for hs in HELPS:
        sel = [r for r in rows if r["help"] == hs]
        ns = sum(r["n_stranded"] for r in sel)
        ex = sum(r["extracted"] for r in sel)
        nr = sum(r["n_rescuers"] for r in sel)
        rd = sum(r["rescuer_deaths"] for r in sel)
        cell = {"n_stranded": ns, "extraction": ex / max(ns, 1),
                "stranded_alive_end": sum(r["stranded_alive_end"] for r in sel) / max(ns, 1),
                "rescuer_mortality": rd / max(nr, 1), "n_rescuers": nr}
        art["cells"][str(hs)] = cell
        ext[hs] = cell["extraction"]
        print(f"help {hs}: stranded {ns}, extraction {cell['extraction']:.3f}, "
              f"rescuer mortality {cell['rescuer_mortality']:.3f} (n {nr})")
    s1 = all(art["cells"][str(hs)]["n_stranded"] >= 100 for hs in HELPS)
    art["S1"] = {"passed": bool(s1)}
    s2 = (ext[0.5] >= ext[0.0] and ext[1.0] >= ext[0.5]
          and ext[1.0] - ext[0.0] >= 0.10)
    art["S2"] = {"extraction_by_help": {str(h): ext[h] for h in HELPS},
                 "top_minus_bottom": ext[1.0] - ext[0.0], "passed": bool(s2)}
    print(f"S1 power (all cells >= 100): {s1} | S2 monotone with "
          f"top-bottom {100 * (ext[1.0] - ext[0.0]):+.1f} pts: {s2}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-14-stranded.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-14-stranded-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-14-stranded.json")
        run_stage(range(31, 55), RESULTS / "phase-14-stranded-replication.json")
