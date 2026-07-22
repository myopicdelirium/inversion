"""Batch runner for parameter sweeps. Parallelism across runs only
(CLAUDE.md); output is byte-identical regardless of worker count or
completion order, because results are keyed and sorted by (cell, seed)
before aggregation. Every run carries its seed and config hash.
"""

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

from .config import Config
from .model import Model, run
from .world import _torus_delta


def _cohort_metrics(cfg, seed, ticks, onset, window):
    """One run's summary. Cohort accounting matches phase 3: agents
    homed to the storm nest and alive at onset; a window death is any
    death in [onset, onset + window]. Trait summaries let the analysis
    ask whether the dead are a biased sample."""
    traj = run(cfg, seed=seed, ticks=ticks)
    ticks_arr = np.array(traj["tick"])
    alive = traj["alive"]
    n = cfg.n_agents

    fresh = Model(cfg, seed)  # deterministic re-init: traits and homes
    tau_bond = fresh.arrays.tau[:, 3].copy()
    bond0 = fresh.arrays.bond.copy()

    out = {
        "seed": seed,
        "config_hash": cfg.config_hash(),
        "survivors": int(alive[-1].sum()),
    }
    if cfg.storm_nest >= 0:
        cohort = (np.arange(n) % cfg.n_nests) == cfg.storm_nest
        k_onset = int(np.argmax(ticks_arr >= onset))
        at_risk = cohort & alive[k_onset]
        dead_window = at_risk & ~alive[-1]
        surv = at_risk & alive[-1]
        out.update({
            "at_risk": int(at_risk.sum()),
            "window_deaths": int(dead_window.sum()),
            "cohort_mortality": float(dead_window.sum() / max(int(at_risk.sum()), 1)),
            "tau_bond_median_dead": float(np.median(tau_bond[dead_window])) if dead_window.any() else None,
            "tau_bond_median_alive": float(np.median(tau_bond[surv])) if surv.any() else None,
            "bond_init_mean_dead": float(bond0[dead_window].mean()) if dead_window.any() else None,
            "bond_init_mean_alive": float(bond0[surv].mean()) if surv.any() else None,
        })
    return out


def _run_job(job):
    overrides, seed, ticks, onset, window = job
    cfg = replace(Config(), **overrides)
    return _cohort_metrics(cfg, seed, ticks, onset, window)


def run_sweep(base, axes, seeds, ticks, onset=2000, window=1000, workers=1):
    """base: dict of config overrides shared by every cell.
    axes: ordered list of (field, [values]).
    Returns a dict whose JSON serialization is independent of workers.
    """
    # Per cell: the cartesian product of axis values, in declared order.
    cells = [{}]
    for field, values in axes:
        cells = [dict(c, **{field: v}) for c in cells for v in values]

    jobs = []
    for cell in cells:
        for seed in seeds:
            jobs.append((dict(base, **cell), seed, ticks, onset, window))

    if workers <= 1:
        results = [_run_job(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_run_job, jobs))

    out_cells = []
    for cell in cells:
        # zip pairing is positional and exact: a row belongs to this
        # cell when its job carried exactly this cell's overrides.
        rows = [r for (j, r) in zip(jobs, results) if j[0] == dict(base, **cell)]
        rows.sort(key=lambda r: r["seed"])
        at_risk = sum(r.get("at_risk", 0) for r in rows)
        deaths = sum(r.get("window_deaths", 0) for r in rows)
        out_cells.append({
            "cell": cell,
            "runs": rows,
            "pooled_cohort_mortality": deaths / max(at_risk, 1),
        })
    return {"base": base, "axes": [[f, list(v)] for f, v in axes],
            "seeds": list(seeds), "ticks": ticks, "cells": out_cells}


def sweep_digest(sweep_result) -> str:
    import hashlib
    payload = json.dumps(sweep_result, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
