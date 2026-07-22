# Phase 5: The phase diagram

Status: **implemented 2026-07-23 under standing delegation**. Spec written before mechanism.

## Purpose

Produce the product: the map of where preference inversion lives and where it does not, over declared axes, from the machinery of phases 1-4, plus the second product phase 4 earned: the composition maps, since individuality decides who dies rather than how many. Two enabling refactors make population scale real, and both must be bit-identical to the existing dynamics: the golden suite is the referee.

## Infrastructure (bit-identical by construction, verified by goldens)

1. **Blocked per-agent draws.** The per-tick Python loop over agent generators is replaced by refilling a block of draws every 256 ticks per agent. `Generator.random(k)` consumes the identical stream values as k singles, and the block is indexed in the same per-tick order, so every trajectory is unchanged to the bit. Block size is an internal constant, provably irrelevant to results (the goldens would catch any deviation).
2. **Exact nearest-food by KD-tree** (scipy, recorded in the lockfile). The (agents x foods) distance matrix is quadratic and dies at population scale. A periodic KD-tree over active sources selects only the *index* of the nearest source; distance and direction are then recomputed with the same torus arithmetic as before, so outputs are bit-identical whenever the selected index matches the old argmin. Ties are measure-zero (continuous respawn positions). Query positions are canonicalized (x equal to world_size maps to 0, the same torus point) without touching state.

Acceptance for both: every existing golden passes unchanged, no hash refreshed, no config field added.

## The diagrams

All cells: 200 agents, 5 nests, no drifting hazards, storm on nest 0 at tick 2000, window 1000, cohort accounting as in phase 3, 6 seeds per cell, every run carrying seed and config hash, sweep digests recorded.

* **Diagram A, the main map**: `bond_init` {0, 0.2, 0.4, 0.6, 0.8, 1.0} x `storm_ramp` {1, 50, 100, 200, 400, 800, 1600} x mode {damage-carrying, harmless} = 84 cells, 504 runs. Reported as excess mortality over the bond-0 row of the same ramp and mode.
* **Diagram B, the psychology plane**: `tau_bond` {15, 30, 60, 120, 240} x `tau_safety` {3, 6, 12, 24, 48} at the flagship storm (sudden, bond 1.0) = 25 cells, 150 runs.
* **Diagram C, the composition map**: ramp x mode at declared median `bond_init = 0.6` with spreads on (`tau_bond_spread 0.5`, `bond_init_spread 0.25`) = 14 cells, 84 runs. Per cell: the selection gaps (dead vs surviving cohort: median tau_bond, mean bond_init), reported where mortality is in (0.05, 0.95) so both groups exist.

## Population scale

* One 10,000-agent run at matched density (world 700, food 7500, 50 nests, cohort 200) with the storm, 3000 ticks: completes, wall time recorded in the artifact.
* Determinism at scale: two 300-tick 10,000-agent runs produce identical golden hashes.

## Acceptance criteria

1. **Preservation**: full test suite green with zero golden or config-hash changes.
2. **Structure, per the constitution's founding sentence**: the main map must contain, as measured, (a) an inversion region: cells at least 40 points of excess mortality; (b) a null region: harmless-mode cells at ramp 800+ within 2 points of control at every bond level. If either fails, it is reported, not tuned.
3. **The psychology plane shows relief**: max minus min cell mortality at least 15 points across the tau plane. Reported as measured.
4. **Composition**: selection gaps with consistent sign across qualifying cells (dead faster-clocked and deeper-bonded than survivors, matching phase 4), reported per cell.
5. **Scale**: the 10k run completes with wall time in the artifact; the 10k determinism check passes.
6. **Artifacts**: `results/phase-5-diagram.json` (all cells, digests, manifest), `phase-5-map.png`, `phase-5-planes.png`. BUILD_BRIEF updated: the diagram exists.

## Non-goals

New mechanisms of any kind, grief or agent-to-agent bonds, moving or multiple storms, trait inheritance, GPU or distributed execution, further axes (declared once here: bond_grow, r_bond, regen, damage remain fixed at defaults this phase and are future diagram dimensions).

## Deviations from spec during build

Recorded 2026-07-23. Full grids in `results/phase-5-diagram.json`; 738 diagram runs plus the 10k record, wall time under four minutes total after the two refactors (200-agent runs went from ~4.5s to 0.92s; 10k agents run at ~13ms per tick).

1. **Criteria 2, 3, 5 pass as declared.** The map has a genuine phase structure: in damage mode, inversion is near-total (excess 0.9 to 1.0) in the region bounded by bond_init >= 0.4 and ramp >= 200, while bond 0.2 stays below 0.17 excess everywhere: a commitment-depth threshold between 0.2 and 0.4. In harmless mode the entire ramp >= 800 band sits within 2 points of control at every bond level: the warning null region, exactly where phase 3 found it. The psychology plane's relief is 0.64, and its dominant axis is unambiguous: the speed of fear. Mortality under a sudden storm rises from ~0.14-0.27 at tau_safety 3 to ~0.71-0.78 at tau_safety 48, monotonically along every row, while tau_bond barely moves the aggregate (echoing phase 4). Survival of sudden threats belongs to quick fear, not to shallow attachment.
2. **Criterion 4 FAILS as declared, and resolves into a two-trait, two-regime finding.** Depth selection is universal: in all 8 qualifying composition cells the dead were more deeply attached at birth (gaps +0.025 to +0.132). Clock selection is regime-dependent: strongly negative (dead faster-clocked) only in the gradual-arrival cells, deepening as the cook slows (-3.8 at ramp 50, -9.3 at 100, -14.5 at 200), because those deaths are cycling returns and a fast clock rebuilds the pull after every escape; at sudden storms with depth spread present, depth absorbs the selection and the clock's gap is small (+2.5). The pre-registered 80% sign rule was written expecting phase 4's flagship pattern to generalize; it does not, and the regime dependence is more informative than the rule. Reported, not tuned.
3. **The two enabling refactors were verified bit-identical** exactly as specced: blocked draws and KD-tree index selection changed no golden hash and no config hash. Zero hash churn this phase.
4. **10k determinism seeds**: the spec said two 300-tick runs; implemented as seed 7 pairs alongside the seed 42 timing run, digest-equal.
