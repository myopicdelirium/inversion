"""Phase 2 validation. Produces the phase-gate artifacts under results/:

  phase-2-validation.json   acceptance criteria 1-5
  phase-2-tethering.png     the tethering figure (criterion 4)

Every reported number carries the seed and config hash that produced it
(CLAUDE.md). Run:  uv run python scripts/validate_phase2.py
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.drives import DRIVE_NAMES  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model, array_hashes, run  # noqa: E402
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TAUS = {"energy": "tau_energy", "safety": "tau_safety", "rest": "tau_rest",
        "bond": "tau_bond"}


def homes_for(cfg, seed):
    """Home coordinates are set deterministically at init; a fresh
    un-stepped Model reproduces them for any recorded run."""
    m = Model(cfg, seed)
    return m.arrays.home_x.copy(), m.arrays.home_y.copy()


def dist_to_home(traj, home_x, home_y, world_size):
    # Per frame, per agent: torus distance from recorded position to
    # the agent's home.
    dx = _torus_delta(traj["x"] - home_x[None, :], world_size)
    dy = _torus_delta(traj["y"] - home_y[None, :], world_size)
    return np.hypot(dx, dy)


def preservation():
    """Criterion 1: no-nest world reproduces the phase 1 behavioural
    arrays bit for bit (also enforced permanently in tests/)."""
    spec = json.loads((ROOT / "tests/golden/phase1_default.json").read_text())
    cfg = replace(Config(), n_nests=0)
    traj = run(cfg, seed=spec["seed"], ticks=spec["ticks"])
    hashes = array_hashes(traj)
    names = ("x", "y", "energy", "integrity", "fatigue", "alive")
    matches = {n: hashes[n] == spec["array_sha256"][n] for n in names}
    print(f"  behavioural arrays identical: {all(matches.values())} ({names})")
    return {"config_hash": cfg.config_hash(), "seed": spec["seed"],
            "ticks": spec["ticks"], "matches": matches,
            "passed": all(matches.values())}


def accumulation_identity():
    """Criterion 2: every bond transition satisfies the declared law,
    grow form at home, decay form away."""
    cfg = replace(Config(), record_every=1)
    seed = 11
    traj = run(cfg, seed=seed, ticks=500)
    home_x, home_y = homes_for(cfg, seed)
    d = dist_to_home(traj, home_x, home_y, cfg.world_size)
    b = traj["bond"]
    db = b[1:] - b[:-1]
    prev = b[:-1]
    at_home = d[1:] < cfg.r_nest  # bond updates use post-move positions
    expected = np.where(at_home,
                        cfg.bond_grow * (1.0 - prev),
                        -cfg.bond_decay * prev)
    live = traj["alive"][1:]
    residual = np.abs(db[live] - expected[live])
    out = {"seed": seed, "config_hash": cfg.config_hash(),
           "transitions_checked": int(live.sum()),
           "max_abs_residual": float(residual.max()),
           "passed": bool(residual.max() < 1e-9)}
    print(f"  bond identity: max residual {out['max_abs_residual']:.2e} "
          f"over {out['transitions_checked']} transitions")
    return out


def weight_identity():
    """Criterion 3: the uniform law, exact, now over four drives."""
    cfg = replace(Config(), record_every=1)
    seed = 12
    traj = run(cfg, seed=seed, ticks=500)
    w, u, alive = traj["weights"], traj["urgency"], traj["alive"]
    out = {"seed": seed, "config_hash": cfg.config_hash(), "per_drive": {}}
    ok = True
    for i, name in enumerate(DRIVE_NAMES):
        tau = getattr(cfg, TAUS[name])
        dw = w[1:, :, i] - w[:-1, :, i]
        gap = u[1:, :, i] - w[:-1, :, i]
        live = alive[1:]
        residual = np.abs(dw[live] - gap[live] / tau)
        tau_hat = float(np.sum(gap[live] ** 2) / np.sum(gap[live] * dw[live]))
        rec = {"declared_tau": tau, "regressed_tau": tau_hat,
               "max_abs_residual": float(residual.max()),
               "transitions_checked": int(live.sum())}
        ok = ok and abs(tau_hat - tau) / tau < 0.001 and rec["max_abs_residual"] < 1e-9
        out["per_drive"][name] = rec
        print(f"  identity {name:7s}: regressed tau {tau_hat:.4f} vs {tau}, "
              f"max residual {rec['max_abs_residual']:.2e}")
    out["passed"] = bool(ok)
    return out


def tethering():
    """Criterion 4: mean distance-to-home over the final 1000 ticks is
    strictly decreasing in bond_init. Attachment tethers the foraging
    range; nothing in the code mentions territory."""
    inits = [0.0, 0.5, 1.0]
    seeds = [21, 22, 23]
    curves, out = {}, {}
    for b0 in inits:
        cfg = replace(Config(), bond_init=b0)
        per_seed, series = [], []
        for seed in seeds:
            traj = run(cfg, seed=seed, ticks=3000)
            home_x, home_y = homes_for(cfg, seed)
            d = dist_to_home(traj, home_x, home_y, cfg.world_size)
            alive = traj["alive"]
            mean_d = np.array([d[k][alive[k]].mean() for k in range(d.shape[0])])
            series.append(mean_d)
            ticks = np.array(traj["tick"])
            per_seed.append(float(mean_d[ticks >= 2000].mean()))
        curves[b0] = {"tick": [int(t) for t in ticks],
                      "mean_dist": [float(v) for v in np.mean(series, axis=0)]}
        out[str(b0)] = {"per_seed_final1000_mean": per_seed,
                        "mean": float(np.mean(per_seed)),
                        "config_hash": cfg.config_hash()}
        print(f"  bond_init {b0}: mean distance-to-home (final 1000 ticks) "
              f"{out[str(b0)]['mean']:.2f}")
    means = [out[str(b)]["mean"] for b in inits]
    passed = means[0] > means[1] > means[2]
    return {"seeds": seeds, "by_bond_init": out, "passed": bool(passed)}, curves


def homeostasis():
    """Criterion 5: the tethered world still keeps its agents alive."""
    cfg = Config()
    per_seed = []
    for seed in range(1, 6):
        traj = run(cfg, seed=seed, ticks=5000)
        ticks = np.array(traj["tick"])
        alive = traj["alive"]
        late = np.flatnonzero(ticks >= 500)
        mean_energy = [float(traj["energy"][k][alive[k]].mean()) for k in late]
        per_seed.append({"seed": seed, "survivors": int(alive[-1].sum()),
                         "mean_energy_min": min(mean_energy),
                         "mean_energy_max": max(mean_energy)})
        print(f"  seed {seed}: {per_seed[-1]['survivors']}/200 alive, mean energy "
              f"[{per_seed[-1]['mean_energy_min']:.3f}, {per_seed[-1]['mean_energy_max']:.3f}]")
    worst = min(s["survivors"] / cfg.n_agents for s in per_seed)
    lo = min(s["mean_energy_min"] for s in per_seed)
    hi = max(s["mean_energy_max"] for s in per_seed)
    return {"config_hash": cfg.config_hash(), "per_seed": per_seed,
            "worst_survival_rate": worst, "mean_energy_envelope": [lo, hi],
            "passed": bool(worst >= 0.95 and lo >= 0.4 and hi <= 0.97)}


def make_figure(curves):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    shades = {0.0: "#B4B2A9", 0.5: "#1D9E75", 1.0: "#085041"}
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=ink, labelsize=8)
    for b0, curve in curves.items():
        ax.plot(curve["tick"], curve["mean_dist"], color=shades[b0], lw=1.8)
        ax.annotate(f"bond_init {b0}", xy=(curve["tick"][-1], curve["mean_dist"][-1]),
                    xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=shades[b0], va="center")
    ax.set_xlabel("tick", fontsize=8, color=ink)
    ax.set_ylabel("mean distance to home", fontsize=8, color=ink)
    ax.set_xlim(0, 3600)
    ax.set_title("Attachment tethers the foraging range (3 seeds per curve)",
                 fontsize=10, color=ink)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-2-tethering.png", bbox_inches="tight")


def main():
    RESULTS.mkdir(exist_ok=True)
    print("preservation (criterion 1):")
    c1 = preservation()
    print("accumulation identity (criterion 2):")
    c2 = accumulation_identity()
    print("weight law identity (criterion 3):")
    c3 = weight_identity()
    print("tethering (criterion 4):")
    c4, curves = tethering()
    print("homeostasis (criterion 5):")
    c5 = homeostasis()
    artifact = {
        "spec": "specs/phase-2.md acceptance criteria 1-5",
        "manifest": build_manifest(seed=0, config=Config()),
        "criterion_1_preservation": c1,
        "criterion_2_accumulation_identity": c2,
        "criterion_3_weight_identity": c3,
        "criterion_4_tethering": c4,
        "criterion_5_homeostasis": c5,
        "passed": all(c["passed"] for c in (c1, c2, c3, c4, c5)),
    }
    (RESULTS / "phase-2-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(curves)
    print(f"-> all criteria passed: {artifact['passed']}")
    print("artifacts written to results/")


if __name__ == "__main__":
    main()
