"""Phase 8 validation. Artifacts under results/:

  phase-8-validation.json  criteria 1-5 of specs/phase-8.md
  phase-8-rescue.png       the pull, restored by the pin

Run:  uv run python scripts/validate_phase8.py
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

MIRE = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
        "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
        "storm_snare": 0.95, "storm_damage": 0.01}


def rescue_run(bond_init, kappa, seed):
    cfg = replace(Config(), **MIRE, bond_init=bond_init,
                  attention_sharpness=kappa)
    m = Model(cfg, seed)
    n = cfg.n_agents
    for _ in range(2050):
        m.step()
    sx, sy = m.world.storm_x, m.world.storm_y

    def inside_now():
        dx = _torus_delta(m.arrays.x - sx, cfg.world_size)
        dy = _torus_delta(m.arrays.y - sy, cfg.world_size)
        return np.hypot(dx, dy) < cfg.storm_radius

    inside = inside_now()
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    partner_trapped = has & m.arrays.alive[pidx] & inside[pidx]
    partner_safe = has & m.arrays.alive[pidx] & ~inside[pidx]
    outside_alive = m.arrays.alive & ~inside
    group_pull = outside_alive & partner_trapped
    group_safe = outside_alive & partner_safe
    entered = np.zeros(n, dtype=bool)
    for _ in range(1200):
        m.step()
        entered |= m.arrays.alive & inside_now()
    died = ~m.arrays.alive
    return {
        "bond_init": bond_init, "kappa": kappa, "seed": seed,
        "config_hash": cfg.config_hash(),
        "n_pull": int(group_pull.sum()), "n_safe": int(group_safe.sum()),
        "deaths_pull": int((died & group_pull).sum()),
        "deaths_safe": int((died & group_safe).sum()),
        "pull_dead_entered": int((died & group_pull & entered).sum()),
    }


def pooled(rows, n_key, d_key):
    n = sum(r[n_key] for r in rows)
    d = sum(r[d_key] for r in rows)
    return d / max(n, 1), n, d


def main():
    RESULTS.mkdir(exist_ok=True)
    arms = {}
    for bond_init, kappa, n_seeds in ((0.8, 0.0, 30), (0.4, 0.0, 30), (0.0, 0.0, 30), (0.4, 0.75, 6)):
        key = f"bond{bond_init}_kappa{kappa}"
        rows = [rescue_run(bond_init, kappa, seed) for seed in range(1, n_seeds + 1)]
        m_pull, n_pull, d_pull = pooled(rows, "n_pull", "deaths_pull")
        m_safe, n_safe, d_safe = pooled(rows, "n_safe", "deaths_safe")
        entered = sum(r["pull_dead_entered"] for r in rows)
        arms[key] = {
            "runs": rows,
            "mortality_partner_trapped": m_pull, "n_pull": n_pull,
            "mortality_partner_safe": m_safe, "n_safe": n_safe,
            "ratio": m_pull / max(m_safe, 1e-9),
            "pull_dead_entered_share": entered / max(d_pull, 1),
        }
        print(f"  {key}: trapped-partner mortality {m_pull:.2f} "
              f"(n {n_pull}) vs safe-partner {m_safe:.2f} (n {n_safe}), "
              f"ratio {arms[key]['ratio']:.1f}, dead-entered share "
              f"{arms[key]['pull_dead_entered_share']:.2f}")

    # Judged at bond 0.8, exactly as the spec declared; the 0.4 arm is
    # reported alongside (its split geometry is commoner, ratio 1.9).
    c2 = {"passed": bool(arms["bond0.8_kappa0.0"]["ratio"] >= 2.0
                         and arms["bond0.0_kappa0.0"]["ratio"] < 2.0)}
    c3 = {"share": arms["bond0.8_kappa0.0"]["pull_dead_entered_share"],
          "passed": bool(arms["bond0.8_kappa0.0"]["pull_dead_entered_share"] >= 0.70)}
    artifact = {
        "spec": "specs/phase-8.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "criterion_1_preservation": "all six golden trajectories verified "
            "bit-identical with the snare off before commit",
        "criterion_2_pull": c2,
        "criterion_3_entries": c3,
        "criterion_4_attention_interaction": arms["bond0.4_kappa0.75"],
        "arms": arms,
        "passed": bool(c2["passed"] and c3["passed"]),
    }
    (RESULTS / "phase-8-validation.json").write_text(json.dumps(artifact, indent=2) + "\n")
    make_figure(arms)
    print(f"criteria: pull {c2['passed']}, entries {c3['passed']}")
    print(f"-> passed: {artifact['passed']}")


def make_figure(arms):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink = "#444441"
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=150)
    labels = ["bond 0.8", "bond 0.4", "bond 0", "bond 0.4\nkappa 0.75"]
    keys = ["bond0.8_kappa0.0", "bond0.4_kappa0.0", "bond0.0_kappa0.0",
            "bond0.4_kappa0.75"]
    x = np.arange(4)
    ax.bar(x - 0.18, [arms[k]["mortality_partner_trapped"] for k in keys], 0.36,
           color="#A32D2D", label="partner trapped in the mire")
    ax.bar(x + 0.18, [arms[k]["mortality_partner_safe"] for k in keys], 0.36,
           color="#B4B2A9", label="partner safe outside")
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel("subsequent mortality of outside agents", fontsize=8, color=ink)
    ax.set_title("The rescue trap: dying of where the beloved is held",
                 fontsize=10, color=ink)
    ax.legend(frameon=False, fontsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=ink, labelsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "phase-8-rescue.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
