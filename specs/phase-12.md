# Phase 12: The search for the clear-eyed region

Status: **implemented 2026-07-24 under standing delegation**. No kernel, config, or golden changes: a declared search over existing axes, with the phase's deliverable being the answer either way.

## Purpose

Phase 11 proved every measured death was a death of not seeing. The remaining question is whether this architecture contains any coordinates where a creature that sees the price still goes in: clear-eyed sacrifice. Locating that region, or bounding its absence over a declared grid, is the result. No direction is desired.

## The clear-eyed operationalization (analysis-side; the agent's code is untouched)

An entry decision is **clear-eyed** when, at the tick the agent chose return toward its trapped partner, its own rollout's safety cost for that action (the seen exposure, in danger-tick units), scaled by the world's burn rate, meets or exceeds the agent's remaining integrity: it chose a path whose seen price is at least its life. Declared caveats: the seen exposure is a lower bound (the grip's slowing of the approach is not in the agent's physics, though the dominant held-at-destination exposure is fully seen), so the flag is conservative; and the danger integral is used as the inside-the-storm weight, a declared approximation. A **clear-eyed cell** requires all three: pull ratio at least 2 over its own bond-0 control, entered share of pull-group deaths at least 0.7, and at least half of dead entrants flagged clear-eyed at a decision they took.

## The declared grid (the mire, phase 8 arena: grip 0.95, burn 0.01, 400 agents, partner bonds, sudden storm at tick 2000, window 1200 from onset+50)

* `tau_safety` {12, 24, 48}: slow fear discounts the seen price, because foresight multiplies predicted exposure by the current fear weight.
* `attention_sharpness` {0, 0.75} (floor 0.05 when nonzero): devotion-dominance suppresses the fear weight that prices the path.
* `bond_init` {0.8, 1.0}: the relief side of the ledger.
* `prospect_horizon` {20, 60}: how much of the held price is inside the sight.
* Controls: `bond_init` 0 at every (tau_safety, kappa, horizon).
* 12 seeds per cell: 24 search cells plus 12 control cells, 432 runs.

## Pre-registered

* **S1, the question, no desired direction**: the grid contains at least one clear-eyed cell, or it does not. Reported either way, with the full grid.
* **S2, falsifiable direction**: entry propensity (pull ratio and entered share) is non-decreasing in tau_safety at fixed other coordinates.
* **S3, inertness**: no kernel or config change; the full suite passes untouched.
* **Replication**: the headline cells (clear-eyed ones if any exist, otherwise the strongest null) rerun on pre-declared fresh seeds before packaging.

## Non-goals

Snare-aware rollout physics (a declared Amendment 4 extension left for a later phase; its absence makes the flag conservative, which is the safe direction), new axes, changes to the clear-eyed definition after seeing results.

## Deviations from spec during build

Recorded 2026-07-24. Full grids in `results/phase-12-search.json` (seeds 1-12) and `phase-12-replication.json` (fresh seeds 31-42), 864 runs total.

1. **S1 answered, and replicated: the clear-eyed region is empty; the clear-eyed individuals are not.** Zero of 24 cells met the declared cell definition on either seed set. But at the slow-fear, devoted-attention corner (tau_safety 48, kappa 0.75), individual clear-eyed deaths occur on both seed sets: dead entrants whose own rollout, at the decision tick, priced the chosen path at or above their remaining life. Original grid: 2 such individuals (clear-eyed shares 1.00 of 1 death at h 20 bond 0.8, 0.17 at h 60). Replication: roughly 5 (shares 0.25, 0.17, 0.22 across three cells). Order ten individuals out of roughly 115,000 agent-runs, all at one corner of the space. In this architecture, sacrifice with the price seen exists as a rarity of particular agents in particular geometry, never as a property of a population.
2. **S2 FAILS as declared**: entry propensity is not monotone in tau_safety (entered shares 0.67 / 0.56 / 0.83 across tau_safety 12 / 24 / 48 at kappa 0.75, h 60, original seeds; replication likewise non-monotone). Slow fear is neither necessary nor smoothly sufficient; the corner effect is an interaction with attention, not a gradient.
3. **What the persistent excess deaths are instead**: at the elevated cells (kappa 0.75, h 60, tau_safety 24-48: pull 0.17-0.25 vs controls 0.10-0.14), entered shares run 0.56 to 1.00 but clear-eyed shares 0.00 to 0.22: most who die entering priced the visit as survivable. The grip is not in their physics, so these are trap-underestimation deaths: mistaken entries, not chosen ones. The conservative flag direction (seen price is a lower bound) means true clear-eyed status can only be undercounted, so the emptiness of the region is if anything overstated against us, which strengthens it.
4. **S3 held**: no kernel or config change; 25 tests passed untouched throughout; the one operational note is that the foreground golden run starved behind the 6-worker replication grid and was rerun after it finished.
5. The anecdote-corner golden (seed 42, 340 of 400 alive) freezes the coordinates where the individuals occur.
