"""Phase 1 validation. Produces the phase-gate artifacts under results/:

  phase-1-homeostasis.json     acceptance criterion 2
  phase-1-lag-validation.json  acceptance criterion 3
  phase-1-lag-validation.png   the step-response figure

Every reported number carries the seed and config hash that produced it
(CLAUDE.md). Run:  uv run python scripts/validate_phase1.py
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.action import ACTION_NAMES  # noqa: E402
from core.config import Config  # noqa: E402
from core.drives import DRIVE_NAMES  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model, run  # noqa: E402

RESULTS = pathlib.Path(__file__).resolve().parents[1] / "results"

TAUS = {"energy": "tau_energy", "safety": "tau_safety", "rest": "tau_rest"}


def homeostasis():
    """Criterion 2: default config, 200 agents, 5000 ticks, 10 seeds."""
    cfg = Config()
    per_seed = []
    for seed in range(1, 11):
        traj = run(cfg, seed=seed, ticks=5000)
        ticks = np.array(traj["tick"])
        alive = traj["alive"]
        # Population mean energy over living agents, per recorded frame
        # after tick 500.
        late = ticks >= 500
        mean_energy = [
            float(traj["energy"][k][alive[k]].mean())
            for k in np.flatnonzero(late)
        ]
        curve_at = [0, 1000, 2000, 3000, 4000, 5000]
        per_seed.append({
            "seed": seed,
            "survivors": int(alive[-1].sum()),
            "survival_rate": float(alive[-1].mean()),
            "mean_energy_min": min(mean_energy),
            "mean_energy_max": max(mean_energy),
            "alive_curve": {t: int(alive[np.flatnonzero(ticks == t)[0]].sum()) for t in curve_at},
        })
        print(f"  seed {seed}: {per_seed[-1]['survivors']}/200 alive, "
              f"mean energy [{per_seed[-1]['mean_energy_min']:.3f}, {per_seed[-1]['mean_energy_max']:.3f}]")

    # Behavioural profile on seed 1 so the artifact shows the homeostat
    # is foraging and fleeing, not degenerate-resting.
    model = Model(cfg, seed=1)
    counts = np.zeros(len(ACTION_NAMES), dtype=np.int64)
    for _ in range(2000):
        living = model.arrays.alive.copy()
        actions = model.step()
        counts += np.bincount(actions[living], minlength=len(ACTION_NAMES))
    profile = {name: float(c / counts.sum()) for name, c in zip(ACTION_NAMES, counts)}

    worst = min(s["survival_rate"] for s in per_seed)
    lo = min(s["mean_energy_min"] for s in per_seed)
    hi = max(s["mean_energy_max"] for s in per_seed)
    passed = worst >= 0.95 and lo >= 0.4 and hi <= 0.97
    artifact = {
        "criterion": "phase-1 acceptance 2: >=95% survival at 5000 ticks, "
                     "population mean energy in [0.4, 0.97] after tick 500",
        "manifest": build_manifest(seed=0, config=cfg),
        "seeds": list(range(1, 11)),
        "per_seed": per_seed,
        "worst_survival_rate": worst,
        "mean_energy_envelope": [lo, hi],
        "action_profile_seed1_first2000": profile,
        "passed": bool(passed),
    }
    (RESULTS / "phase-1-homeostasis.json").write_text(json.dumps(artifact, indent=2) + "\n")
    return artifact


def _fit_discrete_decay(series, floor=1e-10):
    """Fit ln(series) against t. The update law is discrete, so the
    per-tick decay factor is (1 - 1/tau) exactly; fitting the discrete
    form recovers tau without the ~4% continuous-exponential bias.
    `floor` excludes the tail where the decaying gap falls into the
    noise of any slow drift in the input. Returns tau_hat."""
    t = np.arange(len(series))
    keep = series > floor
    slope = np.polyfit(t[keep], np.log(series[keep]), 1)[0]
    return 1.0 / (1.0 - np.exp(slope))


def lag_safety_step():
    """Criterion 3a: hazard onset under a near-uniform danger field;
    w_safety must rise as (1 - (1 - 1/tau)^t) toward the plateau."""
    cfg = replace(
        Config(), n_agents=50, n_hazard=1, r_hazard=10000.0, hazard_drift=0.0,
        damage_rate=0.0, basal_burn=0.0, move_burn=0.0, hazard_onset=100,
        record_every=1,
    )
    seed = 202607
    traj = run(cfg, seed=seed, ticks=400)
    w = traj["weights"][:, :, 1]          # (frames, agents) safety weight
    u = traj["urgency"][:, :, 1]
    onset = 100
    plateau = w[-1]                        # 25 tau past onset; fully relaxed
    gap = plateau[None, :] - w[onset:, :]  # decays by (1-1/tau) per tick
    # Fit the first ~3 tau only, above a 0.05 floor: agents flee outward
    # during measurement so their danger (the input) drifts by ~0.3%,
    # which contaminates the tail of the decay but not the early gap.
    tau_hat = np.median(
        [_fit_discrete_decay(gap[:36, i], floor=0.05) for i in range(w.shape[1])]
    )
    curve = {
        "tick": [int(t) for t in traj["tick"]],
        "mean_w_safety": [float(v) for v in w.mean(axis=1)],
        "mean_u_safety": [float(v) for v in u.mean(axis=1)],
    }
    return seed, cfg, float(tau_hat), curve


def lag_energy_step():
    """Criterion 3b: with zero burn, the first bite fills energy to 1.0
    and steps u_energy to 0; w_energy must decay by (1 - 1/tau)."""
    cfg = replace(
        Config(), n_agents=50, n_hazard=0, basal_burn=0.0, move_burn=0.0,
        n_food=400, record_every=1,
    )
    seed = 202608
    traj = run(cfg, seed=seed, ticks=300)
    energy = traj["energy"]
    w = traj["weights"][:, :, 0]
    fits, aligned = [], []
    for i in range(w.shape[1]):
        full = np.flatnonzero(energy[:, i] >= 1.0)
        if len(full) == 0 or full[0] > 100:
            continue
        series = w[full[0]:, i]
        fits.append(_fit_discrete_decay(series[:60]))
        aligned.append(series[:120])
    tau_hat = float(np.median(fits))
    k = min(len(a) for a in aligned)
    mean_decay = np.mean([a[:k] for a in aligned], axis=0)
    curve = {"tick_since_bite": list(range(k)),
             "mean_w_energy": [float(v) for v in mean_decay]}
    return seed, cfg, tau_hat, curve


def lag_residual_identity():
    """Criterion 3c: on a default-config run, every recorded weight
    transition of every living agent must satisfy
    w[t] - w[t-1] = (u[t] - w[t-1]) / tau exactly, for all three
    drives. Any code path bypassing the uniform law would break this."""
    cfg = replace(Config(), record_every=1)
    seed = 1
    traj = run(cfg, seed=seed, ticks=500)
    w, u, alive = traj["weights"], traj["urgency"], traj["alive"]
    out = {}
    for d, name in enumerate(DRIVE_NAMES):
        tau = getattr(cfg, TAUS[name])
        dw = w[1:, :, d] - w[:-1, :, d]
        gap = u[1:, :, d] - w[:-1, :, d]
        live = alive[1:]
        residual = np.abs(dw[live] - gap[live] / tau)
        tau_hat = float(np.sum(gap[live] ** 2) / np.sum(gap[live] * dw[live]))
        out[name] = {
            "declared_tau": tau,
            "regressed_tau": tau_hat,
            "max_abs_residual": float(residual.max()),
            "transitions_checked": int(live.sum()),
        }
    return seed, cfg, out


def make_figure(safety_curve, safety_tau_hat, energy_curve, energy_tau_hat):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, accent, signal = "#444441", "#0F6E56", "#A32D2D"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), dpi=150)
    for ax in axes:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=ink, labelsize=8)

    t = safety_curve["tick"]
    axes[0].plot(t, safety_curve["mean_u_safety"], color=signal, lw=1.2,
                 label="urgency (instant)")
    axes[0].plot(t, safety_curve["mean_w_safety"], color=accent, lw=1.8,
                 label="weight (lagged)")
    axes[0].axvline(100, color=ink, lw=0.6, ls=":")
    axes[0].set_title(
        f"safety: hazard onset at t=100, fitted tau {safety_tau_hat:.2f} "
        f"(declared 12)", fontsize=9, color=ink)
    axes[0].set_xlabel("tick", fontsize=8, color=ink)
    axes[0].legend(frameon=False, fontsize=8)

    ts = energy_curve["tick_since_bite"]
    axes[1].plot(ts, energy_curve["mean_w_energy"], color=accent, lw=1.8,
                 label="weight (lagged)")
    axes[1].plot(ts, energy_curve["mean_w_energy"][0]
                 * (1 - 1 / 20.0) ** np.arange(len(ts)),
                 color=ink, lw=1.0, ls="--", label="declared-tau theory")
    axes[1].set_title(
        f"energy: hunger satisfied at t=0, fitted tau {energy_tau_hat:.2f} "
        f"(declared 20)", fontsize=9, color=ink)
    axes[1].set_xlabel("ticks since first bite", fontsize=8, color=ink)
    axes[1].legend(frameon=False, fontsize=8)

    fig.suptitle("The lag is real and measurable: weights chase urgencies "
                 "through w += (u - w)/tau", fontsize=10, color=ink)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-1-lag-validation.png", bbox_inches="tight")


def main():
    RESULTS.mkdir(exist_ok=True)
    print("homeostasis (criterion 2):")
    homeo = homeostasis()
    print(f"  -> passed: {homeo['passed']}")

    print("lag validation (criterion 3):")
    s_seed, s_cfg, s_tau, s_curve = lag_safety_step()
    e_seed, e_cfg, e_tau, e_curve = lag_energy_step()
    r_seed, r_cfg, residuals = lag_residual_identity()
    err_s = abs(s_tau - 12.0) / 12.0
    err_e = abs(e_tau - 20.0) / 20.0
    print(f"  safety step:  tau_hat {s_tau:.3f} vs 12 ({err_s:.2%})")
    print(f"  energy step:  tau_hat {e_tau:.3f} vs 20 ({err_e:.2%})")
    for name, r in residuals.items():
        print(f"  identity {name:7s}: regressed tau {r['regressed_tau']:.4f} "
              f"vs {r['declared_tau']}, max residual {r['max_abs_residual']:.2e}, "
              f"{r['transitions_checked']} transitions")
    passed = (
        err_s < 0.05 and err_e < 0.05
        and all(abs(r["regressed_tau"] - r["declared_tau"]) / r["declared_tau"] < 0.001
                for r in residuals.values())
        and all(r["max_abs_residual"] < 1e-9 for r in residuals.values())
    )
    artifact = {
        "criterion": "phase-1 acceptance 3: fitted tau within 5% (step protocols); "
                     "regressed tau within 0.1% and max residual < 1e-9 (identity)",
        "step_protocols": {
            "safety": {"seed": s_seed, "config_hash": s_cfg.config_hash(),
                       "declared_tau": 12.0, "fitted_tau": s_tau,
                       "relative_error": err_s},
            "energy": {"seed": e_seed, "config_hash": e_cfg.config_hash(),
                       "declared_tau": 20.0, "fitted_tau": e_tau,
                       "relative_error": err_e},
        },
        "transition_identity": {"seed": r_seed, "config_hash": r_cfg.config_hash(),
                                 "per_drive": residuals},
        "manifest": build_manifest(seed=0, config=Config()),
        "passed": bool(passed),
        "curves": {"safety_step": s_curve, "energy_decay": e_curve},
    }
    (RESULTS / "phase-1-lag-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(s_curve, s_tau, e_curve, e_tau)
    print(f"  -> passed: {passed}")
    print("artifacts written to results/")


if __name__ == "__main__":
    main()
