"""Individual forensics for phase 12: the tick-level record of one
clear-eyed agent, reconstructed from the deterministic run that
contains it. Artifact: results/phase-12-biography.json.

Run:  uv run python scripts/biography_phase12.py
"""

import json
import pathlib
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.action import ACTION_NAMES, RETURN_HOME  # noqa: E402
from core.config import Config  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta, perceive_partner  # noqa: E402
from scripts.validate_phase12 import seen_exposure  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

CFG = dict(bond_target="partner", n_agents=400, n_hazard=0, storm_nest=0,
           storm_onset=2000, storm_ramp=1, storm_snare=0.95,
           storm_damage=0.01, tau_safety=48.0, attention_sharpness=0.75,
           attention_floor=0.05, bond_init=0.8, prospect_horizon=20)
SEED = 11


def main():
    cfg = replace(Config(), **CFG)
    m = Model(cfg, SEED)
    for _ in range(2050):
        m.step()
    sx, sy = m.world.storm_x, m.world.storm_y

    def storm_dist(xs, ys):
        return np.hypot(_torus_delta(xs - sx, cfg.world_size),
                        _torus_delta(ys - sy, cfg.world_size))

    inside = storm_dist(m.arrays.x, m.arrays.y) < cfg.storm_radius
    p = m.arrays.partner
    has = p >= 0
    pidx = np.where(has, p, 0)
    pull = np.flatnonzero(m.arrays.alive & ~inside & has
                          & m.arrays.alive[pidx] & inside[pidx])

    records = {int(i): [] for i in pull}
    for _ in range(1200):
        actions = m.step()
        d_t, _, _ = perceive_partner(m.arrays, cfg)
        for i in pull:
            i = int(i)
            if not m.arrays.alive[i] and records[i] and records[i][-1]["alive"] is False:
                continue
            partner = int(p[i])
            sd = float(storm_dist(np.array([m.arrays.x[i]]),
                                  np.array([m.arrays.y[i]]))[0])
            danger = float(m._storm_intensity() * np.exp(-sd / cfg.storm_radius))
            row = {
                "tick": m.tick,
                "alive": bool(m.arrays.alive[i]),
                "action": ACTION_NAMES[int(actions[i])] if m.arrays.alive[i] else None,
                "dist_storm_center": round(sd, 2),
                "dist_partner": round(float(d_t[i]), 2) if np.isfinite(d_t[i]) else None,
                "danger": round(danger, 4),
                "energy": round(float(m.arrays.energy[i]), 4),
                "integrity": round(float(m.arrays.integrity[i]), 4),
                "bond": round(float(m.arrays.bond[i]), 4),
                "weights": [round(float(w), 4) for w in m.arrays.weights[i]],
                "partner_alive": bool(m.arrays.alive[partner]),
                "partner_integrity": round(float(m.arrays.integrity[partner]), 4),
            }
            if m.arrays.alive[i] and actions[i] == RETURN_HOME and np.isfinite(d_t[i]):
                v_eff = cfg.speed * (1.0 - m.arrays.fatigue[i] / 2.0)
                tdx = _torus_delta(m.arrays.x[partner] - m.arrays.x[i], cfg.world_size)
                tdy = _torus_delta(m.arrays.y[partner] - m.arrays.y[i], cfg.world_size)
                tn = max(np.hypot(tdx, tdy), 1e-12)
                sdx = _torus_delta(m.arrays.x[i] - sx, cfg.world_size)
                sdy = _torus_delta(m.arrays.y[i] - sy, cfg.world_size)
                sn = max(np.hypot(sdx, sdy), 1e-12)
                proj = (tdx / tn) * (sdx / sn) + (tdy / tn) * (sdy / sn)
                exposure = float(seen_exposure(
                    cfg, np.array([danger]), np.array([v_eff]),
                    np.array([proj]), cfg.storm_radius,
                    np.array([np.ceil(d_t[i] / v_eff)]), cfg.prospect_horizon)[0])
                row["seen_exposure"] = round(exposure, 2)
                row["seen_price_integrity"] = round(exposure * cfg.storm_damage, 4)
                row["clear_eyed"] = bool(exposure * cfg.storm_damage
                                         >= m.arrays.integrity[i])
            records[i].append(row)

    # The subject: flagged at least once, entered, and died.
    subject = None
    for i, rows in records.items():
        flagged = any(r.get("clear_eyed") for r in rows)
        died = any(not r["alive"] for r in rows)
        entered = any(r["alive"] and r["dist_storm_center"] < cfg.storm_radius
                      for r in rows)
        if flagged and died and entered:
            subject = i
            break
    assert subject is not None, "no flagged death in this run; wrong seed?"

    rows = records[subject]
    first_flag = next(r for r in rows if r.get("clear_eyed"))
    entry = next(r for r in rows if r["dist_storm_center"] < cfg.storm_radius)
    death = next(r for r in rows if not r["alive"])
    p_death = next((r for r in rows if not r["partner_alive"]), None)
    artifact = {
        "config": CFG, "seed": SEED,
        "config_hash": cfg.config_hash(),
        "manifest": build_manifest(SEED, cfg),
        "subject": subject, "partner": int(p[subject]),
        "milestones": {
            "first_clear_eyed_decision": first_flag["tick"],
            "entry": entry["tick"],
            "partner_death": p_death["tick"] if p_death else None,
            "subject_death": death["tick"],
        },
        "first_flagged_row": first_flag,
        "timeline": rows,
    }
    (RESULTS / "phase-12-biography.json").write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"subject {subject}, partner {int(p[subject])}")
    print(f"first clear-eyed decision at tick {first_flag['tick']}: "
          f"dist {first_flag['dist_partner']}, seen price "
          f"{first_flag['seen_price_integrity']} vs integrity "
          f"{first_flag['integrity']}, weights {first_flag['weights']}")
    print(f"entry {entry['tick']}, partner death "
          f"{p_death['tick'] if p_death else 'after subject'}, "
          f"subject death {death['tick']}")


if __name__ == "__main__":
    main()
