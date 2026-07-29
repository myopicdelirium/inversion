"""Phase 23 addendum: the reckoning at partial spread. Artifacts:

  results/phase-23-partial.json              P1-P3 on seeds 1-24
  results/phase-23-partial-replication.json  fresh seeds 31-54

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
PROPH = {"prophecy_tick": 2000, "prophecy_seed_tick": 1700,
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
    cred_pre = {}
    alive_at_hour = None
    witness = np.zeros(n, dtype=bool)

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
            cred_pre = {li: float(m.social.credence[li, tj])
                        for li, tj in pairs.items()}
        if m.tick == HOUR:
            alive_at_hour = m.arrays.alive.copy()
        if m.tick == HOUR + 50 and arm != "none":
            d = np.hypot(
                _torus_delta(m.arrays.x - site[0], cfg.world_size),
                _torus_delta(m.arrays.y - site[1], cfg.world_size))
            witness = m.arrays.alive & (d <= m.arrays.r_sight)
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = m.arrays.alive.copy()

    if alive_at_hour is None:
        alive_at_hour = prev_alive
    keepers = near_ticks >= VIGIL_TICKS
    dead = ~m.arrays.alive
    starved = dead & (death_energy <= 0.0)
    never_alive = ~ever_believed & alive_at_hour
    wit_deltas, unwit_deltas = [], []
    if m.social is not None:
        for li, tj in pairs.items():
            if li not in cred_pre:
                continue
            delta = float(m.social.credence[li, tj]) - cred_pre[li]
            (wit_deltas if witness[li] else unwit_deltas).append(delta)
    return {"arm": arm, "seed": seed, "config_hash": cfg.config_hash(),
            "n": n,
            "believed_by_hour": int(ever_believed.sum()),
            "alive_at_hour": int(alive_at_hour.sum()),
            "keepers": int(keepers.sum()),
            "keeper_starved": int((keepers & starved).sum()),
            "never_alive_n": int(never_alive.sum()),
            "never_alive_starved": int((never_alive & starved).sum()),
            "wit_deltas": wit_deltas, "unwit_deltas": unwit_deltas}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-23.md partial-spread addendum",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}
    fa = [r for r in rows if r["arm"] == "false"]
    tr = [r for r in rows if r["arm"] == "true"]

    frac = (sum(r["believed_by_hour"] for r in fa)
            / max(sum(r["n"] for r in fa), 1))
    ctrl = sum(r["never_alive_n"] for r in fa)
    p1 = 0.10 <= frac <= 0.40 and ctrl >= 100
    art["P1"] = {"believed_frac": frac, "never_alive_pooled": ctrl,
                 "passed": bool(p1)}
    print(f"P1 partial by construction: believed {frac:.3f} (window "
          f"[0.10, 0.40]), surviving never-believers {ctrl} (floor "
          f"100): passed {p1}")

    def stats(rows_):
        k = sum(r["keepers"] for r in rows_)
        ks = sum(r["keeper_starved"] for r in rows_)
        nn = sum(r["never_alive_n"] for r in rows_)
        ns = sum(r["never_alive_starved"] for r in rows_)
        return k, ks / max(k, 1), ns / max(nn, 1)

    kf, ksr, nsr = stats(fa)
    kt, ktr, ntr = stats(tr)
    p2 = kf >= 30
    art["P2"] = {"keepers_false": kf, "keeper_starved_false": ksr,
                 "never_alive_starved_false": nsr,
                 "excess_false_pts": 100 * (ksr - nsr),
                 "keepers_true": kt, "keeper_starved_true": ktr,
                 "never_alive_starved_true": ntr,
                 "excess_true_pts": 100 * (ktr - ntr),
                 "passed": bool(p2)}
    print(f"P2 corrected Xhosa excess: {kf} keepers (floor 30), "
          f"starved {ksr:.3f} vs surviving never-believers {nsr:.3f} "
          f"(excess {100 * (ksr - nsr):+.1f} pts, unbarred); true arm "
          f"{kt} keepers {ktr:.3f} vs {ntr:.3f} "
          f"({100 * (ktr - ntr):+.1f} pts): passed {p2}")

    wit = [d for r in fa for d in r["wit_deltas"]]
    unwit = [d for r in fa for d in r["unwit_deltas"]]
    wdrop = -float(np.mean(wit)) if wit else None
    udrop = -float(np.mean(unwit)) if unwit else None
    p3 = wdrop is not None and wdrop >= 0.15
    art["P3"] = {"witness_pairs": len(wit), "witness_drop": wdrop,
                 "unwitnessed_pairs": len(unwit),
                 "unwitnessed_drop": udrop, "passed": bool(p3)}
    print(f"P3 the prophet pays at the pairs that settled: witness "
          f"pairs {len(wit)} drop {wdrop} (bar 0.15); unwitnessed "
          f"{len(unwit)} drop {udrop} (no bar): passed {p3}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-23-partial.json")
    elif stage == "tiebreak":
        run_stage(range(61, 85), RESULTS / "phase-23-partial-tiebreak.json")
    elif stage == "replicate":
        run_stage(range(31, 55),
                  RESULTS / "phase-23-partial-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-23-partial.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-23-partial-replication.json")
