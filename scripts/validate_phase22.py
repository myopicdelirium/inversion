"""Phase 22: the told place. Artifacts:

  results/phase-22-told.json              B2-B4 on seeds 1-24
  results/phase-22-told-replication.json  fresh seeds 31-54

B1 lives in the golden suite. Settlements are reconstructed from
per-tick snapshots of the told/source state (the model drains its
own events), which is deterministic and touches no core code:
a told slot that becomes owned at the same coordinates settled TRUE;
a told slot that vanishes while in sight of its holder settled
FALSE; eviction and expiry are neither.

Run:
  uv run python scripts/validate_phase22.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.world import _torus_delta  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"r_sight": 12.0, "memory_slots": 8, "r_social": 8.0,
         "n_food": 60, "testimony": 0.0}
TICKS = 3000


def cell(telling, seed):
    cfg = replace(Config(), **ARENA, tell_places=telling)
    m = Model(cfg, seed)
    n = cfg.n_agents
    k = cfg.memory_slots
    prev_told = np.zeros((n, k), dtype=bool)
    prev_src = np.full((n, k), -1, dtype=np.int64)
    prev_seen = np.full((n, k), -1, dtype=np.int64)
    prev_x = np.zeros((n, k))
    prev_y = np.zeros((n, k))
    death_energy = np.full(n, np.nan)
    prev_alive = m.arrays.alive.copy()

    told_created = 0
    own_created = 0
    told_true = 0
    told_false = 0
    own_false = 0
    true_pairs = set()
    false_pairs = set()

    for _ in range(TICKS):
        m.step()
        mem = m.memory
        # Settlement classification against last tick's told state.
        was_told = prev_told
        now_told = mem.mem_told
        now_valid = mem.mem_seen >= 0
        # The seen stamp written this tick carries the PRE-increment
        # tick number, which is m.tick - 1 after step() returns.
        stamp = mem.mem_seen == m.tick - 1
        near_prev = np.hypot(
            _torus_delta(mem.mem_x - prev_x, cfg.world_size),
            _torus_delta(mem.mem_y - prev_y, cfg.world_size)
        ) <= cfg.r_eat
        # TRUE settlement: the told slot was confirmed IN PLACE (the
        # conversion rewrites coordinates by at most r_eat); a distant
        # rewrite is an eviction-overwrite, settled nothing.
        confirmed = was_told & now_valid & ~now_told & stamp & near_prev
        vanished = was_told & ~now_valid
        aged_out = vanished & (m.tick - 1 - prev_seen
                               > cfg.memory_horizon)
        disappointed = vanished & ~aged_out
        for li, sj in zip(*np.nonzero(confirmed)):
            told_true += 1
            true_pairs.add((int(li), int(prev_src[li, sj])))
        for li, sj in zip(*np.nonzero(disappointed)):
            told_false += 1
            false_pairs.add((int(li), int(prev_src[li, sj])))
        # Creation accounting.
        newly_told = now_told & ~was_told
        told_created += int(newly_told.sum())
        # An own creation fills an empty slot or overwrites a distant
        # one; an in-place restamp of an existing own slot is a
        # refresh, not a creation, and must not dilute B3's
        # denominator.
        newly_own = (now_valid & ~now_told & stamp
                     & ((prev_seen < 0) | (~near_prev & ~was_told)))
        own_created += int(newly_own.sum())
        # Owned disappointment: slot was valid own last tick, empty now.
        own_vanished = (~was_told & (prev_seen >= 0) & ~now_valid)
        own_aged = own_vanished & (m.tick - 1 - prev_seen
                                   > cfg.memory_horizon)
        own_false += int((own_vanished & ~own_aged).sum())

        prev_told = now_told.copy()
        prev_src = mem.mem_source.copy()
        prev_seen = mem.mem_seen.copy()
        prev_x = mem.mem_x.copy()
        prev_y = mem.mem_y.copy()
        died = prev_alive & ~m.arrays.alive
        death_energy[died] = m.arrays.energy[died]
        prev_alive = m.arrays.alive.copy()

    dead = ~m.arrays.alive
    starved = int((dead & (death_energy <= 0.0)).sum())
    cred_true = [float(m.social.credence[li, tj])
                 for (li, tj) in true_pairs]
    cred_false = [float(m.social.credence[li, tj])
                  for (li, tj) in false_pairs - true_pairs]
    return {"telling": telling, "seed": seed,
            "config_hash": cfg.config_hash(), "n": n,
            "starved": starved, "told_created": told_created,
            "own_created": own_created, "told_true": told_true,
            "told_false": told_false, "own_false": own_false,
            "cred_true": cred_true, "cred_false": cred_false}


def _cell(args):
    return cell(*args)


def run_stage(seeds, out_path):
    jobs = [(t, s) for t in (True, False) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-22.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}
    on = [r for r in rows if r["telling"]]
    off = [r for r in rows if not r["telling"]]

    tt = sum(r["told_true"] for r in on)
    starv_on = sum(r["starved"] for r in on) / sum(r["n"] for r in on)
    starv_off = sum(r["starved"] for r in off) / sum(r["n"] for r in off)
    b2 = tt >= 500 and (starv_off - starv_on) >= 0.03
    art["B2"] = {"told_true": tt, "starved_on": starv_on,
                 "starved_off": starv_off,
                 "saved_points": 100 * (starv_off - starv_on),
                 "passed": bool(b2)}
    print(f"B2 rumors nourish: {tt} true settlements; starvation on "
          f"{starv_on:.3f} vs off {starv_off:.3f} "
          f"(saved {100 * (starv_off - starv_on):+.1f} pts, bars "
          f"500/3): passed {b2}")

    tc = sum(r["told_created"] for r in on)
    tf = sum(r["told_false"] for r in on)
    oc = sum(r["own_created"] for r in on)
    of_ = sum(r["own_false"] for r in on)
    rate_told = tf / max(tc, 1)
    rate_own = of_ / max(oc, 1)
    b3 = rate_own > 0 and rate_told >= 1.5 * rate_own
    art["B3"] = {"told_disappoint_rate": rate_told,
                 "own_disappoint_rate": rate_own,
                 "ratio": rate_told / max(rate_own, 1e-9),
                 "told_created": tc, "own_created": oc,
                 "passed": bool(b3)}
    print(f"B3 secondhand ages worse: told {rate_told:.3f} "
          f"({tf}/{tc}) vs own {rate_own:.3f} ({of_}/{oc}), ratio "
          f"{art['B3']['ratio']:.2f} (bar 1.5): passed {b3}")

    ct = np.concatenate([np.array(r["cred_true"]) for r in on
                         if r["cred_true"]] or [np.array([])])
    cf = np.concatenate([np.array(r["cred_false"]) for r in on
                         if r["cred_false"]] or [np.array([])])
    gap = (float(ct.mean() - cf.mean())
           if ct.size and cf.size else None)
    b4 = gap is not None and gap >= 0.15
    art["B4"] = {"mean_cred_true": float(ct.mean()) if ct.size else None,
                 "mean_cred_false": float(cf.mean()) if cf.size else None,
                 "gap": gap, "n_true_pairs": int(ct.size),
                 "n_false_pairs": int(cf.size), "passed": bool(b4)}
    print(f"B4 reputation separates: true-tellers "
          f"{art['B4']['mean_cred_true']} (n {ct.size}) vs "
          f"stale-voiced {art['B4']['mean_cred_false']} (n {cf.size}), "
          f"gap {gap} (bar 0.15): passed {b4}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-22-told.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-22-told-replication.json")
    else:
        run_stage(range(1, 25), RESULTS / "phase-22-told.json")
        run_stage(range(31, 55),
                  RESULTS / "phase-22-told-replication.json")
