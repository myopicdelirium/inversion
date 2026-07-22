"""Phase 5: produce the phase diagram. Artifacts under results/:

  phase-5-diagram.json  all cells of diagrams A, B, C with seeds,
                        config hashes, sweep digests, 10k scale record
  phase-5-map.png       the main map (excess mortality, both modes)
  phase-5-planes.png    the psychology plane and the composition gaps

Run:  uv run python scripts/validate_phase5.py
"""

import json
import pathlib
import sys
import time
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import golden_hash, run  # noqa: E402
from core.sweep import run_sweep, sweep_digest  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"n_hazard": 0, "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1}
BONDS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
RAMPS = [1, 50, 100, 200, 400, 800, 1600]
SEEDS = [1, 2, 3, 4, 5, 6]
WORKERS = 6


def cell_map(sweep, fields):
    return {tuple(c["cell"][f] for f in fields): c["pooled_cohort_mortality"]
            for c in sweep["cells"]}


def main():
    RESULTS.mkdir(exist_ok=True)

    print("diagram A: bond x ramp x mode (504 runs)")
    t0 = time.time()
    a = run_sweep(base=ARENA,
                  axes=[("storm_ramp_harmless", [False, True]),
                        ("bond_init", BONDS), ("storm_ramp", RAMPS)],
                  seeds=SEEDS, ticks=3000, onset=2000, window=1000,
                  workers=WORKERS)
    ta = time.time() - t0
    amap = cell_map(a, ("storm_ramp_harmless", "bond_init", "storm_ramp"))
    excess = {}
    for mode in (False, True):
        for b in BONDS:
            for r in RAMPS:
                excess[(mode, b, r)] = amap[(mode, b, r)] - amap[(mode, 0.0, r)]
    print(f"  done in {ta:.0f}s, digest {sweep_digest(a)[:12]}")

    print("diagram B: tau plane (150 runs)")
    t0 = time.time()
    b_sweep = run_sweep(base=dict(ARENA, bond_init=1.0),
                        axes=[("tau_bond", [15.0, 30.0, 60.0, 120.0, 240.0]),
                              ("tau_safety", [3.0, 6.0, 12.0, 24.0, 48.0])],
                        seeds=SEEDS, ticks=3000, onset=2000, window=1000,
                        workers=WORKERS)
    tb = time.time() - t0
    bmap = cell_map(b_sweep, ("tau_bond", "tau_safety"))
    relief = max(bmap.values()) - min(bmap.values())
    print(f"  done in {tb:.0f}s, relief {relief:.3f} "
          f"(min {min(bmap.values()):.2f}, max {max(bmap.values()):.2f})")

    print("diagram C: composition (84 runs)")
    t0 = time.time()
    c_sweep = run_sweep(base=dict(ARENA, bond_init=0.6, tau_bond_spread=0.5,
                                  bond_init_spread=0.25),
                        axes=[("storm_ramp_harmless", [False, True]),
                              ("storm_ramp", RAMPS)],
                        seeds=SEEDS, ticks=3000, onset=2000, window=1000,
                        workers=WORKERS)
    tc = time.time() - t0
    comp = []
    for cell in c_sweep["cells"]:
        m = cell["pooled_cohort_mortality"]
        rows = [r for r in cell["runs"] if r["tau_bond_median_dead"] is not None
                and r["tau_bond_median_alive"] is not None]
        if not (0.05 < m < 0.95) or not rows:
            comp.append({"cell": cell["cell"], "mortality": m, "qualifying": False})
            continue
        clock_gap = float(np.mean([r["tau_bond_median_dead"] - r["tau_bond_median_alive"]
                                   for r in rows]))
        depth_gap = float(np.mean([r["bond_init_mean_dead"] - r["bond_init_mean_alive"]
                                   for r in rows
                                   if r["bond_init_mean_dead"] is not None]))
        comp.append({"cell": cell["cell"], "mortality": m, "qualifying": True,
                     "clock_gap": clock_gap, "depth_gap": depth_gap})
    qual = [c for c in comp if c["qualifying"]]
    clock_ok = sum(1 for c in qual if c["clock_gap"] < 0)
    depth_ok = sum(1 for c in qual if c["depth_gap"] > 0)
    print(f"  done in {tc:.0f}s; qualifying cells {len(qual)}, "
          f"clock gap negative in {clock_ok}, depth gap positive in {depth_ok}")

    print("population scale: 10,000 agents")
    big = replace(Config(), n_agents=10000, world_size=700.0, n_food=7500,
                  n_nests=50, record_every=50, **ARENA, bond_init=1.0)
    t0 = time.time()
    big_traj = run(big, seed=42, ticks=3000)
    t10k = time.time() - t0
    at_risk = 10000 // 50
    cohort = (np.arange(10000) % 50) == 0
    k_onset = int(np.argmax(np.array(big_traj["tick"]) >= 2000))
    risk = cohort & big_traj["alive"][k_onset]
    dead = risk & ~big_traj["alive"][-1]
    det = golden_hash(run(big, seed=7, ticks=300)) == golden_hash(run(big, seed=7, ticks=300))
    print(f"  3000 ticks in {t10k:.0f}s; cohort mortality "
          f"{dead.sum() / max(risk.sum(), 1):.2f}; determinism {det}")

    # Criteria, judged as declared in specs/phase-5.md.
    hot = max(excess[(False, b, r)] for b in BONDS[1:] for r in RAMPS)
    null_ok = all(abs(excess[(True, b, r)]) <= 0.02
                  for b in BONDS[1:] for r in (800, 1600))
    c2 = {"max_excess_damage_mode": hot, "inversion_region": bool(hot >= 0.40),
          "null_region_harmless_800plus": bool(null_ok),
          "passed": bool(hot >= 0.40 and null_ok)}
    c3 = {"relief": relief, "passed": bool(relief >= 0.15)}
    c4 = {"qualifying_cells": len(qual), "clock_gap_negative": clock_ok,
          "depth_gap_positive": depth_ok,
          "passed": bool(qual and clock_ok >= 0.8 * len(qual)
                         and depth_ok >= 0.8 * len(qual))}
    c5 = {"wall_seconds_10k_3000ticks": t10k, "determinism_10k": bool(det),
          "cohort_size": int(at_risk), "passed": bool(det)}

    artifact = {
        "spec": "specs/phase-5.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "diagram_a": {"sweep": a, "digest": sweep_digest(a),
                      "wall_seconds": ta,
                      "excess": {f"{m}|{b}|{r}": v for (m, b, r), v in excess.items()}},
        "diagram_b": {"sweep": b_sweep, "digest": sweep_digest(b_sweep),
                      "wall_seconds": tb},
        "diagram_c": {"sweep": c_sweep, "digest": sweep_digest(c_sweep),
                      "wall_seconds": tc, "composition": comp},
        "criterion_2_structure": c2,
        "criterion_3_relief": c3,
        "criterion_4_composition": c4,
        "criterion_5_scale": c5,
        "passed": bool(c2["passed"] and c3["passed"] and c4["passed"] and c5["passed"]),
    }
    (RESULTS / "phase-5-diagram.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figures(amap, excess, bmap, comp)
    print(f"criteria: structure {c2['passed']} (max excess {hot:.2f}, "
          f"null {null_ok}), relief {c3['passed']} ({relief:.2f}), "
          f"composition {c4['passed']}, scale {c5['passed']}")
    print(f"-> all criteria passed: {artifact['passed']}")


def make_figures(amap, excess, bmap, comp):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=150)
    for ax, mode, title in ((axes[0], False, "damage ramps with signal"),
                            (axes[1], True, "harmless ramp: warning only")):
        grid = np.array([[excess[(mode, b, r)] for r in RAMPS] for b in BONDS])
        im = ax.imshow(grid, cmap="Reds", vmin=0, vmax=1, aspect="auto", origin="lower")
        ax.set_xticks(range(len(RAMPS)), [str(r) for r in RAMPS], fontsize=7, color=ink)
        ax.set_yticks(range(len(BONDS)), [str(b) for b in BONDS], fontsize=7, color=ink)
        ax.set_xlabel("storm ramp, ticks", fontsize=8, color=ink)
        ax.set_ylabel("bond_init", fontsize=8, color=ink)
        ax.set_title(f"Excess mortality over bond 0: {title}", fontsize=9, color=ink)
        for i in range(len(BONDS)):
            for j in range(len(RAMPS)):
                v = grid[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                        color="#FFFFFF" if v > 0.5 else ink)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("The phase diagram: where inversion lives", fontsize=11, color=ink)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-5-map.png", bbox_inches="tight")

    fig2, axes2 = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
    tb_vals = [15.0, 30.0, 60.0, 120.0, 240.0]
    ts_vals = [3.0, 6.0, 12.0, 24.0, 48.0]
    grid = np.array([[bmap[(tb, ts)] for ts in ts_vals] for tb in tb_vals])
    im = axes2[0].imshow(grid, cmap="Reds", vmin=0, vmax=1, aspect="auto", origin="lower")
    axes2[0].set_xticks(range(5), [str(v) for v in ts_vals], fontsize=7, color=ink)
    axes2[0].set_yticks(range(5), [str(v) for v in tb_vals], fontsize=7, color=ink)
    axes2[0].set_xlabel("tau_safety (speed of fear)", fontsize=8, color=ink)
    axes2[0].set_ylabel("tau_bond (attachment clock)", fontsize=8, color=ink)
    axes2[0].set_title("Mortality on the psychology plane, sudden storm, bond 1.0",
                       fontsize=9, color=ink)
    for i in range(5):
        for j in range(5):
            v = grid[i, j]
            axes2[0].text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                          color="#FFFFFF" if v > 0.5 else ink)
    fig2.colorbar(im, ax=axes2[0], fraction=0.046)

    for mode, color, label in ((False, "#A32D2D", "damage-carrying ramp"),
                               (True, "#0F6E56", "harmless ramp")):
        xs, ys = [], []
        for c in comp:
            if c["qualifying"] and c["cell"]["storm_ramp_harmless"] == mode:
                xs.append(c["cell"]["storm_ramp"])
                ys.append(c["clock_gap"])
        if xs:
            axes2[1].plot(xs, ys, color=color, lw=1.6, marker="o", ms=4, label=label)
    axes2[1].axhline(0, color=ink, lw=0.6, ls=":")
    axes2[1].set_xscale("log")
    axes2[1].set_xlabel("storm ramp, ticks (log)", fontsize=8, color=ink)
    axes2[1].set_ylabel("tau_bond, dead minus alive", fontsize=8, color=ink)
    axes2[1].set_title("Selection: the dead carry faster attachment clocks",
                       fontsize=9, color=ink)
    axes2[1].legend(frameon=False, fontsize=8)
    for ax in axes2:
        ax.tick_params(colors=ink, labelsize=7)
    for side in ("top", "right"):
        axes2[1].spines[side].set_visible(False)
    fig2.tight_layout()
    fig2.savefig(RESULTS / "phase-5-planes.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
