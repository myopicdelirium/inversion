# Phase 14: The other in the ledger

Status: **implemented 2026-07-24 under standing delegation**, under Amendment 5. Spec before mechanism; the fencing tripwires already exist and are named in the amendment.

## Purpose

Phase 13 bounded the architecture: no up-front wager, because no agent's ledger ever contained the beloved. This phase adds the minimum other-regard that makes the wager arithmetically possible: an urgency term for the living bond target's peril, and assistance physics so that reaching them can actually end that peril. Then the question is asked a third time, now properly posed: with the price seen (full sight), the stake denominated in the other (care), and the hands able to help (assistance), does the wager occur, and does it succeed? No direction is desired. A subsidiary question with policy weight: does care produce rescues, futile deaths, or both, and at what coefficients?

## Mechanism (all default-zero, bit-inert)

* Config: `care` (0..1, default 0), `r_help` (default 2.0), `help_strength` (0..1, default 0).
* `u_bond = b * clip((1 - exp(-d/r_bond)) + care * peril, 0, 1)`, peril = danger field at the living target's location, zero for absent targets. In `core/drives.py`, urgency stage, continuous, no branch.
* Assistance: within `r_help` of one's gripped partner, the partner's effective snare scales by `1 - help_strength`. Symmetric. In `core/world.py`.
* E-table care components, declared folk forms: myopic return gains `care * peril * help_strength / (1 + travel)`; farsighted return gains `care * peril * help_strength * (h - arrival)+` (the expectation that presence ends the peril, proportional to helping power). Zero when care or help is zero, exactly.

## Pre-registered

* **W1, the question, no desired direction**: mire, full sight, h 60, tau_safety 12, kappa 0, bond 0.8, grid care {0, 0.5, 1.0} x help {0, 0.5, 1.0}, 12 seeds: either some care/help cell shows pull-group entries at excess with clear-eyed flags (the wager occurs), or none does. Additionally measured either way: **extraction** (trapped partners alive and outside by the end) versus the care 0 / help 0 baseline: do rescues succeed, and at what death cost to the rescuers?
* **W2, falsifiable direction**: extraction increases with help_strength at fixed care.
* **W3, the everyday tax**: ordinary hazard world, care 1 vs 0 (help 0), survival within 3 points (5 seeds). Care should reprice partner peril, not break daily life.
* **W4, identity**: the care urgency reconstructs exactly from recorded arrays plus partner positions on a care > 0 run (max residual below 1e-9).
* **W5, preservation**: care 0, help 0 bit-identical everywhere (twelve goldens, hash-refresh routine for the three new fields).
* **Replication** of the full W1 grid on fresh seeds before packaging, per the standing default.

## Non-goals

Care spread as a trait (later axis), one-to-many bonds and authority (next capability on the delta list), care toward non-bond agents, any reading of the target's integrity (fenced by the standing tripwire), reciprocity bookkeeping.

## Deviations from spec during build

Recorded 2026-07-24. Full grids in `results/phase-14-wager.json` (seeds 1-12) and `phase-14-replication.json` (fresh seeds 31-42), 216 grid runs plus W3/W4.

1. **W5, W4, W3 pass.** All twelve golden trajectories bit-identical with care and help at zero; the care urgency identity is exact to the bit (max residual 0.0e+00); the everyday tax is 0.3 points (0.993 vs 0.990). One anomaly recorded for the audit trail: during the preservation check, the phase 13 threshold golden reported a trajectory mismatch once, in a single scripted run, and passed identically on three immediate reruns with all nine per-array hashes matching; cause not reproduced at the time; later fully explained as a verifier config-reconstruction error, see docs/INCIDENT-2026-07-24-determinism.md.
2. **W1 answered, and replicated: the wager does not occur.** Zero clear-eyed and zero up-front deaths in all 18 cells across both seed sets. With the other priced into the ledger and hands that work, the model produces assistance, not sacrifice: agents help when it is worth it and still refuse to die for it. Three phases of searching (12, 13, 14) now agree from three different directions.
3. **The replicated finding is the liberation effect, and it reframes what rescue is.** With any nonzero help, the trapped pool at the onset+50 snapshot collapses from 70-75 to 18-28 on both seed sets: cohesive pairs are adjacent when the storm strikes, so the helping hand is already in place, and most of the rescue that will ever happen happens immediately, through proximity, before anything looks like a decision. The expedition, the going-back-in, is a rounding error next to the standing-beside.
4. **W2 FAILS to replicate as declared.** The original seeds showed post-snapshot extraction rising with help at care 1.0 (0.28 / 0.41 / 0.52); fresh seeds show 0.19 / 0.22 / 0.21, on residual pools of roughly twenty agents per cell: small-n noise, and the claim is withdrawn pending a designed protocol. The residue left after the liberation wave is precisely the pairs that were not adjacent, and studying expedition-rescue for them requires a scenario that strands partners apart at onset, which cohesion makes naturally rare: a declared follow-up design, not run here.
5. The care-regime golden freezes care 1, help 1 (seed 42, 256 of 400 alive).


## Addendum, pre-registered 2026-07-24 before running: stranded pairs

W2 was withdrawn on residual pools of roughly twenty agents per cell: cohesion makes stranded pairs naturally rare, and the declared fix was a scenario that strands partners apart at onset. The distant-death protocol has since validated a separator that uses an existing axis: scarcity. Design: the W-arena verbatim (mire, full sight h 60, tau_safety 12, care 1.0) with n_food 40 and nothing else changed. The stranded cohort, per cell, snapshotted at tick 2050 exactly as W2 was: caught agents (alive, inside the storm) whose partner is alive, outside, and farther than r_help away, so the liberation wave cannot have freed them. Observation window 1200 ticks, matching W2. Declared before running:

* **S1, power floor**: at least 100 pooled stranded-caught agents in each help cell (help 0, 0.5, 1.0) on declared seeds 1-24; otherwise the separator failed in this arena and the report says so.
* **S2, the resurrected W2, falsifiable direction**: extraction of the stranded (alive and outside the storm at window end) is monotone non-decreasing in help_strength at care 1.0, and the help 1.0 cell exceeds the help 0 cell by at least 10 points. Replication on fresh seeds 31-54 against the same bars before packaging.
* **S3, rescue cost, measured either way, no bar**: mortality of the stranded agents' free partners per help cell, both stages. If help extracts the trapped by killing the rescuers, the numbers will say so and the article will carry both.
* Note for honesty: the tick-2050 snapshot is 50 ticks post-onset, so cohorts are not identical across help cells; they are per-cell cohorts exactly as in W2.

### Amendment to the stranded-pairs registration, 2026-07-24, before any outcome data

The design check killed the scarcity separator: in the full-sight W-arena, n_food 40 is a famine. Spot checks on seeds 99, 7, and 15 (cohort counts at the snapshot only; no outcomes were computed, and 7 and 15 are declared seeds, so the peek is recorded here) found 146 to 177 of 400 agents alive at tick 2050, storm-caught counts of 0 to 7, and zero stranded agents: caught agents' partners were already dead of the famine. S1 was unpassable and the protocol was not run as first registered. The distant-death arena tolerated scarcity because its agents were myopic; the full-sight arena starves under it.

Amended separator, using spawn geometry instead of hunger: **storm_onset 100**. Pairs spawn at random positions and converge over hundreds of ticks, so an early storm catches them still apart. n_food returns to default; everything else stays the W-arena verbatim, care 1.0. Snapshot at tick 150 (50 post-onset, matching W2's offset), observation window 1200 ticks, cohort definition unchanged (caught, partner alive, outside, beyond r_help). S1, S2, S3 and both seed sets stand exactly as declared above. One design-confirmation run on unused seed 99 is permitted to verify the cohort forms; declared seeds will not be touched again before the protocol runs.

### Closure of the stranded-pairs protocol, 2026-07-24: one body

The protocol closes at the design stage, unrun, because every separator failed its design check, and the pattern of failure is itself the result. All checks below used unused seeds (96 to 99) except where the earlier amendment records its peek; no outcomes were ever computed on declared seeds; no formal S1/S2/S3 verdicts exist because no registered protocol ran.

* Famine (n_food 40): kills 55 to 63 percent of the world before onset; caught agents' partners are already dead. The full-sight arena starves where the myopic distant-death arena merely dispersed.
* Early storm (onset 100, snapshot 150): pairs converge from random spawn to median distance 2.6 within 150 ticks; the storm arrives to find them already inseparable, and an unsettled world puts almost nobody in its path (1 caught of 400).
* The dense-wide funnel (n_agents 800, n_food 300 to hold per-capita supply, storm_radius 15, snapshot at onset): 269 caught across four seeds, of whom 5 had a living partner outside. 98.1 percent of caught agents are caught together with their partner.
* **The finding, structural and unregistered**: in this model a bonded pair is one body. Median pair separation, 2.6, is small against every storm the arena can throw, so pairs are either both caught or both free, and the stranded case W2 wanted to study occurs at the rate of a rounding error. W2 stays permanently withdrawn: its original extraction gradient was noise measured on a population of freaks. The expedition-rescue question is not underpowered here, it is unanswerable, and answering it would require a mechanism that separates partners as part of ordinary life (individual duties, solitary foraging roles), which is a capability decision for a future phase, not an axis to torque now.
* The registered instrument (`scripts/validate_phase14_stranded.py`) is kept as the record of what was designed.