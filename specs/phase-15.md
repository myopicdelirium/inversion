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