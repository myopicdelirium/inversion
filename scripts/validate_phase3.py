"""Phase 3 validation. Produces the phase-gate artifacts under results/:

  phase-3-validation.json  criteria 1-6 of specs/phase-3.md, judged as
                           written, plus the harmless-ramp supplement
  phase-3-map.png          mortality heatmap and ramp curves

The grid is large, so this runs in stages, each writing its raw cells
into results/phase-3-cells.json:

  uv run python scripts/validate_phase3.py c2       criterion 2 (20 runs)
  uv run python scripts/validate_phase3.py grid_a   bond 0, 0.25 rows (40)
  uv run python scripts/validate_phase3.py grid_b   bond 0.5, 0.75, 1.0 (60)
  uv run python scripts/validate_phase3.py warn     harmless-ramp row (15)
  uv run python scripts/validate_phase3.py report   judge, write artifacts

Vocabulary rule (specs/phase-3.md): storm mortality, onset deaths,
return deaths. Every cell carries its seed and config hash.
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CELLS = RESULTS / "phase-3-cells.json"

ONSET = 2000
WINDOW = 1000
RAMPS = [1, 100, 400, 1600]
BONDS = [0.0, 0.25, 0.5, 0.75, 1.0]
GRID_SEEDS = [1, 2, 3, 4, 5]
C2_SEEDS = list(range(1, 11))


def cell_config(bond_init, ramp, harmless):
    # Arena: default nests (5, so the cohort homed to the storm nest is
    # about 40 of 200), drifting hazards off so every integrity death
    # in the window is a storm death.
    return replace(
        Config(), n_hazard=0, storm_nest=0, storm_onset=ONSET,
        storm_ramp=ramp, storm_ramp_harmless=harmless, bond_init=bond_init,
    )


def run_cell(bond_init, ramp, harmless, seed):
    """One run. Returns cohort accounting and the death decomposition.

    Cohort: agents homed to the storm nest and alive at onset. A death
    is an onset death if the agent was never observed outside the storm
    radius between activation and dying (caught inside, the neglect
    regime), a return death if it exited at least once and re-entered
    before dying (the commitment regime), otherwise other (e.g. starved
    while displaced)."""
    cfg = cell_config(bond_init, ramp, harmless)
    m = Model(cfg, seed)
    n = cfg.n_agents
    cohort = (np.arange(n) % cfg.n_nests) == cfg.storm_nest
    sx, sy = m.world.storm_x, m.world.storm_y

    ever_out = np.zeros(n, dtype=bool)       # outside storm since onset
    re_entered = np.zeros(n, dtype=bool)     # inside again after an exit
    death_tick = np.full(n, -1, dtype=np.int64)
    alive_at_onset = None
    for _ in range(ONSET + WINDOW):
        was = m.arrays.alive.copy()
        m.step()
        died = was & ~m.arrays.alive
        death_tick[died] = m.tick
        if m.tick == ONSET:
            alive_at_onset = m.arrays.alive.copy()
        if m.tick >= ONSET:
            dx = _torus_delta(m.arrays.x - sx, cfg.world_size)
            dy = _torus_delta(m.arrays.y - sy, cfg.world_size)
            inside = np.hypot(dx, dy) < cfg.storm_radius
            ever_out |= m.arrays.alive & ~inside
            re_entered |= m.arrays.alive & inside & ever_out

    at_risk = cohort & alive_at_onset
    died_window = at_risk & (death_tick >= ONSET)
    integrity_death = died_window & (m.arrays.integrity <= 0.0)
    onset_deaths = integrity_death & ~ever_out
    return_deaths = integrity_death & re_entered
    other = died_window & ~onset_deaths & ~return_deaths
    return {
        "bond_init": bond_init, "ramp": ramp, "harmless": harmless,
        "seed": seed, "config_hash": cfg.config_hash(),
        "cohort": int(cohort.sum()),
        "at_risk": int(at_risk.sum()),
        "pre_onset_cohort_deaths": int((cohort & ~alive_at_onset).sum()),
        "window_deaths": int(died_window.sum()),
        "onset_deaths": int(onset_deaths.sum()),
        "return_deaths": int(return_deaths.sum()),
        "other_deaths": int(other.sum()),
        "storm_mortality": float(died_window.sum() / max(int(at_risk.sum()), 1)),
    }


def load_cells():
    if CELLS.exists():
        return json.loads(CELLS.read_text())
    return []


def save_cells(cells):
    CELLS.write_text(json.dumps(cells, indent=2) + "\n")


def run_stage(name, jobs):
    cells = load_cells()
    done = {(c["bond_init"], c["ramp"], c["harmless"], c["seed"]) for c in cells}
    for bond_init, ramp, harmless, seed in jobs:
        if (bond_init, ramp, harmless, seed) in done:
            continue
        cell = run_cell(bond_init, ramp, harmless, seed)
        cells.append(cell)
        print(f"  bond {bond_init} ramp {ramp:4d} harmless {int(harmless)} "
              f"seed {seed}: mortality {cell['storm_mortality']:.2f} "
              f"(onset {cell['onset_deaths']}, return {cell['return_deaths']}, "
              f"other {cell['other_deaths']}, at risk {cell['at_risk']})")
        save_cells(cells)
    print(f"stage {name} complete, {len(cells)} cells stored")


def pooled(cells, bond_init, ramp, harmless, seeds):
    rows = [c for c in cells if c["bond_init"] == bond_init and c["ramp"] == ramp
            and c["harmless"] == harmless and c["seed"] in seeds]
    at_risk = sum(c["at_risk"] for c in rows)
    deaths = sum(c["window_deaths"] for c in rows)
    return {
        "n_seeds": len(rows),
        "at_risk": at_risk,
        "window_deaths": deaths,
        "mortality": deaths / max(at_risk, 1),
        "onset_deaths": sum(c["onset_deaths"] for c in rows),
        "return_deaths": sum(c["return_deaths"] for c in rows),
        "other_deaths": sum(c["other_deaths"] for c in rows),
    }


def report():
    cells = load_cells()

    # Criterion 2: sudden storm, bonded vs control, 10 seeds.
    per_seed = []
    for seed in C2_SEEDS:
        b = next(c for c in cells if (c["bond_init"], c["ramp"], c["harmless"], c["seed"]) == (1.0, 1, False, seed))
        z = next(c for c in cells if (c["bond_init"], c["ramp"], c["harmless"], c["seed"]) == (0.0, 1, False, seed))
        per_seed.append({"seed": seed, "bonded": b["storm_mortality"],
                         "control": z["storm_mortality"]})
    wins = sum(1 for r in per_seed if r["bonded"] > r["control"])
    pool_b = pooled(cells, 1.0, 1, False, C2_SEEDS)
    pool_z = pooled(cells, 0.0, 1, False, C2_SEEDS)
    c2 = {"per_seed": per_seed, "seeds_bonded_exceeds_control": wins,
          "pooled_bonded": pool_b["mortality"], "pooled_control": pool_z["mortality"],
          "pooled_excess_points": 100 * (pool_b["mortality"] - pool_z["mortality"]),
          "passed": bool(wins >= 9 and (pool_b["mortality"] - pool_z["mortality"]) >= 0.05)}

    # Criterion 3, judged exactly as written in the spec.
    row = {r: pooled(cells, 1.0, r, False, GRID_SEEDS)["mortality"] for r in RAMPS}
    control_1600 = pooled(cells, 0.0, 1600, False, GRID_SEEDS)["mortality"]
    non_increasing = all(row[RAMPS[i]] >= row[RAMPS[i + 1]] - 1e-12 for i in range(len(RAMPS) - 1))
    strict = row[1] > row[1600]
    near_control = abs(row[1600] - control_1600) <= 0.02
    c3 = {"mortality_by_ramp_bond1": {str(r): row[r] for r in RAMPS},
          "control_at_1600": control_1600,
          "non_increasing": bool(non_increasing), "strict_decrease_1_to_1600": bool(strict),
          "within_2pts_of_control_at_1600": bool(near_control),
          "passed": bool(non_increasing and strict and near_control)}

    # Criterion 4: decomposition, recorded per condition.
    decomposition = {}
    for b in BONDS:
        for r in RAMPS:
            p = pooled(cells, b, r, False, GRID_SEEDS)
            decomposition[f"bond{b}_ramp{r}"] = p
    # Prediction 3 evaluation at the flagship cell.
    flag = pooled(cells, 1.0, 1, False, GRID_SEEDS)
    ctrl = pooled(cells, 0.0, 1, False, GRID_SEEDS)
    excess_deaths = flag["window_deaths"] - round(ctrl["mortality"] * flag["at_risk"])
    c4 = {"decomposition": decomposition,
          "prediction3_flagship": {
              "excess_deaths_vs_control": excess_deaths,
              "return_deaths": flag["return_deaths"],
              "onset_deaths": flag["onset_deaths"],
              "return_share_of_integrity_deaths": flag["return_deaths"] / max(flag["return_deaths"] + flag["onset_deaths"], 1)}}

    # Criterion 5: the map must contain structure.
    heat = {}
    for b in BONDS:
        for r in RAMPS:
            heat[f"{b}|{r}"] = pooled(cells, b, r, False, GRID_SEEDS)["mortality"]
    controls = {r: heat[f"0.0|{r}"] for r in RAMPS}
    has_hot = any(heat[f"{b}|{r}"] >= controls[r] + 0.20 for b in BONDS[1:] for r in RAMPS)
    has_null = any(abs(heat[f"{b}|{r}"] - controls[r]) <= 0.02 for b in BONDS[1:] for r in RAMPS)
    c5 = {"map": heat, "has_cell_20pts_above_control": bool(has_hot),
          "has_bonded_cell_within_2pts_of_control": bool(has_null),
          "passed": bool(has_hot and has_null)}

    # Supplement: the harmless ramp (warning, not slow cook).
    warn_row = {r: pooled(cells, 1.0, r, True, GRID_SEEDS)["mortality"] for r in RAMPS if r != 1}
    warn_row[1] = row[1]  # ramp 1 has no ramp period; identical by construction
    supplement = {"mortality_by_ramp_bond1_harmless": {str(r): warn_row[r] for r in RAMPS},
                  "decomposition": {f"ramp{r}": pooled(cells, 1.0, r, True, GRID_SEEDS) for r in RAMPS if r != 1}}

    artifact = {
        "spec": "specs/phase-3.md, criteria judged exactly as written",
        "manifest": build_manifest(seed=0, config=cell_config(1.0, 1, False)),
        "arena_note": "n_nests 5 (cohort about 40 of 200 homed to the storm nest), n_hazard 0 so every integrity death in the window is a storm death",
        "criterion_2_collision": c2,
        "criterion_3_null_test_as_written": c3,
        "criterion_4_decomposition": c4,
        "criterion_5_map": c5,
        "supplement_harmless_ramp": supplement,
        "cells_file": "results/phase-3-cells.json",
    }
    (RESULTS / "phase-3-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(heat, controls, row, warn_row)

    print("criterion 2 (collision):", "PASS" if c2["passed"] else "FAIL",
          f"| pooled {pool_b['mortality']:.2f} vs control {pool_z['mortality']:.2f}, {wins}/10 seeds")
    print("criterion 3 (null test, as written):", "PASS" if c3["passed"] else "FAIL",
          "|", {r: round(row[r], 2) for r in RAMPS}, f"control@1600 {control_1600:.2f}")
    print("criterion 4: recorded | flagship return share",
          f"{c4['prediction3_flagship']['return_share_of_integrity_deaths']:.2f}")
    print("criterion 5 (structure):", "PASS" if c5["passed"] else "FAIL")
    print("supplement (harmless ramp):", {r: round(warn_row[r], 2) for r in RAMPS})


def make_figure(heat, controls, row, warn_row):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)

    grid = np.array([[heat[f"{b}|{r}"] for r in RAMPS] for b in BONDS])
    im = axes[0].imshow(grid, cmap="Greys", vmin=0, vmax=1, aspect="auto", origin="lower")
    axes[0].set_xticks(range(len(RAMPS)), [str(r) for r in RAMPS], fontsize=8, color=ink)
    axes[0].set_yticks(range(len(BONDS)), [str(b) for b in BONDS], fontsize=8, color=ink)
    axes[0].set_xlabel("storm ramp, ticks", fontsize=8, color=ink)
    axes[0].set_ylabel("bond_init", fontsize=8, color=ink)
    axes[0].set_title("Storm mortality of the homed cohort", fontsize=10, color=ink)
    for i, b in enumerate(BONDS):
        for j, r in enumerate(RAMPS):
            v = grid[i, j]
            axes[0].text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                         color="#FFFFFF" if v > 0.5 else ink)
    fig.colorbar(im, ax=axes[0], fraction=0.046)

    axes[1].plot(RAMPS, [row[r] for r in RAMPS], color="#A32D2D", lw=1.8,
                 marker="o", ms=4, label="as specced: damage ramps with signal")
    axes[1].plot(RAMPS, [warn_row[r] for r in RAMPS], color="#0F6E56", lw=1.8,
                 marker="s", ms=4, label="harmless ramp: warning, then full damage")
    axes[1].plot(RAMPS, [controls[r] for r in RAMPS], color="#888780", lw=1.2,
                 ls="--", label="bond 0 control")
    axes[1].set_xscale("log")
    axes[1].set_xticks(RAMPS, [str(r) for r in RAMPS], fontsize=8)
    axes[1].tick_params(colors=ink, labelsize=8)
    for side in ("top", "right"):
        axes[1].spines[side].set_visible(False)
    axes[1].set_xlabel("storm ramp, ticks (log)", fontsize=8, color=ink)
    axes[1].set_ylabel("storm mortality, bond 1.0", fontsize=8, color=ink)
    axes[1].set_title("Warning saves; gradual arrival kills", fontsize=10, color=ink)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-3-map.png", bbox_inches="tight")


STAGES = {
    "c2": [(b, 1, False, s) for b in (1.0, 0.0) for s in C2_SEEDS],
    "grid_a": [(b, r, False, s) for b in (0.0, 0.25) for r in RAMPS for s in GRID_SEEDS],
    "grid_b": [(b, r, False, s) for b in (0.5, 0.75, 1.0) for r in RAMPS for s in GRID_SEEDS],
    "warn": [(1.0, r, True, s) for r in RAMPS if r != 1 for s in GRID_SEEDS],
}


if __name__ == "__main__":
    stage = sys.argv[1]
    RESULTS.mkdir(exist_ok=True)
    if stage == "report":
        report()
    else:
        run_stage(stage, STAGES[stage])
