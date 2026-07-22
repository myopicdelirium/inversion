# Phase 3: Collision environments

Status: **approved 2026-07-23**. Spec authored by the user; the go-ahead ("move forward with the next step") postdates the draft and constitutes the review this phase required. Implemented same day.

## Purpose

Make the timing collision reachable and measurable. The drive and action machinery of phases 1-2 is frozen; phase 3 adds only environment (a storm) and measurement. The load-bearing result is the null test: if mortality does not collapse when the same threat is telegraphed slowly, the model fails its own emergence claim and that failure gets reported, not tuned away.

## What the model predicts before this phase is built

Written down now so the phase cannot quietly become a fishing expedition.

1. **The collision exists.** Under a sudden lethal storm centered on a nest, agents bonded to that nest die at higher rates than zero-bond controls in identical worlds.
2. **Telegraphing saves lives.** At fixed bond, mortality falls monotonically as the storm's onset ramp lengthens, collapsing toward the control rate: a slowly arriving threat gives the safety weight time to win and the bond weight time to lose.
3. **Commitment kills by pulling back, not pinning down.** Separation distress is zero at home, so at-home agents flee a sudden storm with only the ordinary safety lag. The commitment-specific deaths should be re-entries: agents that escaped, were pulled back by rising separation distress, and returned into the danger. Deaths therefore decompose into onset deaths (caught inside at activation, the neglect regime) and return deaths (re-entered after at least one exit, the commitment regime), and the excess mortality of bonded agents over controls should be carried by return deaths.

## Model additions (environment and measurement only)

### The storm

* One additional hazard, centered on the nest indexed by `storm_nest` (default -1, disabled). Static position: it sits on the nest. Placement consumes no RNG draws, so the world stream is identical with the storm on or off.
* Activates at tick `storm_onset` (default 2000) with intensity ramping linearly from 0 to 1 over `storm_ramp` ticks (1 = a step). Intensity multiplies both its danger contribution `exp(-d / storm_radius)` (into the existing max field) and its damage `storm_damage` inside `storm_radius`.
* Defaults: `storm_radius = 10.0`, `storm_damage = 0.05` (lethal in 20 ticks at full intensity from full integrity; roughly 1.7x the safety lag plus escape time, so a sudden storm is survivable but costly for an agent that reacts on the ordinary lag, and fatal for one that keeps coming back).
* No drive, action, or E-table changes of any kind. The storm is experimental apparatus, declared here.

### Measurement

* Storm mortality: fraction of agents homed to the storm nest that die in [onset, onset + 1000], against the same window in control runs (`bond_init = 0`, same seeds).
* Death classification, recorded per death in the artifact: onset death (inside the storm continuously since activation) vs return death (at least one exit and re-entry before dying). Classification lives in analysis code, reads trajectories only, and touches nothing in `core/` except a storm-geometry helper.
* Vocabulary rule: artifacts and analysis say storm mortality, onset deaths, return deaths. The invariant's forbidden vocabulary stays forbidden everywhere.

## Acceptance criteria

1. **Preservation, exact and total.** With the storm disabled, the phase 2 combined golden hash is unchanged. No array shapes change in this phase, so there is no supersession and nothing to sign off.
2. **The collision exists.** Sudden storm (`storm_ramp = 1`), `bond_init` 1.0 vs 0.0, 10 seeds: bonded storm-mortality exceeds control in at least 9 of 10 seeds, pooled excess at least 5 percentage points.
3. **The null test.** At `bond_init = 1.0`, ramp in {1, 100, 400, 1600}: mortality non-increasing in ramp with strict decrease from 1 to 1600, and mortality at ramp 1600 within 2 percentage points of control. These thresholds are declared now; if calibration forces different ones, that is a documented deviation with the reason, never a silent change.
4. **Regime decomposition recorded.** Return-death and onset-death counts per condition in the artifact. Prediction 3 (excess carried by return deaths) is evaluated and reported either way; it is a falsifiable claim, not a pass condition.
5. **First phase-diagram slice.** Grid: `bond_init` {0, 0.25, 0.5, 0.75, 1.0} x ramp {1, 100, 400, 1600}, at least 5 seeds per cell. Artifact: mortality per cell with seeds and config hashes, plus a heatmap figure. The map must contain structure: at least one cell 20 or more points above control and at least one within 2 points of it. A map that is all death or no death fails the phase, per the constitution's founding sentence.
6. **Golden.** One storm-enabled golden run committed alongside the storm-disabled equivalence check.

## Non-goals

Bonds to agents, grief (the nest is never destroyed, only made dangerous), rescue or approach behaviors, damage sensitization, moving storms, multiple storms, tau sweeps beyond the two axes above (tau_safety and tau_bond as swept axes arrive with the Phase 4 sweep machinery).

## Open design questions flagged for review

1. **Return-based commitment death is a modeling claim.** In this architecture the bond cannot pin an agent at home under fire, because separation distress is zero at home; it can only pull the agent back. This matches the origin case (the searcher returns to the search) and keeps the urgency form clean. The alternative, an attachment urgency that rises when the home itself is threatened, would need the bond drive to read the danger field, which walks toward the invariant line. Recommendation: accept return-based death as the phase 3 mechanism and revisit only with evidence.
2. **Storm placement is aimed at a nest.** This is a designed experiment, not a naturalistic world. Declared here as apparatus; the naturalistic version (storms wander, collisions happen by chance) belongs to phase 5 population runs.
3. **The mortality window (1000 ticks) and threshold numbers** in criteria 2-3-5 are pre-run guesses of the same kind phase 1's homeostasis band was; they may need documented calibration.

## Deviations from spec during build

Recorded 2026-07-23, the implementation session. Full numbers in `results/phase-3-validation.json`; raw cells with per-run seeds and config hashes in `results/phase-3-cells.json`.

1. **Criterion 3, the null test, FAILS as written, and the failure is the phase's central finding.** Storm mortality at bond 1.0 by ramp {1, 100, 400, 1600}: 0.25, 0.49, 1.00, 1.00, against controls at 0.00. Mortality rises with telegraphing instead of collapsing. Mechanism: as specced, damage ramps with the signal, so a long ramp is a gradual arrival of harm, not a warning. Under gradual harm, no single tick makes fleeing out-value the current activity, the bond cycles agents back through the warming zone, and cumulative damage crosses lethal before danger ever feels urgent. Not tuned away; reported.
2. **Supplementary apparatus added to disambiguate: `storm_ramp_harmless`** (default false, preservation intact). The ramp becomes warning only: the danger signal rises as specced but damage starts when the ramp completes. Under this reading of "telegraphed," prediction 2 holds exactly as pre-registered: mortality 0.25, 0.20, 0.02, 0.00 across the same ramps, monotone collapse to control. The model forced a conceptual distinction the spec's vocabulary did not have: warning saves lives, gradual arrival of harm kills more than sudden arrival. Same ramps, same bond, opposite outcomes.
3. **Prediction 3 confirmed exactly.** At the flagship cell (sudden storm, bond 1.0), onset deaths are 0 and the return share of integrity deaths is 1.00: every commitment death is an agent that escaped and went back. The bond does not pin agents down; it pulls them back. Even in the slow-cook cells, deaths classify as return deaths: agents cycle out and back through the growing storm.
4. **Arena declarations** (the spec left them open): default 5 nests, so the cohort homed to the storm nest is about 40 of 200; drifting hazards off (`n_hazard = 0`) so every integrity death in the window is a storm death. Declared in `scripts/validate_phase3.py::cell_config`.
5. **Criteria as judged: 2 PASS** (pooled 0.29 vs 0.00, 10/10 seeds, excess 29 points against the required 5), **3 FAIL as written / holds under the harmless-ramp reading** (deviation 2), **4 recorded** (decomposition per condition in the artifact), **5 PASS** (the map has hot cells 20+ points above control and bonded cells within 2 points of control; it is neither all death nor no death), **6 done** (two goldens, not one: the inversion cell and the null cell, since the constitution says null regions are findings and get goldens too).
6. **Phase 2 stored config hash refreshed twice** (storm fields, then `storm_ramp_harmless`), each time after verifying in the same run that the phase 2 golden trajectory hash is bit-for-bit unchanged. The trajectory hash never moved.
7. **Pre-onset observation, reported for the record:** in a single-nest arena at bond 1.0, tether-induced crowding starved 22 of 200 agents before any storm existed (probe run, seed 42). The 5-nest arena dilutes this; cohort at-risk counts per cell are in the raw file. Commitment has a carrying cost even in peacetime.
