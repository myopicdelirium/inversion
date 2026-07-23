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

1. **W5, W4, W3 pass.** All twelve golden trajectories bit-identical with care and help at zero; the care urgency identity is exact to the bit (max residual 0.0e+00); the everyday tax is 0.3 points (0.993 vs 0.990). One anomaly recorded for the audit trail: during the preservation check, the phase 13 threshold golden reported a trajectory mismatch once, in a single scripted run, and passed identically on three immediate reruns with all nine per-array hashes matching; cause not reproduced, noted here rather than hidden.
2. **W1 answered, and replicated: the wager does not occur.** Zero clear-eyed and zero up-front deaths in all 18 cells across both seed sets. With the other priced into the ledger and hands that work, the model produces assistance, not sacrifice: agents help when it is worth it and still refuse to die for it. Three phases of searching (12, 13, 14) now agree from three different directions.
3. **The replicated finding is the liberation effect, and it reframes what rescue is.** With any nonzero help, the trapped pool at the onset+50 snapshot collapses from 70-75 to 18-28 on both seed sets: cohesive pairs are adjacent when the storm strikes, so the helping hand is already in place, and most of the rescue that will ever happen happens immediately, through proximity, before anything looks like a decision. The expedition, the going-back-in, is a rounding error next to the standing-beside.
4. **W2 FAILS to replicate as declared.** The original seeds showed post-snapshot extraction rising with help at care 1.0 (0.28 / 0.41 / 0.52); fresh seeds show 0.19 / 0.22 / 0.21, on residual pools of roughly twenty agents per cell: small-n noise, and the claim is withdrawn pending a designed protocol. The residue left after the liberation wave is precisely the pairs that were not adjacent, and studying expedition-rescue for them requires a scenario that strands partners apart at onset, which cohesion makes naturally rare: a declared follow-up design, not run here.
5. The care-regime golden freezes care 1, help 1 (seed 42, 256 of 400 alive).
