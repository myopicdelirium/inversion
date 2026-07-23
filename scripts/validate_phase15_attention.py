"""Phase 15 addendum 4: the trained voice. Artifacts:

  results/phase-15-attention.json              A0-A1 on seeds 1-24
  results/phase-15-attention-replication.json  fresh seeds 31-54
  results/phase-15-attention-a2.json           pooled mediation cell

Byte-identical rerun of the distant-death cells with one live
measurement: each mourner's drive-weight vector at the moment of loss.
Primary predictor, declared in the spec: w_energy (weights column 0).

Run:
  uv run python scripts/validate_phase15_attention.py all
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

DISTANT = {"bond_target": "leader", "n_leaders": 10, "n_agents": 400,
           "n_hazard": 0, "storm_nest": 0, "storm_onset": 2000,
           "storm_ramp": 1, "storm_snare": 0.95, "storm_damage": 0.01,
           "n_food": 40, "attention_floor": 0.01}


def attention_cell(mode, seed):
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
    loss_w = np.full((n, 4), np.nan)
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
                loss_tick[target_died] = m.tick
                loss_w[target_died] = m.arrays.weights[target_died]
        prev_alive = alive.copy()

    bereaved = loss_tick >= 0
    starved = bereaved & (death_tick >= loss_tick) & (death_energy <= 0.0)
    return {"mode": mode, "seed": seed, "config_hash": cfg.config_hash(),
            "bereaved": int(bereaved.sum()),
            "loss_w": [[round(float(v), 5) for v in row]
                       for row in loss_w[bereaved]],
            "starved": [bool(s) for s in starved[bereaved]]}


def _cell(args):
    return attention_cell(args[0], args[1])


def run_stage(seeds, out_path):
    jobs = [(m, s) for m in ("leader", "partner") for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))
    art = {"spec": "specs/phase-15.md addendum 4",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}

    pooled = {}
    for m in ("leader", "partner"):
        we = np.concatenate([np.array(r["loss_w"])[:, 0] for r in rows
                             if r["mode"] == m and r["bereaved"] > 0]
                            or [np.array([])])
        s = np.concatenate([np.array(r["starved"], dtype=bool) for r in rows
                            if r["mode"] == m and r["bereaved"] > 0]
                           or [np.array([], dtype=bool)])
        pooled[m] = (we, s)
        art[m] = {"bereaved": int(we.size),
                  "median_w_energy": float(np.median(we)) if we.size else None,
                  "neglect_rate": float(s.mean()) if we.size else None}
        print(f"{m}: bereaved {we.size}, median w_energy at loss "
              f"{art[m]['median_w_energy']}, neglect {art[m]['neglect_rate']}")

    a0 = (art["leader"]["median_w_energy"] is not None
          and art["partner"]["median_w_energy"] is not None
          and art["leader"]["median_w_energy"] > art["partner"]["median_w_energy"])
    art["A0"] = {"passed": bool(a0)}
    print(f"A0 manipulation check (leader median w_energy > partner): {a0}")

    we, s = pooled["partner"]
    lo, hi = np.quantile(we, [1 / 3, 2 / 3])
    terc = {}
    for name, mask in (("low", we <= lo), ("mid", (we > lo) & (we <= hi)),
                       ("high", we > hi)):
        terc[name] = {"n": int(mask.sum()),
                      "rate": float(s[mask].mean()) if mask.any() else None}
    low, high = terc["low"]["rate"], terc["high"]["rate"]
    a1 = low is not None and high is not None and low >= 2.0 * max(high, 1e-9)
    art["A1"] = {"terciles": terc, "cut_lo": float(lo), "cut_hi": float(hi),
                 "ratio": low / max(high, 1e-9) if low is not None else None,
                 "passed": bool(a1)}
    print(f"A1 partner terciles by w_energy: low {low} (n {terc['low']['n']}), "
          f"mid {terc['mid']['rate']}, high {high} (n {terc['high']['n']}): {a1}")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)
    return pooled


def judge_a2(pool_main, pool_rep):
    both = {}
    for m in ("leader", "partner"):
        we = np.concatenate([pool_main[m][0], pool_rep[m][0]])
        s = np.concatenate([pool_main[m][1], pool_rep[m][1]])
        both[m] = (we, s)
    allw = np.concatenate([both["leader"][0], both["partner"][0]])
    hi = float(np.quantile(allw, 2 / 3))
    rates = {}
    for m in ("leader", "partner"):
        we, s = both[m]
        top = we > hi
        rates[m] = {"n_top": int(top.sum()),
                    "top_rate": float(s[top].mean()) if top.any() else None,
                    "uncond_rate": float(s.mean())}
    uncond_gap = rates["partner"]["uncond_rate"] - rates["leader"]["uncond_rate"]
    top_gap = (rates["partner"]["top_rate"] - rates["leader"]["top_rate"]
               if None not in (rates["partner"]["top_rate"],
                               rates["leader"]["top_rate"]) else None)
    a2 = top_gap is not None and abs(top_gap) <= 0.5 * abs(uncond_gap)
    art = {"spec": "specs/phase-15.md addendum 4", "cut_top": hi,
           "rates": rates, "uncond_gap_points": 100 * uncond_gap,
           "top_gap_points": 100 * top_gap if top_gap is not None else None,
           "passed": bool(a2)}
    print(f"A2 mediation: unconditioned gap {100 * uncond_gap:+.1f} pts, "
          f"loud-hunger gap {art['top_gap_points']} pts "
          f"(leader n_top {rates['leader']['n_top']}): {a2}")
    (RESULTS / "phase-15-attention-a2.json").write_text(
        json.dumps(art, indent=2) + "\n")
    print("written phase-15-attention-a2.json")


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-15-attention.json")
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-15-attention-replication.json")
    else:
        pm = run_stage(range(1, 25), RESULTS / "phase-15-attention.json")
        pr = run_stage(range(31, 55),
                       RESULTS / "phase-15-attention-replication.json")
        judge_a2(pm, pr)
