"""Phase 15: authority. Artifacts:

  results/phase-15-authority.json     L1-L3 per specs/phase-15.md
  results/phase-15-replication.json   L2/L3 on fresh seeds

Run:
  uv run python scripts/validate_phase15.py main
  uv run python scripts/validate_phase15.py replicate
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
from core.model import Model, run  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

LEAD = {"bond_target": "leader", "n_leaders": 10, "n_agents": 400,
        "n_hazard": 0, "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1}
MIRE_LEAD = {**LEAD, "storm_snare": 0.95, "storm_damage": 0.01}
PHASE7_BASELINE = 0.141


def congregation(bond_init, seed):
    cfg = replace(Config(), **{**LEAD, "storm_nest": -1}, bond_init=bond_init)
    m = Model(cfg, seed)
    samples = []
    for _ in range(3000):
        m.step()
        if m.tick > 2000 and m.tick % 50 == 0:
            p = m.arrays.partner
            has = p >= 0
            pidx = np.where(has, p, 0)
            both = has & m.arrays.alive & m.arrays.alive[pidx]
            dx = _torus_delta(m.arrays.x[pidx] - m.arrays.x, cfg.world_size)
            dy = _torus_delta(m.arrays.y[pidx] - m.arrays.y, cfg.world_size)
            samples.append(float(np.hypot(dx, dy)[both].mean()))
    return float(np.mean(samples))


def storm_cell(kappa, seed, mire=False):
    ticks_total = 3500 if kappa > 0 else 3000
    arena = MIRE_LEAD if mire else LEAD
    cfg = replace(Config(), **arena, bond_init=0.8, attention_sharpness=kappa)
    traj = run(cfg, seed=seed, ticks=ticks_total)
    m0 = Model(cfg, seed)
    p = m0.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    sx, sy = m0.world.storm_x, m0.world.storm_y
    ticks = np.array(traj["tick"])
    alive = traj["alive"]
    k_on = int(np.argmax(ticks >= 2000))
    idx = np.arange(cfg.n_agents)

    leader_x = traj["x"][k_on][pidx]
    leader_y = traj["y"][k_on][pidx]
    ld = np.hypot(_torus_delta(leader_x - sx, cfg.world_size),
                  _torus_delta(leader_y - sy, cfg.world_size))
    leader_caught = has & alive[k_on][pidx] & (ld < cfg.storm_radius)
    followers = has & alive[k_on]
    g_caught = followers & leader_caught
    g_free = followers & ~leader_caught

    death_frame = np.where(~alive[-1], np.argmax(~alive, axis=0), -1)
    died = death_frame >= k_on
    out = {"kappa": kappa, "seed": seed, "config_hash": cfg.config_hash(),
           "n_caught": int(g_caught.sum()), "n_free": int(g_free.sum()),
           "deaths_caught": int((g_caught & died).sum()),
           "deaths_free": int((g_free & died).sum())}
    if kappa > 0:
        pa = alive[:, pidx]
        l_dies = has & (~pa[-1])
        loss = np.where(l_dies, np.argmax(~pa, axis=0), -1)
        bereaved = l_dies & alive[np.maximum(loss, 0), idx]
        starved = (death_frame >= 0) & (
            traj["energy"][np.maximum(death_frame, 0), idx] <= 0.0)
        neglect = bereaved & starved & (death_frame >= loss)
        baseline = has & ~l_dies & alive[k_on]
        base_starved = baseline & starved & (death_frame >= k_on)
        out.update({"bereaved": int(bereaved.sum()),
                    "neglect": int(neglect.sum()),
                    "baseline_n": int(baseline.sum()),
                    "baseline_starved": int(base_starved.sum())})
    return out


def _cell(args):
    kind = args[0]
    if kind == "cong":
        return {"kind": "cong", "bond_init": args[1], "seed": args[2],
                "mean_dist": congregation(args[1], args[2])}
    return {"kind": "storm", **storm_cell(args[1], args[2], mire=args[3])}


def run_stage(seeds, out_path, with_l1, mire=False):
    jobs = []
    if with_l1:
        jobs += [("cong", b, s) for b in (0.8, 0.0) for s in range(1, 6)]
    jobs += [("storm", k, s, mire) for k in (0.0, 2.0) for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(_cell, jobs))

    art = {"spec": "specs/phase-15.md",
           "manifest": build_manifest(seed=0, config=Config()),
           "seeds": list(seeds), "rows": rows}
    if with_l1:
        d8 = np.mean([r["mean_dist"] for r in rows
                      if r["kind"] == "cong" and r["bond_init"] == 0.8])
        d0 = np.mean([r["mean_dist"] for r in rows
                      if r["kind"] == "cong" and r["bond_init"] == 0.0])
        art["L1"] = {"bonded": float(d8), "unbonded": float(d0),
                     "ratio": float(d0 / max(d8, 1e-9)),
                     "passed": bool(d0 / max(d8, 1e-9) >= 3.0)}
        print(f"L1 congregation: bonded {d8:.2f} vs unbonded {d0:.2f} "
              f"(ratio {art['L1']['ratio']:.1f})")
    s0 = [r for r in rows if r["kind"] == "storm" and r["kappa"] == 0.0]
    mc = sum(r["deaths_caught"] for r in s0) / max(sum(r["n_caught"] for r in s0), 1)
    mf = sum(r["deaths_free"] for r in s0) / max(sum(r["n_free"] for r in s0), 1)
    art["L2"] = {"mortality_leader_caught": mc, "mortality_leader_free": mf,
                 "n_caught": sum(r["n_caught"] for r in s0),
                 "ratio": mc / max(mf, 1e-9), "passed": bool(mc >= 2.0 * mf)}
    print(f"L2 single point of failure: caught {mc:.3f} (n "
          f"{art['L2']['n_caught']}) vs free {mf:.3f} (ratio {art['L2']['ratio']:.1f})")
    s2 = [r for r in rows if r["kind"] == "storm" and r["kappa"] == 2.0]
    ber = sum(r["bereaved"] for r in s2)
    neg = sum(r["neglect"] for r in s2)
    bn = sum(r["baseline_n"] for r in s2)
    bd = sum(r["baseline_starved"] for r in s2)
    rate = neg / max(ber, 1)
    art["L3"] = {"bereaved": ber, "neglect_rate": rate,
                 "baseline_rate": bd / max(bn, 1),
                 "phase7_baseline": PHASE7_BASELINE,
                 "gap_points": 100 * (rate - PHASE7_BASELINE),
                 "passed": bool(abs(rate - PHASE7_BASELINE) <= 0.05)}
    print(f"L3 additivity null: {neg}/{ber} bereaved starve ({rate:.3f}) vs "
          f"phase-7 partner baseline {PHASE7_BASELINE} "
          f"(gap {art['L3']['gap_points']:+.1f} pts; own-baseline "
          f"{art['L3']['baseline_rate']:.3f})")
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "main":
        run_stage(range(1, 25), RESULTS / "phase-15-authority.json", with_l1=True)
    elif stage == "replicate":
        run_stage(range(31, 55), RESULTS / "phase-15-replication.json", with_l1=False)
    elif stage == "mire_main":
        run_stage(range(1, 25), RESULTS / "phase-15-mire-leader.json",
                  with_l1=False, mire=True)
    else:
        run_stage(range(31, 55), RESULTS / "phase-15-mire-replication.json",
                  with_l1=False, mire=True)
