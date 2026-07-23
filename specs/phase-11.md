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

(To be filled at implementation.)
