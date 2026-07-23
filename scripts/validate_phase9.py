"""Phase 9: map the human axes. Artifacts under results/:

  phase-9-maps.json  diagrams D, E, F; predictions P1-P4 judged as written
  phase-9-maps.png   attention map and tar pit

Run:  uv run python scripts/validate_phase9.py
"""

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.sweep import run_sweep, sweep_digest  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"n_hazard": 0, "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1}
SEEDS = [1, 2, 3, 4, 5, 6]
KAPPAS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]


def main():
    RESULTS.mkdir(exist_ok=True)

    print("diagram D: attention x place-attachment (216 runs)")
    d = run_sweep(base=ARENA,
                  axes=[("attention_sharpness", KAPPAS),
                        ("bond_init", [0.0, 0.5, 1.0]),
                        ("storm_ramp", [1, 400])],
                  seeds=SEEDS, ticks=3000, onset=2000, window=1000, workers=6)
    dmap = {(c["cell"]["attention_sharpness"], c["cell"]["bond_init"],
             c["cell"]["storm_ramp"]): c["pooled_cohort_mortality"]
            for c in d["cells"]}
    for r in (1, 400):
        for b in (1.0, 0.5, 0.0):
            print(f"  ramp {r:>3} bond {b}: "
                  f"{[round(dmap[(k, b, r)], 3) for k in KAPPAS]}")

    print("diagram E: the tar pit (36 runs)")
    e = run_sweep(base=dict(ARENA, storm_damage=0.01),
                  axes=[("storm_snare", [0.0, 0.5, 0.9]),
                        ("bond_init", [0.0, 1.0])],
                  seeds=SEEDS, ticks=3000, onset=2000, window=1000, workers=6)
    emap = {(c["cell"]["storm_snare"], c["cell"]["bond_init"]):
            c["pooled_cohort_mortality"] for c in e["cells"]}
    for b in (1.0, 0.0):
        print(f"  bond {b}: snare 0/0.5/0.9 -> "
              f"{[round(emap[(s, b)], 3) for s in (0.0, 0.5, 0.9)]}")

    print("diagram F: selection under attention (12 runs)")
    f = run_sweep(base=dict(ARENA, bond_init=0.6, tau_bond_spread=0.5,
                            bond_init_spread=0.25),
                  axes=[("attention_sharpness", [0.0, 0.75])],
                  seeds=SEEDS, ticks=3000, onset=2000, window=1000, workers=6)
    gaps = {}
    for c in f["cells"]:
        k = c["cell"]["attention_sharpness"]
        rows = [r for r in c["runs"] if r["tau_bond_median_dead"] is not None
                and r["tau_bond_median_alive"] is not None]
        clock = float(np.mean([r["tau_bond_median_dead"] - r["tau_bond_median_alive"]
                               for r in rows])) if rows else None
        depth = float(np.mean([r["bond_init_mean_dead"] - r["bond_init_mean_alive"]
                               for r in rows
                               if r["bond_init_mean_dead"] is not None])) if rows else None
        gaps[str(k)] = {"mortality": c["pooled_cohort_mortality"],
                        "clock_gap": clock, "depth_gap": depth,
                        "seeds_with_both_groups": len(rows)}
        print(f"  kappa {k}: mortality {c['pooled_cohort_mortality']:.3f}, "
              f"clock gap {clock}, depth gap {depth}")

    p1_base = dmap[(0.0, 1.0, 1)]
    p1_best = min(dmap[(0.5, 1.0, 1)], dmap[(0.75, 1.0, 1)])
    p1 = {"kappa0": p1_base, "best_moderate": p1_best,
          "passed": bool(p1_best <= 0.5 * p1_base)}
    p2_vals = [dmap[(k, 1.0, 400)] for k in KAPPAS]
    p2 = {"values": p2_vals, "passed": bool(all(v >= 0.95 for v in p2_vals))}
    rise_b1 = emap[(0.9, 1.0)] - emap[(0.0, 1.0)]
    rise_b0 = emap[(0.9, 0.0)] - emap[(0.0, 0.0)]
    mono = emap[(0.0, 1.0)] <= emap[(0.5, 1.0)] <= emap[(0.9, 1.0)]
    p3 = {"rise_bond1": float(rise_b1), "rise_bond0": float(rise_b0),
          "monotone": bool(mono),
          "passed": bool(mono and rise_b1 >= 0.10 and rise_b0 < 0.05)}
    g0, g75 = gaps.get("0.0", {}), gaps.get("0.75", {})
    p4_ok = (g0.get("clock_gap") is not None and g75.get("clock_gap") is not None
             and abs(g75["clock_gap"]) >= abs(g0["clock_gap"])
             and abs(g75["depth_gap"]) >= abs(g0["depth_gap"]))
    p4 = {"kappa0": g0, "kappa075": g75, "passed": bool(p4_ok)}

    artifact = {
        "spec": "specs/phase-9.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "diagram_d": {"sweep": d, "digest": sweep_digest(d)},
        "diagram_e": {"sweep": e, "digest": sweep_digest(e)},
        "diagram_f": {"sweep": f, "digest": sweep_digest(f), "gaps": gaps},
        "P1_focus_protects": p1,
        "P2_saturation_attention_proof": p2,
        "P3_tar_pit": p3,
        "P4_selection_sharpens": p4,
        "passed": bool(p1["passed"] and p2["passed"] and p3["passed"] and p4["passed"]),
    }
    (RESULTS / "phase-9-maps.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(dmap, emap)
    print(f"P1 {p1['passed']} ({p1_base:.2f} -> {p1_best:.2f}), "
          f"P2 {p2['passed']}, P3 {p3['passed']} (+{rise_b1:.2f} vs +{rise_b0:.2f}), "
          f"P4 {p4['passed']}")
    print(f"-> all predictions held: {artifact['passed']}")


def make_figure(dmap, emap):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
    for b, color in ((1.0, "#501313"), (0.5, "#A32D2D"), (0.0, "#B4B2A9")):
        axes[0].plot(KAPPAS, [dmap[(k, b, 1)] for k in KAPPAS], color=color,
                     lw=1.8, marker="o", ms=4, label=f"bond {b}, sudden")
        axes[0].plot(KAPPAS, [dmap[(k, b, 400)] for k in KAPPAS], color=color,
                     lw=1.4, ls="--", marker="s", ms=3, label=f"bond {b}, slow cook")
    axes[0].set_xlabel("attention sharpness", fontsize=8, color=ink)
    axes[0].set_ylabel("cohort storm mortality", fontsize=8, color=ink)
    axes[0].set_title("Attention on the place-attachment map", fontsize=10, color=ink)
    axes[0].legend(frameon=False, fontsize=6.5, ncol=2)

    x = np.arange(3)
    axes[1].bar(x - 0.18, [emap[(s, 1.0)] for s in (0.0, 0.5, 0.9)], 0.36,
                color="#A32D2D", label="bond 1.0")
    axes[1].bar(x + 0.18, [emap[(s, 0.0)] for s in (0.0, 0.5, 0.9)], 0.36,
                color="#B4B2A9", label="bond 0")
    axes[1].set_xticks(x, ["snare 0", "snare 0.5", "snare 0.9"], fontsize=8)
    axes[1].set_ylabel("cohort storm mortality", fontsize=8, color=ink)
    axes[1].set_title("The tar pit: slow burn, growing grip", fontsize=10, color=ink)
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=ink, labelsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-9-maps.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
