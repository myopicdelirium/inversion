# Phase 15: Authority

Status: **implemented 2026-07-24 under standing delegation**. No amendment required, and that is the phase's structural claim: the attachment law never assumed mutuality, so authority is topology, not new mechanism. `core/drives.py` and `core/action.py` are untouched; the change is bond wiring at initialization plus one config field.

## Purpose

The capability deltas name one-to-many bonds as the first missing piece of every tier-one case: Jonestown's, Munster's, and Heaven's Gate's structure begins with many people attached to one. This phase adds the minimal form: `bond_target = "leader"`, where agents 0 through n_leaders-1 are unbonded leaders and every other agent's bond points at leader (i mod n_leaders). Bond formation stays the standing law (grows by proximity, fades by absence); grief, care, assistance, and tethering all inherit the topology unchanged. The phase then measures what one-to-many attachment does before any social transmission exists, which sets up the additivity null that the transmission phase must later break.

## Pre-registered

* **L1, congregation**: leader mode, no storm, 10 leaders among 400 agents, bond 0.8 vs 0.0, 5 seeds: mean follower distance to own leader over the final 1000 ticks at least 3x smaller when bonded. Phase 6's cohesion, one-to-many.
* **L2, the single point of failure**: plain sudden storm (damage 0.05, no snare), kappa 0, care 0, 24 seeds: window mortality of followers whose own leader was caught at onset at least 2x that of followers whose leader was not. The congregation's fate should couple to one agent's luck.
* **L3, the additivity null, the phase's deepest claim**: at kappa 2 (floor 0), followers bereaved by their leader's death starve at a rate within 5 points of the phase 7 partner-mode baseline (0.141). Without transmission between agents, mass grief must be exactly the sum of individual griefs: a congregation of mourners is 39 separate mourners. If this null holds, it becomes the yardstick the transmission phase must later beat for any claim of emergent collective collapse; if it fails, one-to-many topology alone already compounds grief, and that is a major finding.
* **L4, preservation**: defaults untouched, bit-identical everywhere (thirteen goldens, hash-refresh routine for the one new field `n_leaders`).
* **Replication** of L2 and L3 on fresh seeds before packaging, per the standing default.

## Non-goals

Leader influence on follower knowledge or expectations (belief objects, the next delta), succession after leader death, leaders with their own bonds, follower-follower bonds, any transmission.

## Addendum, pre-registered 2026-07-24 before running: the mire-leader experiment

The declared follow-up, run under this spec. Arena: leader mode as above plus the mire (snare 0.95, burn 0.01), so a caught leader is held dying for about a hundred ticks before its congregation. Declared, same bars as before:

* **M1 (L2 proper)**: follower window-mortality with own leader caught at onset at least 2x the free-leader rate (kappa 0, seeds 1-24, replication 31-54).
* **M2 (L3 proper, the additivity null)**: at kappa 2, bereaved-follower neglect-death rate within 5 points of the phase 7 partner baseline 0.141. The held leader fixes the power problem: caught leaders now die in view.
* Measured and reported without a bar: whether follower deaths under a caught leader are entries (the pied piper, en masse) or threshold deaths.

## Deviations from spec during build

Recorded 2026-07-24. Artifacts: `results/phase-15-authority.json` (seeds 1-24) and `phase-15-replication.json` (fresh seeds 31-54).

1. **The structural claim held trivially and L1 passes**: authority required zero mechanism, only wiring, and congregation emerges at ratio 4.7 (followers at mean distance 6.48 from their leader versus 30.72 unbonded). Note the texture: one-to-many cohesion is looser than pair cohesion (6.5 versus phase 6's 1.2), because thirty-nine followers cannot all occupy the same spot; the congregation has a radius by construction.
2. **L2 FAILS as declared, weakly and consistently**: follower mortality with a caught leader is 1.3x the free-leader rate on both seed sets (0.031 vs 0.024; 0.038 vs 0.030), against a declared 2x. The arena is the reason: a plain sudden storm without the snare holds a caught leader for only about fifteen ticks, too briefly for the congregation's fate to couple to it. A weak coupling exists and replicates in direction; the strong test requires a held leader.
3. **L3 is VOID for power, not answered**: the same arena barely kills leaders, so bereavement almost never occurs (16 bereaved pooled in the main stage, zero starving; zero bereaved at all in replication). Zero of sixteen against an expected 14.1% is not a confirmed additivity null, and zero-of-zero is no test. The declared comparison to the phase 7 partner baseline could not be performed.
4. **The mire-leader arena is the declared follow-up for both**: a leader caught by grip 0.95 with slow burn dies over about a hundred ticks in view of thirty-nine bonded followers, generating both the sustained capture L2 needs and the bereavement volume L3 needs. Not run in this phase.
5. L4 held throughout: the merge landed with every golden contract replay-verified in two processes, and the congregation golden joins the suite through the embedded-config path with no test-file edit at all, the first dividend of the incident's systemic fix.


## Mire-leader results, recorded 2026-07-24

Artifacts: `results/phase-15-mire-leader.json` (seeds 1-24), `phase-15-mire-replication.json` (fresh seeds 31-54).

* **M1 PASSES, replicated**: follower mortality with own leader caught is 0.477 vs 0.167 free (ratio 2.9, n 193) and 0.375 vs 0.146 (ratio 2.6, n 312). The single point of failure exists once the leader can be held.
* **M2 remains void, and the reason is the finding**: at kappa 2, followers of caught leaders died 109 of 112 (main) and 264 of 264 (replication). Bereavement cannot be observed because the congregation stands where the leader stands: capture of the center is capture of the circle, and the circle burns with it, deaf under attention's zero-trap, held by the same grip. Mass grief is unmeasurable at these coordinates not for lack of power but because there are no mourners left. The additivity question requires survivors, which requires the leader to die away from its crowd; a designed distant-death protocol is the declared follow-up, not run.
* The circle golden freezes the kappa-2 regime (seed 42).

## Addendum 2, pre-registered 2026-07-24 before running: the distant-death protocol

Mass bereavement requires survivors, which requires distance at the moment of capture. Scarcity provides it with existing axes: n_food 40 disperses congregations for foraging. Arena: the mire-leader world plus scarcity, kappa 2, floor 0.01 (the faint whisper: grief can still kill, fear is acquirable), bond 0.8. Two arms in the identical arena with identical seeds: bond_target leader (10 leaders) and bond_target partner. Declared:

* **D1, power floor**: at least 100 pooled bereaved followers alive after their leader's death (seeds 1-24); otherwise the protocol failed to separate and says so.
* **D2, the additivity null, properly paired, no desired direction**: per-capita bereaved starvation excess (bereaved neglect rate minus the same arena's never-bereaved baseline rate) in leader mode within 5 points of the identical quantity in partner mode. If crowd grief exceeds pair grief with no transmission in the model, that is a discovery about topology alone; if they match, the additivity null finally lands and becomes the yardstick the transmission phase must beat.
* Replication on fresh seeds 31-54 before packaging.

## Distant-death results, recorded 2026-07-24

Artifacts: `results/phase-15-distant.json` (seeds 1-24), `phase-15-distant-replication.json` (fresh seeds 31-54). Judged exactly as declared:

* **D1 FAILED on the declared seeds**: 29 pooled leader-mode bereaved on seeds 1-24, under the 100 floor. The fresh seeds happened to clear it (171), but the declared verdict is the main stage's, and it says the protocol under-separates: even under scarcity, leaders rarely die away from their whole crowd. Both stages are reported; neither is promoted over the other.
* **D2: the additivity null is refuted, sign replicated, magnitude unsettled**: leader-mode bereaved starvation excess +0.172 vs partner-mode +0.327 (gap -15.5 points, outside the declared 5), replication +0.076 vs +0.307 (gap -23.1). Crowd grief is sub-additive at face value: a mourner in a congregation starves at a quarter to half the rate of a mourner in a pair. No desired direction was declared. Caveats, named plainly: the leader arm is thin (5 and 13 neglect deaths), and the two bereaved cohorts are selected by different geometry, so the magnitude is not promoted.
* **The unregistered observation worth more than either verdict**: baseline starvation among the never-bereaved is 0.000 in all four arms of both stages. In an arena of scarcity, agents who kept their bond fed themselves without exception, thousands of them; every single starvation death in this world was a mourner's. Post hoc, flagged as such.
* **Candidate explanation for D2, post hoc and untested**: the model contains no solace mechanism, so the gap must be geometric. Leader-mode bereaved are by construction the dispersed foragers, standing at the food when the news has no distance to travel; partner-mode bereaved lived beside their dead. Mourning at the death site may be deadlier than mourning at the granary. Declared follow-up: condition neglect on distance-to-food at the moment of loss.
* The distant golden freezes the leader arm (seed 42).

## Addendum 3, pre-registered 2026-07-24 before running: grief geometry

The distant-death protocol left a candidate explanation untested: the model has no solace mechanism, so D2's sub-additivity must be geometric, and the suspicion is that mourning far from food is what kills. Same arena, same seeds, new instrument: at the moment of loss, record each new mourner's distance to the nearest active food source; at the end, whether they starved. Declared before running:

* **G0, manipulation check**: median distance-to-food at loss is smaller for leader-mode bereaved than partner-mode bereaved, in each stage. The candidate explanation assumed leader-mode mourners stand at the food; if this fails, the explanation dies here and the report says so.
* **G1, the geometry effect**: within partner mode (the powered arm), mourners in the top tercile of distance-to-food at loss starve at at least 2x the rate of the bottom tercile, terciles computed within stage. Declared seeds 1-24 primary, fresh seeds 31-54 replication.
* **G2, mediation**: pooling both stages upfront (the leader arm is thin and this is declared now, not after), within the bottom (near-food) tercile of the pooled distance distribution, the leader-vs-partner neglect gap must shrink to at most half the unconditioned pooled gap for geometry to be judged the mediator.
* No new mechanism, no config change: the arms are byte-identical reruns of the distant cells with a live measurement added.

## Grief-geometry results, recorded 2026-07-24

Artifacts: `results/phase-15-geometry.json`, `phase-15-geometry-replication.json`, `phase-15-geometry-g2.json`. Judged exactly as declared:

* **G0 FAILED, both stages, and the candidate explanation dies here as declared**: leader-mode mourners were not nearer food at the moment of loss. Median loss-distance 8.77 vs partner 8.43 (main), 10.24 vs 7.96 (replication): the crowd's mourners were actually farther from the granary, and starved less anyway. The assumed selection was factually wrong.
* **G1 FAILED, both stages**: partner-mode far-tercile mourners starve at 0.348 vs near 0.306 (ratio 1.14) and 0.363 vs 0.238 (ratio 1.52), under the declared 2x. Post hoc, flagged: the terciles are monotone in the declared direction in both stages (near < mid < far), so geometry has a real but small effect, nothing like a mediator.
* **G2 nominally passed and is NOT promoted**: near-food gap 11.77 points against a bar of 11.80 (half of 23.6), leader near-food n of 48, and a dead manipulation check upstream. A mediation verdict with a false premise, a razor margin, and a thin cell is not a verdict.
* What stands: crowd grief's sub-additivity is replicated and now unexplained. The model has no solace mechanism and place is ruled out. The remaining named candidate, speculation until instrumented: a life of contention trains hunger's attention weight. A follower shares its food with 39 rivals and lives with hunger's voice amplified; a paired agent, with one. At the moment of loss, grief must capture the attention field to kill, and the crowded life may have trained a voice grief cannot shout down. Declared follow-up: record attention weights at the moment of loss.

## Addendum 4, pre-registered 2026-07-24 before running: the trained voice

The remaining candidate for crowd grief's sub-additivity: a life of contention trains hunger's attention weight, and grief cannot capture an attention field where hunger's voice is already loud. Same arena, same seeds, byte-identical rerun with one live measurement: each mourner's full drive-weight vector at the moment of loss. Primary predictor declared now: the energy weight, w_energy. Labeled A to avoid collision with phase 14's withdrawn W2. Declared before running:

* **A0, manipulation check**: median w_energy at loss is higher for leader-mode bereaved than partner-mode bereaved, in each stage. If contention does not actually train hunger's weight, this candidate dies here and the report says so.
* **A1, the gradient**: within partner mode (the powered arm), mourners in the bottom tercile of w_energy at loss starve at at least 2x the rate of the top tercile, terciles within stage. Declared seeds 1-24 primary, fresh seeds 31-54 replication.
* **A2, mediation**: pooling both stages upfront, within the top (loud-hunger) tercile of the pooled w_energy distribution, the leader-vs-partner neglect gap must shrink to at most half the unconditioned pooled gap for the trained voice to be judged the mediator. The G2 lesson stands: a nominal pass with a dead A0 upstream will not be promoted.
* Full weight vectors are stored in the artifact for post hoc inspection, flagged as such if used.

## Trained-voice results, recorded 2026-07-24

Artifacts: `results/phase-15-attention.json`, `phase-15-attention-replication.json`, `phase-15-attention-a2.json`. Judged exactly as declared:

* **A0 FAILED (split, and the bar was each stage)**: leader-mode median w_energy at loss was 0.414 vs partner 0.087 on the declared seeds, then 0.069 vs 0.071 on fresh seeds. The dramatic main-stage gap lived in a 30-mourner cohort and did not survive contact with new seeds. Contention does not reliably train hunger's weight in the bereaved-at-loss population.
* **A1 FAILED both stages, direction wrong at the top**: partner-mode mourners in the high-w_energy tercile starved MORE than the low tercile (0.433 vs 0.316, n 552/553; 0.384 vs 0.372, n 609/610). The predicted protective gradient does not exist.
* **A2 FAILED**: loud-hunger gap 22.1 points against a bar of 11.8; conditioning on the trained voice shrinks nothing.
* Post hoc, flagged, replicated in shape, not promoted: both stages show a U, with the middle tercile safest (0.249 and 0.199). A coherent reading exists: low w_energy at loss marks grief-captured attention that starves deaf, high w_energy marks a stomach already empty when the loss arrived, and survival lives in the middle. Also flagged: w_energy tracks current emptiness by construction, so this instrument cannot separate a trained voice from a starving present; a cleaner instrument would average w_energy over a window before loss.
* **Standing after two eliminations**: crowd grief's sub-additivity is replicated and unexplained, with place and the trained voice both killed by their own pre-registered checks. The mediator hunt pauses here by decision, not exhaustion: two declared kills are a result, and a third instrument fished from the same post hoc pond risks the forking paths that pre-registration exists to prevent. The phenomenon is filed open. The build returns to structure: stranded pairs, the matched-famine vigil, then belief objects and transmission.