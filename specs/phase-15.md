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

## Deviations from spec during build

(To be filled at end of implementation session.)
