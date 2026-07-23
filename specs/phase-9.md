# Phase 9: The human axes join the map

Status: **implemented 2026-07-23 under standing delegation**. A pure measurement phase: no kernel, config, or golden changes of any kind. Every axis below already exists; this phase maps them.

## Purpose

The phase diagram (phase 5) predates attention and the snare. This phase extends it over both, and over trait selection under attention, in the place-attachment arena where inversion lives. Four predictions are pre-registered, because this model has corrected its designers five times and the record should keep inviting it.

## Pre-registered predictions

* **P1, focus protects here too.** In the sudden-storm place arena, moderate sharpness (kappa 0.5 to 0.75) at bond 1.0 cuts cohort mortality to at most half the kappa 0 value, by the same focused-evacuation dynamics seen in the partner arena.
* **P2, saturation is attention-proof.** At the slow cook (ramp 400, bond 1.0), mortality stays within 5 points of 1.0 across all kappa: gradual arrival kills through timing, and no attention allocation repairs timing.
* **P3, the tar pit deepens inversion.** At sudden onset, damage 0.01, bond 1.0, kappa 0: mortality rises monotonically with snare {0, 0.5, 0.9}, by at least 10 points end to end, while the bond 0 control rises by less than 5: the snare's lethality routes through the returns.
* **P4, attention sharpens selection.** In the heterogeneous flagship (spreads on), the dead-vs-survivor trait gaps at kappa 0.75 are at least as large in magnitude as at kappa 0: dominance lock-in amplifies initial differences.

## The grids (all 200 agents, storm on nest 0 at tick 2000, window 1000, cohort accounting as phase 3, 6 seeds per cell, seeds 1-6)

* **Diagram D, attention x place-attachment**: kappa {0, 0.25, 0.5, 0.75, 1.0, 1.5} x bond_init {0, 0.5, 1.0} x ramp {1, 400}, damage mode. 36 cells, 216 runs.
* **Diagram E, the tar pit**: ramp 1, damage 0.01, kappa 0, snare {0, 0.5, 0.9} x bond_init {0, 1.0}. 6 cells, 36 runs.
* **Diagram F, selection under attention**: heterogeneous flagship (bond median 0.6, tau_bond spread 0.5, bond_init spread 0.25, ramp 1), kappa {0, 0.75}. 2 cells, 12 runs; clock and depth gaps.

## Acceptance criteria

1. **Nothing changes but knowledge**: the full suite passes untouched, no hash refreshed.
2. P1 through P4 judged exactly as written above; failures reported as findings per house rule.
3. Artifacts: `results/phase-9-maps.json` with every cell, seeds, config hashes, sweep digests; figure `phase-9-maps.png`.
4. If a new null or protective regime is found, one golden freezes it (null regions are findings, Amendment 1).

## Non-goals

Trait inheritance (the next mechanism phase), kappa above 1.5 (established nonviable in ambient-hazard worlds; the storm arena has none, but the diagram should stay within the range a full world tolerates), partner-mode cells (partner attachment was mapped in phases 6-8).

## Deviations from spec during build

Recorded 2026-07-23. Full numbers, validity annotations, and corrections in `results/phase-9-maps.json`. This phase's deviations section is longer than its results section, deliberately: an artifact was caught in-session, before anything was published, and the record of how is worth more than the cells it voided.

1. **The near-miss, stated first.** The raw map showed kappa 1.5 as protective (mortality 0.333 sudden, 0.000 slow cook at bond 1.0), and for roughly one hour the working interpretation was "extreme attention protects by silencing love." The regime golden froze seed 42 to specimen it: 0 of 200 alive. That contradiction forced the check: at bond 1.0, kappa 1.5, between 199 and 200 of 200 agents starve BEFORE tick 2000, at home, in an arena containing no hazards and no storm damage yet. The cohort mortality metric divides by an at-risk pool of 0 to 3 agents and its guard reads empty as zero. All four bonded kappa 1.5 cells are void (at-risk pools 3 and 11 of 240) and are so marked in the artifact and figure. The corrected regime name: **peacetime collapse**. Deep place-attachment plus extreme sharpness starves its carriers with no enemy at all: the bond weight dominates on the first foraging trips, hunger becomes inaudible, and the population dies at home by around tick 400. The golden is kept, renamed, with an honest description.
2. **The zero-trap, the mechanism under everything here.** Under the attention law, a drive with weight exactly 0 is heard as u * (0 / max)^kappa = 0, permanently, at any kappa above 0. Weights initialize to urgencies, so an agent spawned in safety has fear at exactly zero and can never acquire it. This explains: the bond 0 rows being seed-identical across every kappa above 0 (fear-deaf storm deaths reduce to pure geometry: 0.396 sudden, 0.208 slow cook); much of phase 7's everyday-boundary collapse; and the P1 refutation below. A fear never once felt cannot be learned later, at any sharpness. Whether that is a finding to keep or an idealization to soften (an epsilon floor in the law, or weights initialized off the urgencies) is a kernel-design fork under Amendment 3, flagged for decision, not taken here.
3. **P1 REFUTED on valid cells, in the opposite direction.** Sudden storm, bond 0.5 and 1.0: mortality 1.000 at every kappa from 0.25 through 1.0, against 0.133 and 0.255 at kappa 0. The prediction imported phase 7's focused-evacuation story from the partner arena; in the place arena the tether holds the cohort in range while the zero-trap keeps fear inaudible. The person/place asymmetry extends to attention: the same sharpness that protected partner-bonded agents annihilates place-bonded ones.
4. **P2 HOLDS on valid cells**: slow-cook mortality 1.000 across kappa 0 through 1.0 at bond 1.0 (the kappa 1.5 cell is void). Saturation is attention-proof where the cohort exists.
5. **P3 HOLDS exactly as registered**, the one clean confirmation: tar pit mortality 0.000 / 0.008 / 0.682 across snare 0 / 0.5 / 0.9 at bond 1.0, with the bond 0 control flat at 0.000 throughout. The snare's lethality routes entirely through the returns.
6. **P4 unjudgeable as declared, resolved into a statement**: at the declared cell mortality saturated at 1.000, and saturated outcomes carry no selection signal (when everyone dies, traits stop mattering). A labeled post-hoc cell at kappa 1.5 (heterogeneous) shows mortality 0.694 with clock gap -12.1 and depth gap +0.037, but on an at-risk pool of only 36 (the rest starved pre-onset); interpret with care, replicate before printing.
7. **Criterion 1 held throughout**: no kernel, config, or golden-hash changes; the suite passes untouched.
