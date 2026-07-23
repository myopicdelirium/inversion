"""Phase 7 validation. Artifacts under results/:

  phase-7-validation.json  criteria 1-8 of specs/phase-7.md
  phase-7-attention.png    the grief-lethality map and the symmetry

Run:  uv run python scripts/validate_phase7.py
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

STORM = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1}
TAUS = np.array([20.0, 12.0, 30.0, 60.0])


def identity_kappa2():
    """Criterion 3: every transition satisfies the attended law, with
    heard reconstructed from recorded arrays."""
    cfg = replace(Config(), **STORM, bond_init=0.8, attention_sharpness=2.0,
                  record_every=1)
    seed = 3
    traj = run(cfg, seed=seed, ticks=3000)
    w, u, alive = traj["weights"], traj["urgency"], traj["alive"]
    prev = w[:-1]
    loudest = np.maximum(prev.max(axis=2, keepdims=True), 1e-12)
    heard = u[1:] * (prev / loudest) ** cfg.attention_sharpness
    expected = prev + (heard - prev) / TAUS[None, None, :]
    live = alive[1:]
    residual = float(np.max(np.abs(w[1:][live] - expected[live])))
    checked = int(live.sum()) * 4
    print(f"  attended-law identity: max residual {residual:.1e} over "
          f"{checked} drive transitions")
    return {"seed": seed, "config_hash": cfg.config_hash(),
            "max_abs_residual": residual, "transitions": checked,
            "passed": bool(residual < 1e-12)}


def everyday_null():
    """Criterion 4 as declared (kappa 2 within 2 points of kappa 0),
    plus the full viability boundary along the axis, measured because
    the declared point turned out to sit far beyond it."""
    out = {}
    for kappa in (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
        survs = []
        for seed in range(1, 6):
            cfg = replace(Config(), attention_sharpness=kappa)
            traj = run(cfg, seed=seed, ticks=5000)
            survs.append(float(traj["alive"][-1].mean()))
        out[str(kappa)] = {"per_seed": survs, "mean": float(np.mean(survs))}
        print(f"  everyday world, kappa {kappa}: survival {out[str(kappa)]['mean']:.3f}")
    gap = abs(out["0.0"]["mean"] - out["2.0"]["mean"])
    out["gap_at_declared_kappa2"] = float(gap)
    out["passed"] = bool(gap <= 0.02)
    return out


def bereavement_cell(kappa, bond_init, seed):
    """One partner-storm run's bereavement accounting, from the
    recorded trajectory alone."""
    cfg = replace(Config(), **STORM, bond_init=bond_init,
                  attention_sharpness=kappa)
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
    # Bereaved: partner died, agent still alive at that frame.
    idx = np.arange(cfg.n_agents)
    bereaved = partner_dies & alive[np.maximum(loss_frame, 0), idx]

    death_frame = np.where(~alive[-1], np.argmax(~alive, axis=0), -1)
    starved = (death_frame >= 0) & (traj["energy"][np.maximum(death_frame, 0), idx] <= 0.0)
    neglect = bereaved & starved & (death_frame >= loss_frame)

    baseline_group = has & ~partner_dies & alive[k_onset]
    baseline_starved = baseline_group & starved & (death_frame >= k_onset)
    return {
        "kappa": kappa, "bond_init": bond_init, "seed": seed,
        "config_hash": cfg.config_hash(),
        "bereaved": int(bereaved.sum()),
        "bereaved_neglect_deaths": int(neglect.sum()),
        "baseline_agents": int(baseline_group.sum()),
        "baseline_starvation_deaths": int(baseline_starved.sum()),
    }


def grief_map():
    """Criteria 5 and 7 from one grid."""
    kappas = [0.0, 0.5, 1.0, 1.5, 2.0]
    bonds = [0.4, 0.8]
    cells = []
    for kappa in kappas:
        for b0 in bonds:
            rows = [bereavement_cell(kappa, b0, seed) for seed in range(1, 7)]
            ber = sum(r["bereaved"] for r in rows)
            neg = sum(r["bereaved_neglect_deaths"] for r in rows)
            base_n = sum(r["baseline_agents"] for r in rows)
            base_d = sum(r["baseline_starvation_deaths"] for r in rows)
            cells.append({
                "kappa": kappa, "bond_init": b0, "runs": rows,
                "bereaved": ber,
                "neglect_rate": neg / max(ber, 1),
                "baseline_starvation_rate": base_d / max(base_n, 1),
            })
            print(f"  kappa {kappa} bond {b0}: {neg}/{ber} bereaved starve "
                  f"(baseline {cells[-1]['baseline_starvation_rate']:.3f})")
    def cell(kappa, b0):
        return next(c for c in cells if c["kappa"] == kappa and c["bond_init"] == b0)
    k0 = cell(0.0, 0.8)
    k2 = cell(2.0, 0.8)
    excess0 = k0["neglect_rate"] - k0["baseline_starvation_rate"]
    excess2 = k2["neglect_rate"] - k2["baseline_starvation_rate"]
    c5 = {"excess_kappa0": float(excess0), "excess_kappa2": float(excess2),
          "passed": bool(abs(excess0) < 0.05 and excess2 >= 0.20)}
    print(f"  neglect requires attention: excess {excess0:+.3f} at kappa 0, "
          f"{excess2:+.3f} at kappa 2")
    return c5, {"cells": cells}


def tunnel_vision():
    """Criterion 6: hunger's dominance blinds agents to danger. Scarce
    food, ordinary drifting hazards, no storm."""
    out = {}
    for kappa in (0.0, 2.0):
        rates = []
        for seed in range(1, 6):
            cfg = replace(Config(), n_food=25, attention_sharpness=kappa)
            traj = run(cfg, seed=seed, ticks=4000)
            idx = np.arange(cfg.n_agents)
            death_frame = np.where(~traj["alive"][-1],
                                   np.argmax(~traj["alive"], axis=0), -1)
            burned = (death_frame >= 0) & (
                traj["integrity"][np.maximum(death_frame, 0), idx] <= 0.0)
            rates.append(float(burned.mean()))
        out[str(kappa)] = {"per_seed": rates, "mean": float(np.mean(rates))}
        print(f"  scarce food, kappa {kappa}: integrity-death rate "
              f"{out[str(kappa)]['mean']:.3f}")
    ratio = out["2.0"]["mean"] / max(out["0.0"]["mean"], 1e-9)
    out["ratio"] = float(ratio)
    out["passed"] = bool(ratio >= 1.5)
    return out


def make_figure(grid, tunnel):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
    kappas = [0.0, 0.5, 1.0, 1.5, 2.0]
    for b0, color in ((0.4, "#7F77DD"), (0.8, "#3C3489")):
        ys = [next(c["neglect_rate"] for c in grid["cells"]
                   if c["kappa"] == k and c["bond_init"] == b0) for k in kappas]
        axes[0].plot(kappas, ys, color=color, lw=1.8, marker="o", ms=4,
                     label=f"bond {b0}")
    axes[0].set_xlabel("attention sharpness", fontsize=8, color=ink)
    axes[0].set_ylabel("bereaved who starve", fontsize=8, color=ink)
    axes[0].set_title("Where grief becomes lethal", fontsize=10, color=ink)
    axes[0].legend(frameon=False, fontsize=8)

    x = np.arange(2)
    axes[1].bar(x, [tunnel["0.0"]["mean"], tunnel["2.0"]["mean"]], 0.5,
                color=["#B4B2A9", "#854F0B"])
    axes[1].set_xticks(x, ["kappa 0", "kappa 2"], fontsize=8)
    axes[1].set_ylabel("deaths in hazards, scarce food", fontsize=8, color=ink)
    axes[1].set_title("The same deafness, pointed at fear", fontsize=10, color=ink)
    for ax in axes:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=ink, labelsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-7-attention.png", bbox_inches="tight")


def main():
    RESULTS.mkdir(exist_ok=True)
    print("attended-law identity (criterion 3):")
    c3 = identity_kappa2()
    print("everyday null (criterion 4):")
    c4 = everyday_null()
    print("the grief map (criteria 5, 7):")
    c5, grid = grief_map()
    print("tunnel vision (criterion 6):")
    c6 = tunnel_vision()
    artifact = {
        "spec": "specs/phase-7.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "criterion_1_preservation": "all golden trajectories verified "
            "bit-identical at kappa 0 before commit; config hashes refreshed",
        "criterion_2_no_drive_names": "tests/test_invariants.py::"
            "test_update_law_names_no_drive, written before the mechanism",
        "criterion_3_identity": c3,
        "criterion_4_everyday_null": c4,
        "criterion_5_neglect_requires_attention": c5,
        "criterion_6_tunnel_vision": c6,
        "criterion_7_grief_map": grid,
        "passed": bool(c3["passed"] and c4["passed"] and c5["passed"] and c6["passed"]),
    }
    (RESULTS / "phase-7-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(grid, c6)
    print(f"criteria: identity {c3['passed']}, everyday {c4['passed']}, "
          f"neglect {c5['passed']}, symmetry {c6['passed']}")
    print(f"-> all criteria passed: {artifact['passed']}")


if __name__ == "__main__":
    main()
