"""Phase 10 validation: the whisper floor. Artifact:

  results/phase-10-floor.json  predictions F1-F4 judged as written

Run:  uv run python scripts/validate_phase10.py
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FLOOR = 0.05


def everyday_survival(kappa, floor, seeds=range(1, 6)):
    vals = []
    for seed in seeds:
        cfg = replace(Config(), attention_sharpness=kappa, attention_floor=floor)
        vals.append(float(run(cfg, seed=seed, ticks=5000)["alive"][-1].mean()))
    return float(np.mean(vals)), vals


def main():
    RESULTS.mkdir(exist_ok=True)

    print("F1: fear becomes acquirable (everyday, kappa 1)")
    f1_mean, f1_seeds = everyday_survival(1.0, FLOOR)
    f1 = {"floor0_reference": 0.108, "floor005": f1_mean, "per_seed": f1_seeds,
          "passed": bool(f1_mean >= 0.5)}
    print(f"  survival {f1_mean:.3f} (was 0.108 at floor 0)")

    print("F2: peacetime collapse cured (place arena, bond 1.0, kappa 1.5)")
    alive_at_onset = []
    for seed in (1, 2, 3, 4, 5):
        cfg = replace(Config(), n_hazard=0, storm_nest=0, storm_onset=2000,
                      storm_ramp=1, bond_init=1.0, attention_sharpness=1.5,
                      attention_floor=FLOOR)
        traj = run(cfg, seed=seed, ticks=2000)
        alive_at_onset.append(int(traj["alive"][-1].sum()))
    f2 = {"alive_at_onset_per_seed": alive_at_onset,
          "floor0_reference": "0-1 of 200",
          "passed": bool(min(alive_at_onset) >= 150)}
    print(f"  alive at onset: {alive_at_onset} (was 0-1 of 200 at floor 0)")

    print("F3: the origin case survives the fix (grief cell, kappa 2)")
    rows = [grief_cell_with_floor(2.0, 0.8, seed) for seed in range(1, 7)]
    ber = sum(r["bereaved"] for r in rows)
    neg = sum(r["bereaved_neglect_deaths"] for r in rows)
    base_n = sum(r["baseline_agents"] for r in rows)
    base_d = sum(r["baseline_starvation_deaths"] for r in rows)
    rate = neg / max(ber, 1)
    f3 = {"bereaved": ber, "neglect_deaths": neg, "neglect_rate": rate,
          "baseline_rate": base_d / max(base_n, 1),
          "passed": bool(rate >= 0.03 and base_d / max(base_n, 1) <= 0.01)}
    print(f"  {neg}/{ber} bereaved starve (rate {rate:.3f}, baseline "
          f"{f3['baseline_rate']:.3f})")

    print("F4: the axis becomes smooth (everyday boundary at floor 0.05)")
    boundary = {}
    for kappa in (0.0, 0.5, 1.0, 1.5, 2.0):
        m, _ = everyday_survival(kappa, FLOOR)
        boundary[str(kappa)] = m
        print(f"  kappa {kappa}: survival {m:.3f}")
    f4 = {"boundary": boundary, "passed": bool(boundary["1.5"] > 0.3)}

    artifact = {
        "spec": "specs/phase-10.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "F1_fear_acquirable": f1, "F2_collapse_cured": f2,
        "F3_origin_case_survives": f3, "F4_smooth_axis": f4,
        "passed": bool(f1["passed"] and f2["passed"] and f3["passed"] and f4["passed"]),
    }
    (RESULTS / "phase-10-floor.json").write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"F1 {f1['passed']}, F2 {f2['passed']}, F3 {f3['passed']}, F4 {f4['passed']}")
    print(f"-> all predictions held: {artifact['passed']}")


def grief_cell_with_floor(kappa, bond_init, seed):
    """bereavement accounting with the floor on; mirrors
    scripts/validate_phase7.bereavement_cell with one added field."""
    from core.model import Model
    cfg = replace(Config(), bond_target="partner", n_agents=400, n_hazard=0,
                  storm_nest=0, storm_onset=2000, storm_ramp=1,
                  bond_init=bond_init, attention_sharpness=kappa,
                  attention_floor=FLOOR)
    traj = run(cfg, seed=seed, ticks=3500)
    m0 = Model(cfg, seed)
    p = m0.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    alive = traj["alive"]
    ticks = np.array(traj["tick"])
    k_onset = int(np.argmax(ticks >= 2000))
    partner_alive = alive[:, pidx]
    partner_dies = has & (~partner_alive[-1])
    loss_frame = np.where(partner_dies, np.argmax(~partner_alive, axis=0), -1)
    idx = np.arange(cfg.n_agents)
    bereaved = partner_dies & alive[np.maximum(loss_frame, 0), idx]
    death_frame = np.where(~alive[-1], np.argmax(~alive, axis=0), -1)
    starved = (death_frame >= 0) & (traj["energy"][np.maximum(death_frame, 0), idx] <= 0.0)
    neglect = bereaved & starved & (death_frame >= loss_frame)
    baseline_group = has & ~partner_dies & alive[k_onset]
    baseline_starved = baseline_group & starved & (death_frame >= k_onset)
    return {"bereaved": int(bereaved.sum()),
            "bereaved_neglect_deaths": int(neglect.sum()),
            "baseline_agents": int(baseline_group.sum()),
            "baseline_starvation_deaths": int(baseline_starved.sum())}


if __name__ == "__main__":
    main()
