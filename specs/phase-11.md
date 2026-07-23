# Phase 11: Farsight

Status: **spec ready 2026-07-23; implementation next session** (Amendment 4 is already in the constitution; spec written first, per the constitution, and deliberately left to cool before the largest kernel change since the beginning).

## Purpose

Every death in this model so far has been a mistake: lag, deafness, timing. Human devotion includes the clear-eyed kind. Amendment 4 permits the minimum machinery for it: action values become integrals of predicted WORLD consequences over a declared horizon, evaluated under the agent's current, frozen weights. The agent may see the price of a path; it may never reason about what it will want. The phase answers the program's deepest open question: is preference inversion only myopia, or does devotion survive foresight? Both answers are publishable; neither is desired.

## The mechanism (h-tick analytic rollout, `core/action.py`)

* `prospect_horizon` h, declared, default 0 = the existing closed forms, bit for bit (dual path, old table untouched at h 0).
* For h > 0, per action, closed-form integrals of predicted urgency reduction over h ticks under the agent's declared physics: straight-line motion at current effective speed, static known fields (drift and other agents unmodeled: agents predict physics, never minds), eating on predicted arrival, distress shrinking along the approach to the bond target, danger integrated along the path. All exp/geometric sums, vectorized, no simulation loop.
* `core/action.py` may not reference integrity at all (tripwire written before the mechanism): the felt price of a path is its integrated danger exposure, never a death predicate.
* V(a) = sum over drives of w_d times the predicted cumulative reduction. Argmax, frozen order. Weights frozen during evaluation.

## Pre-registered questions (directions deliberately not declared where the answer is the point)

* **Q1, preservation**: h 0 bit-identical everywhere.
* **Q2, the frog with foresight**: slow cook (ramp 400, bond 1.0, kappa 0) at h {0, 20, 60}: the boiling frog died of never integrating; a forecaster integrates. Declared: mortality at h 60 at most half of h 0.
* **Q3, THE question, no desired direction**: the mire rescue arm (phase 8 config, bond 0.8, kappa 0) at h 60. If the pull ratio collapses toward 1, inversion was myopia all the way down, and the phase diagram is a map of error. If entries persist at ratio 1.5 or more with the price visible, the model produces chosen sacrifice, and the vocabulary of the whole program changes. The model answers; we print the answer.
* **Q4, everyday null**: ordinary world at h 60 within 3 points of h 0 survival.
* **Q5, identity**: a unit test reconstructs V from a recorded snapshot and matches selection exactly.

## Acceptance criteria

1. Q1 through Q5 as written; Q3 reported whichever way it lands.
2. Tripwires before mechanism: the no-integrity rule for action.py; existing invariant suite untouched.
3. Artifacts, figure, one golden per newly named regime, deviations at whatever length honesty needs.

## Non-goals

Predicting other agents, predicting own drives (forbidden by Amendment 4, permanently), stochastic rollouts, learning or model updating, horizons as per-agent traits (a later axis).

## Deviations from spec during build

Recorded 2026-07-24. Full numbers in `results/phase-11-farsight.json` and `phase-11-replication.json`.

1. **A rollout coherence bug, caught by Q4 before any verdict was recorded.** The first implementation modeled held actions inconsistently: the safety row integrated a full-horizon approach as if the agent walked through its destination into the hazard forever (an exp(v h / scale) explosion that priced any food in a danger shadow as lethal), and the rest row ignored fatigue's floor, overvaluing rest roughly tenfold. Pre-fix numbers, kept for the record: everyday survival 0.133, mire arms with entered-share 0.00 (agents starving outside, not rescuing). Both rows were given the same arrival-and-saturation caps the energy row already had. This was a coherence fix to the declared physics, not tuning toward any result.
2. **Q1 passes**: all nine golden trajectories bit-identical at horizon 0. **Q5 passes**: farsighted selection reconstructs exactly (tests/test_farsight.py).
3. **Q2 passes emphatically and replicates**: slow-cook cohort mortality 1.000 / 0.977 / 0.114 at h 0 / 20 / 60 (seeds 1-6), and 1.000 to 0.018 on fresh seeds 11-16 against a declared bar of one half. The boiling frog is a disease of myopia: an integrator leaves the ramp early.
4. **Q3, the question, answered as pre-registered, and the answer is the first branch**: inversion was myopia all the way down, in every cell measured. Myopic baseline: pull 0.29 vs safe 0.12 (ratio 2.4, entered share 0.88). At h 60: pull 0.06 vs safe 0.18 (seeds 1-30) and 0.19 vs 0.16 (fresh seeds 31-60): both within their controls' noise bands (bond 0 ratios 0.8 and 1.3). The mechanism visible in the runs: en-route fear catch-up plus the visible held price abort rescues before entry. The phase diagram of phases 3 through 10 is, at these coordinates, a map of error: deaths the agents would not have died had they seen.
5. **Q4 FAILS as declared**: everyday survival 0.922 at h 60 vs 0.992 at h 0, a 7.0-point gap against the declared 3. Foresight is not free in the ordinary world; the cost is real and reported, its mechanism unmapped this phase.
6. **Post hoc, labeled: the knowing-and-going cell** (mire, bond 0.8, h 60, kappa 0.75, floor 0.05, seeds 1-30): ratio 0.7, no excess, entered share 0.80 of five deaths. Even with attention suppressing fear, foresight at these coordinates does not recreate the pull. The clear-eyed sacrifice region, if this architecture contains one, lies at coordinates not yet visited (deeper bonds, nearer trapped targets, other attention regimes), and locating it or proving its absence is the next map worth drawing.
