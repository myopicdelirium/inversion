"""Phase 11 validation: farsight. Artifacts under results/:

  phase-11-farsight.json  Q1-Q5 of specs/phase-11.md, judged as written
  phase-11-farsight.png   the frog with foresight, and Q3's answer

Run:
  uv run python scripts/validate_phase11.py main
  uv run python scripts/validate_phase11.py replicate   (fresh seeds)
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

PLACE = {"n_hazard": 0, "storm_nest": 0, "storm_onset": 2000}
MIRE = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
        "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
        "storm_snare": 0.95, "storm_damage": 0.01}


def frog(h, seeds):
    """Slow cook, bond 1.0, kappa 0, at horizon h: cohort mortality."""
    deaths = at_risk = 0
    for seed in seeds:
        cfg = replace(Config(), **PLACE, storm_ramp=400, bond_init=1.0,
                      prospect_horizon=h)
        traj = run(cfg, seed=seed, ticks=3000)
        ticks = np.array(traj["tick"])
        k = int(np.argmax(ticks >= 2000))
        cohort = (np.arange(cfg.n_agents) % cfg.n_nests) == 0
        risk = cohort & traj["alive"][k]
        deaths += int((risk & ~traj["alive"][-1]).sum())
        at_risk += int(risk.sum())
    return deaths / max(at_risk, 1), at_risk


def rescue(bond_init, h, seed):
    """Phase 8's mire experiment at horizon h."""
    cfg = replace(Config(), **MIRE, bond_init=bond_init, prospect_horizon=h)
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
    trapped = has & m.arrays.alive[pidx] & inside[pidx]
    safe_p = has & m.arrays.alive[pidx] & ~inside[pidx]
    outside = m.arrays.alive & ~inside
    g_pull = outside & trapped
    g_safe = outside & safe_p
    entered = np.zeros(n, dtype=bool)
    for _ in range(1200):
        m.step()
        entered |= m.arrays.alive & inside_now()
    died = ~m.arrays.alive
    return {"seed": seed, "config_hash": cfg.config_hash(),
            "n_pull": int(g_pull.sum()), "n_safe": int(g_safe.sum()),
            "deaths_pull": int((died & g_pull).sum()),
            "deaths_safe": int((died & g_safe).sum()),
            "pull_dead_entered": int((died & g_pull & entered).sum())}


def rescue_arm(bond_init, h, seeds):
    rows = [rescue(bond_init, h, s) for s in seeds]
    np_, ns = sum(r["n_pull"] for r in rows), sum(r["n_safe"] for r in rows)
    dp, ds = sum(r["deaths_pull"] for r in rows), sum(r["deaths_safe"] for r in rows)
    ent = sum(r["pull_dead_entered"] for r in rows)
    return {"runs": rows, "n_pull": np_, "n_safe": ns,
            "mortality_pull": dp / max(np_, 1), "mortality_safe": ds / max(ns, 1),
            "ratio": (dp / max(np_, 1)) / max(ds / max(ns, 1), 1e-9),
            "entered_share": ent / max(dp, 1)}


def stage_main():
    print("Q2: the frog with foresight (slow cook, bond 1.0)")
    q2 = {}
    for h in (0, 20, 60):
        m, risk = frog(h, range(1, 7))
        q2[str(h)] = {"mortality": m, "at_risk": risk}
        print(f"  h {h:>2}: cohort mortality {m:.3f} (at risk {risk})")
    q2["passed"] = bool(q2["60"]["mortality"] <= 0.5 * q2["0"]["mortality"])

    print("Q3: does inversion survive foresight? (mire, 30 seeds per arm)")
    q3 = {}
    for bond_init, h in ((0.8, 0), (0.8, 60), (0.0, 60)):
        key = f"bond{bond_init}_h{h}"
        q3[key] = rescue_arm(bond_init, h, range(1, 31))
        a = q3[key]
        print(f"  {key}: pull {a['mortality_pull']:.2f} (n {a['n_pull']}) vs "
              f"safe {a['mortality_safe']:.2f}, ratio {a['ratio']:.1f}, "
              f"entered share {a['entered_share']:.2f}")

    print("Q4: everyday null")
    q4 = {}
    for h in (0, 60):
        vals = [float(run(replace(Config(), prospect_horizon=h), seed=s,
                          ticks=5000)["alive"][-1].mean()) for s in range(1, 6)]
        q4[str(h)] = float(np.mean(vals))
        print(f"  h {h:>2}: survival {q4[str(h)]:.3f}")
    q4["passed"] = bool(abs(q4["0"] - q4["60"]) <= 0.03)

    artifact = {
        "spec": "specs/phase-11.md",
        "manifest": build_manifest(seed=0, config=Config()),
        "Q1_preservation": "all nine golden trajectories bit-identical at "
            "horizon 0 before commit; config hashes refreshed",
        "Q2_frog_with_foresight": q2,
        "Q3_inversion_under_foresight": q3,
        "Q4_everyday_null": q4,
        "Q5_reconstruction": "tests/test_farsight.py",
    }
    (RESULTS / "phase-11-farsight.json").write_text(json.dumps(artifact, indent=2) + "\n")
    print("main stage written")


def stage_replicate():
    declared = {
        "Q2R": "fresh seeds 11-16: h 60 slow-cook mortality at most half of h 0",
        "Q3R": "fresh seeds 31-60: same qualitative Q3 answer as seeds 1-30 "
               "(ratio on the same side of 1.5), entered share within 0.15",
    }
    out = {"declared_before_running": declared}
    q2 = {}
    for h in (0, 60):
        m, risk = frog(h, range(11, 17))
        q2[str(h)] = {"mortality": m, "at_risk": risk}
        print(f"  Q2R h {h}: {m:.3f}")
    out["Q2R"] = q2
    q3 = {}
    for bond_init, h in ((0.8, 60), (0.0, 60)):
        key = f"bond{bond_init}_h{h}"
        q3[key] = rescue_arm(bond_init, h, range(31, 61))
        a = q3[key]
        print(f"  Q3R {key}: pull {a['mortality_pull']:.2f} (n {a['n_pull']}) "
              f"vs safe {a['mortality_safe']:.2f}, ratio {a['ratio']:.1f}, "
              f"entered share {a['entered_share']:.2f}")
    out["Q3R"] = q3
    out["manifest"] = build_manifest(seed=0, config=Config())
    (RESULTS / "phase-11-replication.json").write_text(json.dumps(out, indent=2) + "\n")
    print("replication stage written")


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    {"main": stage_main, "replicate": stage_replicate}[sys.argv[1]]()
