"""Phase 25: through the eyes. Artifacts:

  results/phase-25-escape.json              R2-R7 on seeds 1-48
  results/phase-25-escape-replication.json  fresh seeds 109-156

Seed ranges and the R3/R4 forms follow the recorded amendments in
specs/phase-25.md (design-confirmation amendment; panel fixes and the
replication-range excision are the second recorded amendment).

Three arms, same seeds, differing only in the care percept: T
(telepathic), S (sighted, the escapable distress), N (numb, care 0,
the separation-only baseline). Cohorts and bars as registered in
specs/phase-25.md. Design-confirmation mode (seeds 96-99) reports
survival, pair separation at onset, and cohort counts only: no
outcome measures.

Run:
  uv run python scripts/validate_phase25.py design
  uv run python scripts/validate_phase25.py all
"""

import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.config import Config  # noqa: E402
from core.drives import BOND  # noqa: E402
from core.manifest import build_manifest  # noqa: E402
from core.model import Model  # noqa: E402
from core.world import _torus_delta, peril_at, perceive_partner  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

ARENA = {"bond_target": "partner", "n_agents": 400, "n_hazard": 0,
         "storm_nest": 0, "storm_onset": 2000, "storm_ramp": 1,
         "storm_snare": 0.95, "storm_damage": 0.01,
         "prospect_horizon": 60, "prospect_sees_grip": True,
         "r_sight": 12.0, "memory_slots": 8,
         "wonder_horizon": 100, "wonder_relief": 0.1,
         "help_strength": 1.0}
ARMS = {"T": {"care": 1.0, "empathy_sighted": False},
        "S": {"care": 1.0, "empathy_sighted": True},
        "N": {"care": 0.0, "empathy_sighted": False}}
ONSET = 2000
WINDOW = 1200


def cell(args):
    arm, seed = args
    cfg = replace(Config(), **ARENA, **ARMS[arm])
    m = Model(cfg, seed)
    for _ in range(ONSET):
        m.step()
    alive_onset = int(m.arrays.alive.sum())
    d0, _, _ = perceive_partner(m.arrays, cfg)
    both = np.isfinite(d0)
    sep_median = float(np.median(d0[both])) if both.any() else None
    sep_beyond = (float((d0[both] > cfg.r_sight).mean())
                  if both.any() else None)

    n = cfg.n_agents
    witness = np.zeros(n, bool)
    absentee = np.zeros(n, bool)
    left = np.zeros(n, bool)
    returned_w = np.zeros(n, bool)
    returned_a = np.zeros(n, bool)
    forec_w = np.zeros(n, bool)
    forec_a = np.zeros(n, bool)
    grip_ever = np.zeros(n, bool)
    # R2, the gate identity, probed along the live run itself (S arm).
    # The panel proved the first probe was a tautology on the gate
    # under test, so the reconstruction is now independent: production
    # physics (peril_at), the panel-fix gate rebuilt from raw arrays,
    # never Model._target_peril.
    resid = 0.0
    sx, sy = m.world.storm_x, m.world.storm_y
    for _ in range(WINDOW):
        if arm == "S":
            dpre, _, _ = m._bond_distances()
            pp = m.arrays.partner
            phas = pp >= 0
            ppidx = np.where(phas, pp, 0)
            present = phas & m.arrays.alive[ppidx]
            px = np.where(present, m.arrays.x[ppidx], 0.0)
            py = np.where(present, m.arrays.y[ppidx], 0.0)
            level = peril_at(px, py, m.world, cfg, m._hazards_active(),
                             m._storm_intensity())
            per_ind = np.where(present, level, 0.0)
            per_ind = np.where(dpre <= m.arrays.r_sight, per_ind, 0.0)
            sep = 1.0 - np.exp(-dpre / cfg.r_bond)
            expected = m.arrays.bond * np.clip(
                sep + cfg.care * per_ind, 0.0, 1.0)
            pre_alive = m.arrays.alive.copy()
        m.step()
        if arm == "S" and pre_alive.any():
            resid = max(resid, float(np.abs(
                m.arrays.urgency[pre_alive, BOND]
                - expected[pre_alive]).max()))
        dx = _torus_delta(m.arrays.x - sx, cfg.world_size)
        dy = _torus_delta(m.arrays.y - sy, cfg.world_size)
        inside = ((np.hypot(dx, dy) < cfg.storm_radius)
                  & (m._storm_intensity() > 0.0))
        alive_u = m.arrays.alive
        grip_now = alive_u & inside
        grip_ever |= grip_now
        p = m.arrays.partner
        has = p >= 0
        pidx = np.where(has, p, 0)
        p_grip = has & alive_u[pidx] & grip_now[pidx]
        d, _, _ = perceive_partner(m.arrays, cfg)
        vis = d <= m.arrays.r_sight
        fresh = alive_u & ~inside & p_grip & ~witness & ~absentee
        witness |= fresh & vis
        absentee |= fresh & ~vis
        # Panel fixes, recorded in the spec: the registered censor
        # first (a partner that dies or exits the storm while u is
        # away forecloses return), then the transitions, each
        # requiring a living u; the dead cannot leave or return, and
        # entering the storm is not desertion.
        forec_w |= left & ~returned_w & ~p_grip
        forec_a |= absentee & ~returned_a & ~p_grip
        left |= witness & p_grip & ~vis & alive_u & ~inside
        returned_w |= left & p_grip & vis & alive_u & ~forec_w
        returned_a |= absentee & p_grip & vis & alive_u & ~forec_a

    abandoned = left & ~returned_w
    stayed = witness & ~left
    alive = m.arrays.alive

    def _mean(mask, arr):
        live = mask & alive
        return float(arr[live].mean()) if live.any() else None

    return {"arm": arm, "seed": seed, "config_hash": cfg.config_hash(),
            "alive_onset": alive_onset, "sep_median": sep_median,
            "sep_beyond_sight": sep_beyond,
            "n_witness": int(witness.sum()),
            "n_absentee": int(absentee.sum()),
            "n_leavers": int(left.sum()),
            "n_returned_w": int(returned_w.sum()),
            "n_abandoned": int(abandoned.sum()),
            "n_returned_a": int(returned_a.sum()),
            "n_foreclosed_w": int((forec_w & ~returned_w).sum()),
            "n_foreclosed_a": int((forec_a & ~returned_a).sum()),
            "gate_residual": resid if arm == "S" else None,
            "witness_dead": int((witness & ~alive).sum()),
            "abandoner_energy": _mean(abandoned, m.arrays.energy),
            "abandoner_integrity": _mean(abandoned, m.arrays.integrity),
            "stayer_energy": _mean(stayed, m.arrays.energy),
            "stayer_integrity": _mean(stayed, m.arrays.integrity),
            "n_gripped_ever": int(grip_ever.sum()),
            "gripped_dead": int((grip_ever & ~alive).sum()),
            "gripped_extracted": int((grip_ever & alive & ~inside).sum()),
            "final_alive": int(alive.sum())}


def _pool(rows, arm, key):
    return sum(r[key] for r in rows if r["arm"] == arm)


def run_design(seeds):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell, jobs))
    for arm in ARMS:
        sel = [r for r in rows if r["arm"] == arm]
        alive = [r["alive_onset"] for r in sel]
        seps = [r["sep_median"] for r in sel]
        bey = [r["sep_beyond_sight"] for r in sel]
        print(f"arm {arm}: alive at onset {alive}, median pair "
              f"separation {[round(s, 1) for s in seps]}, frac beyond "
              f"sight {[round(b, 2) for b in bey]}")
        print(f"  cohort counts per seed: witnesses "
              f"{[r['n_witness'] for r in sel]}, absentees "
              f"{[r['n_absentee'] for r in sel]}, leavers "
              f"{[r['n_leavers'] for r in sel]}")
    print("design-confirmation: cohort counts and survival only; the "
          "shared cell computes outcome measures but none are shown "
          "or read here")


def run_stage(seeds, out_path):
    jobs = [(a, s) for a in ARMS for s in seeds]
    with ProcessPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(cell, jobs))
    art = {"spec": "specs/phase-25.md",
           "manifest": build_manifest(
               seed=0, config=replace(Config(), **ARENA, **ARMS["T"])),
           "arm_config_hashes": {
               a: replace(Config(), **ARENA, **ARMS[a]).config_hash()
               for a in ARMS},
           "seeds": list(seeds), "rows": rows}

    resid = max(r["gate_residual"] for r in rows if r["arm"] == "S")
    r2 = resid < 1e-9
    art["R2"] = {"max_residual": resid, "passed": bool(r2)}
    print(f"R2 gate identity: max residual {resid:.2e} (bar 1e-9): "
          f"passed {r2}")

    wit = {a: _pool(rows, a, "n_witness") for a in ARMS}
    absn = {a: _pool(rows, a, "n_absentee") for a in ARMS}
    lvs = {a: _pool(rows, a, "n_leavers") for a in ARMS}
    r3 = (min(wit.values()) >= 150 and lvs["S"] >= 60
          and lvs["N"] >= 60)
    art["R3"] = {"witnesses": wit, "leavers": lvs, "passed": bool(r3)}
    print(f"R3 power floors: witnesses {wit} (floor 150), leavers "
          f"{lvs} (floor 60 in S and N): passed {r3}")

    # The absentee cohort, demoted to descriptive by the recorded
    # design-confirmation amendment: counts only, no bar.
    art["absentees"] = {a: {"n": absn[a],
                            "returned": _pool(rows, a, "n_returned_a")}
                        for a in ARMS}
    print(f"absentees (descriptive, no bar): "
          + ", ".join(f"{a} {absn[a]}" for a in ARMS))

    leave = {a: lvs[a] / max(wit[a], 1) for a in ARMS}
    r4_delta = leave["N"] - leave["T"]
    r4 = r4_delta >= 0.10
    art["R4"] = {"witness_leave_rate": leave, "N_minus_T": r4_delta,
                 "passed": bool(r4)}
    print(f"R4 care-glue check: witness leave rate N {leave['N']:.3f} "
          f"vs T {leave['T']:.3f} (S {leave['S']:.3f}); N-T "
          f"{100 * r4_delta:+.1f} pts (bar +10): passed {r4}")

    # The registration's gate: R5 and R6 are judged only when the
    # floors and the care-glue manipulation check both hold.
    gates = r3 and r4
    art["gates_passed"] = bool(gates)

    aband = {a: _pool(rows, a, "n_abandoned") / max(wit[a], 1)
             for a in ARMS}
    r5_delta = aband["S"] - aband["T"]
    r5_verdict = (("E2_confirmed_rung_refused" if r5_delta >= 0.15
                   else "rung_passed" if r5_delta <= 0.05
                   else "no_verdict") if gates
                  else "unjudged_gates_failed")
    art["R5"] = {"abandonment": aband, "S_minus_T": r5_delta,
                 "verdict": r5_verdict}
    print(f"R5 escape test: abandonment S {aband['S']:.3f} vs T "
          f"{aband['T']:.3f} (N {aband['N']:.3f}); S-T "
          f"{100 * r5_delta:+.1f} pts (bars +15 refuse / +5 pass): "
          f"{r5_verdict}")

    ret_w = {a: _pool(rows, a, "n_returned_w") / max(lvs[a], 1)
             for a in ARMS}
    r6_delta = ret_w["S"] - ret_w["N"]
    r6 = r6_delta >= 0.10
    art["R6"] = {"leaver_return": ret_w, "S_minus_N": r6_delta,
                 "foreclosed": {a: _pool(rows, a, "n_foreclosed_w")
                                for a in ARMS},
                 "passed": bool(r6) if gates else None}
    print(f"R6 the return: leaver return S {ret_w['S']:.3f} vs N "
          f"{ret_w['N']:.3f} (T {ret_w['T']:.3f}); S-N "
          f"{100 * r6_delta:+.1f} pts (bar +10): passed {r6}")

    costs = {}
    for a in ARMS:
        sel = [r for r in rows if r["arm"] == a]
        ge = sum(r["n_gripped_ever"] for r in sel)
        costs[a] = {
            "abandoner_energy": [r["abandoner_energy"] for r in sel],
            "stayer_energy": [r["stayer_energy"] for r in sel],
            "abandoner_integrity": [r["abandoner_integrity"] for r in sel],
            "stayer_integrity": [r["stayer_integrity"] for r in sel],
            "witness_mortality": (sum(r["witness_dead"] for r in sel)
                                  / max(wit[a], 1)),
            "gripped_extraction": (sum(r["gripped_extracted"] for r in sel)
                                   / max(ge, 1)),
            "gripped_mortality": (sum(r["gripped_dead"] for r in sel)
                                  / max(ge, 1))}
        print(f"R7 costs, arm {a}: witness mortality "
              f"{costs[a]['witness_mortality']:.3f}, gripped extraction "
              f"{costs[a]['gripped_extraction']:.3f}, gripped mortality "
              f"{costs[a]['gripped_mortality']:.3f}")
    art["R7"] = costs
    out_path.write_text(json.dumps(art, indent=2) + "\n")
    print("written", out_path.name)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    stage = sys.argv[1]
    if stage == "design":
        run_design(range(96, 100))
    elif stage == "main":
        run_stage(range(1, 49), RESULTS / "phase-25-escape.json")
    elif stage == "replicate":
        run_stage(range(109, 157),
                  RESULTS / "phase-25-escape-replication.json")
    else:
        run_stage(range(1, 49), RESULTS / "phase-25-escape.json")
        run_stage(range(109, 157),
                  RESULTS / "phase-25-escape-replication.json")
