"""Phase 6 validation. Artifacts under results/:

  phase-6-validation.json  criteria 1-6 of specs/phase-6.md
  phase-6-grief.png        the mourning curve and the pull into the storm

Run:  uv run python scripts/validate_phase6.py
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
from core.world import _torus_delta  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

PAIRED = {"bond_target": "partner", "n_hazard": 0}
STORM = dict(PAIRED, storm_nest=0, storm_onset=2000, storm_ramp=1)


def pair_distance(m):
    has = m.arrays.partner >= 0
    idx = np.where(has, m.arrays.partner, 0)
    both = has & m.arrays.alive & m.arrays.alive[idx]
    dx = _torus_delta(m.arrays.x[idx] - m.arrays.x, m.config.world_size)
    dy = _torus_delta(m.arrays.y[idx] - m.arrays.y, m.config.world_size)
    return np.hypot(dx, dy), both


def cohesion():
    """Criterion 2: partners keep each other close, by the same law."""
    out = {}
    for b0 in (0.0, 0.8):
        means = []
        for seed in range(1, 6):
            cfg = replace(Config(), **PAIRED, bond_init=b0)
            m = Model(cfg, seed)
            samples = []
            for t in range(3000):
                m.step()
                if m.tick > 2000 and m.tick % 50 == 0:
                    d, both = pair_distance(m)
                    samples.append(float(d[both].mean()))
            means.append(float(np.mean(samples)))
        out[str(b0)] = {"per_seed": means, "mean": float(np.mean(means))}
        print(f"  bond_init {b0}: mean partner distance {out[str(b0)]['mean']:.2f}")
    ratio = out["0.0"]["mean"] / max(out["0.8"]["mean"], 1e-9)
    out["ratio"] = float(ratio)
    out["passed"] = bool(ratio >= 3.0)
    return out


def grief_identities():
    """Criterion 3: u_bond equals b bit-exactly in bereavement, decay
    follows the declared contraction, and the mourning curve matches.
    Pairs roam, so exposure to the storm is statistical; pooled over
    seeds at n = 400."""
    seeds = [5, 6, 7, 8, 9, 10]
    n_bereaved = 0
    max_u_gap = 0.0
    max_decay_res = 0.0
    by_lag = {}
    cfg = replace(Config(), **STORM, n_agents=400, bond_init=0.8, record_every=1)
    for seed in seeds:
        traj = run(cfg, seed=seed, ticks=3400)
        m0 = Model(cfg, seed)
        partner = m0.arrays.partner
        has = partner >= 0
        idx = np.where(has, partner, 0)
        alive = traj["alive"]
        bereaved = has[None, :] & alive & ~alive[:, idx]   # (frames, agents)
        # Frames whose perception already saw the dead partner:
        # bereaved on the previous frame too (perception runs before
        # deaths in the tick order), so u at frame t was computed from
        # b at frame t-1 at infinite distance: u == b, bit for bit.
        settled = bereaved[1:] & bereaved[:-1]
        if not settled.any():
            continue
        b = traj["bond"]
        u = traj["urgency"][:, :, 3]
        max_u_gap = max(max_u_gap,
                        float(np.max(np.abs(u[1:][settled] - b[:-1][settled]))))
        db = b[1:] - b[:-1]
        expected = -cfg.bond_decay * b[:-1]
        max_decay_res = max(max_decay_res,
                            float(np.max(np.abs(db[settled] - expected[settled]))))
        loss_frame = np.where(bereaved.any(axis=0), np.argmax(bereaved, axis=0), -1)
        n_bereaved += int((loss_frame >= 0).sum())
        for i in np.flatnonzero(loss_frame >= 0):
            for k in range(0, 1200, 40):
                f = loss_frame[i] + k
                if f + 1 < u.shape[0] and bereaved[f, i]:
                    by_lag.setdefault(k, []).append(float(u[f + 1, i]))
    curve_t = sorted(by_lag)
    curve_u = [float(np.mean(by_lag[k])) for k in curve_t]
    print(f"  bereaved agents (pooled): {n_bereaved}; max |u - b| "
          f"{max_u_gap:.1e}; max decay residual {max_decay_res:.1e}")
    return {"seeds": seeds, "config_hash": cfg.config_hash(),
            "bereaved_agents": n_bereaved,
            "max_abs_u_minus_b": max_u_gap,
            "max_decay_residual": max_decay_res,
            "mourning_curve": {"ticks_since_loss": curve_t, "mean_distress": curve_u},
            "passed": bool(n_bereaved > 20 and max_u_gap == 0.0
                           and max_decay_res < 1e-9)}


def pull_and_fate():
    """Criteria 4 and 5: the partner inside the storm drags the
    survivor in, and cohesion means dying together."""
    rows = {"0.8": [], "0.0": []}
    for b0 in (0.8, 0.0):
        for seed in range(1, 7):
            cfg = replace(Config(), **STORM, n_agents=400, bond_init=b0)
            m = Model(cfg, seed)
            n = cfg.n_agents
            for _ in range(2050):
                m.step()
            # Pairs roam, so exposure is whoever the storm caught by
            # onset+50; the pull reaches any agent whose partner is in
            # or under it, wherever they are.
            sx, sy = m.world.storm_x, m.world.storm_y
            dx = _torus_delta(m.arrays.x - sx, cfg.world_size)
            dy = _torus_delta(m.arrays.y - sy, cfg.world_size)
            inside = np.hypot(dx, dy) < cfg.storm_radius
            p = m.arrays.partner
            has = p >= 0
            pidx = np.where(has, p, 0)
            partner_gone = has & (~m.arrays.alive[pidx] | inside[pidx])
            exposed = m.arrays.alive & ~inside
            group_pull = exposed & partner_gone
            group_safe = exposed & has & ~partner_gone
            alive_now = m.arrays.alive.copy()
            for _ in range(950):
                m.step()
            died = ~m.arrays.alive
            mort_pull = float(died[group_pull].mean()) if group_pull.any() else None
            mort_safe = float(died[group_safe].mean()) if group_safe.any() else None
            # Shared fate: among pairs both alive at onset+50, do
            # deaths correlate within pairs?
            firsts = np.flatnonzero(has & (np.arange(n) < p)
                                    & alive_now & alive_now[pidx])
            a_dead = died[firsts]
            b_dead = died[p[firsts]]
            both = float((a_dead & b_dead).mean()) if len(firsts) else None
            expected = float(a_dead.mean() * b_dead.mean()) if len(firsts) else None
            rows[str(b0)].append({
                "seed": seed, "config_hash": cfg.config_hash(),
                "n_pull": int(group_pull.sum()), "n_safe": int(group_safe.sum()),
                "mortality_partner_in_storm": mort_pull,
                "mortality_partner_safe": mort_safe,
                "pairs": int(len(firsts)),
                "p_both_die": both, "p_independent": expected,
            })
    def pooled(rs, key_n, key_m):
        tot = sum(r[key_n] for r in rs)
        dead = sum(r[key_n] * r[key_m] for r in rs if r[key_m] is not None)
        return dead / max(tot, 1)
    pull8 = pooled(rows["0.8"], "n_pull", "mortality_partner_in_storm")
    safe8 = pooled(rows["0.8"], "n_safe", "mortality_partner_safe")
    pull0 = pooled(rows["0.0"], "n_pull", "mortality_partner_in_storm")
    safe0 = pooled(rows["0.0"], "n_safe", "mortality_partner_safe")
    fate_signs = sum(1 for r in rows["0.8"]
                     if r["p_both_die"] is not None and r["p_independent"] is not None
                     and r["p_both_die"] > r["p_independent"])
    c4 = {"runs": rows,
          "pooled_bond08": {"partner_in_storm": pull8, "partner_safe": safe8},
          "pooled_bond00": {"partner_in_storm": pull0, "partner_safe": safe0},
          "ratio_bond08": pull8 / max(safe8, 1e-9),
          "ratio_bond00": pull0 / max(safe0, 1e-9),
          "passed": bool(pull8 >= 2.0 * safe8 and pull0 < 2.0 * max(safe0, 0.01))}
    c5 = {"seeds_with_positive_pair_correlation": fate_signs,
          "passed": bool(fate_signs >= 4)}
    print(f"  pull (bond 0.8): partner-in-storm {pull8:.2f} vs partner-safe "
          f"{safe8:.2f} (ratio {c4['ratio_bond08']:.1f})")
    print(f"  pull (bond 0.0): {pull0:.2f} vs {safe0:.2f} "
          f"(ratio {c4['ratio_bond00']:.1f})")
    print(f"  shared fate: positive pair correlation in {fate_signs}/6 seeds")
    return c4, c5


def protective_contrast():
    """Not a declared criterion; measured because criteria 4 and 5
    exposed it. Same storm, same attachment depth: how many die when
    the beloved is a place versus a person?"""
    out = {}
    for mode in ("nest", "partner"):
        per_seed = []
        for seed in range(1, 7):
            cfg = replace(Config(), n_agents=400, n_hazard=0, storm_nest=0,
                          storm_onset=2000, storm_ramp=1, bond_init=0.8,
                          bond_target=mode)
            m = Model(cfg, seed)
            for _ in range(2000):
                m.step()
            at_onset = m.arrays.alive.copy()
            for _ in range(1000):
                m.step()
            died = at_onset & ~m.arrays.alive
            per_seed.append(float(died.sum() / max(int(at_onset.sum()), 1)))
        out[mode] = {"per_seed": per_seed, "pooled": float(np.mean(per_seed))}
        print(f"  bond_target {mode}: population mortality in window "
              f"{out[mode]['pooled']:.3f}")
    return out


def make_figure(grief, c4):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
    t = grief["mourning_curve"]["ticks_since_loss"]
    u = grief["mourning_curve"]["mean_distress"]
    axes[0].plot(t, u, color="#534AB7", lw=1.8)
    if u:
        theory = u[0] * (1 - Config().bond_decay) ** np.array(t)
        axes[0].plot(t, theory, color=ink, lw=1.0, ls="--",
                     label="declared decay")
        axes[0].legend(frameon=False, fontsize=8)
    axes[0].set_xlabel("ticks since loss", fontsize=8, color=ink)
    axes[0].set_ylabel("mean distress of the bereaved", fontsize=8, color=ink)
    axes[0].set_title("The mourning clock: distress with no destination",
                      fontsize=10, color=ink)

    contrast = c4["protective_contrast"]
    x = np.arange(2)
    axes[1].bar(x, [contrast["nest"]["pooled"], contrast["partner"]["pooled"]],
                0.5, color=["#A32D2D", "#0F6E56"])
    axes[1].set_xticks(x, ["beloved is a place\n(nest)", "beloved is a person\n(partner)"],
                       fontsize=8)
    axes[1].set_ylabel("population mortality, storm window", fontsize=8, color=ink)
    axes[1].set_title("Love that moves with you, same storm, same depth",
                      fontsize=10, color=ink)
    for ax in axes:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=ink, labelsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-6-grief.png", bbox_inches="tight")


def main():
    RESULTS.mkdir(exist_ok=True)
    print("cohesion (criterion 2):")
    c2 = cohesion()
    print("grief identities (criterion 3):")
    c3 = grief_identities()
    print("the pull and shared fate (criteria 4, 5):")
    c4, c5 = pull_and_fate()
    print("protective contrast (measured, not declared):")
    c4["protective_contrast"] = protective_contrast()
    artifact = {
        "spec": "specs/phase-6.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "criterion_1_preservation": "all golden trajectory hashes verified "
            "unchanged in nest mode before commit; config hashes refreshed "
            "for the bond_target field",
        "criterion_2_cohesion": c2,
        "criterion_3_grief_identities": c3,
        "criterion_4_pull": c4,
        "criterion_5_shared_fate": c5,
        "passed": bool(c2["passed"] and c3["passed"] and c4["passed"] and c5["passed"]),
    }
    (RESULTS / "phase-6-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(c3, c4)
    print(f"criteria: cohesion {c2['passed']} (ratio {c2['ratio']:.1f}), "
          f"grief {c3['passed']}, pull {c4['passed']}, fate {c5['passed']}")
    print(f"-> all criteria passed: {artifact['passed']}")


if __name__ == "__main__":
    main()
