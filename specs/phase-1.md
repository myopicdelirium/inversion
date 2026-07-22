# Phase 1 — Homeostat kernel

Status: **draft, awaiting review**. No mechanism code until this spec is approved.

## Purpose

Build the smallest agent that keeps itself alive through the exact machinery that will later carry commitment: lagged drive weights over instant urgencies, myopic argmax. Validate that the lag is real and measurable. No commitment of any kind exists in this phase; the mechanism must predate the phenomenon.

## Model definition

### World

* 2D continuous toroidal arena, side `L` (default 100.0). Time advances in discrete ticks, `dt = 1`.
* **Food**: `n_food` point sources (default 40). An agent within radius `r_eat` (default 1.5) of a source eats: energy rises by `gain_eat` (default 0.25/tick), and the source is consumed then respawns after `food_respawn` ticks (default 50) at a new uniform-random location drawn from the world RNG stream.
* **Hazard**: `n_hazard` circular danger zones (default 3), radius `r_hazard` (default 8.0), drifting with a slow random walk (step from the world stream). Inside a zone, integrity falls by `damage_rate` (default 0.02/tick). Danger is perceptible at any distance as a scalar field `danger(x) = max over zones of exp(-dist/r_hazard)`.

### Body state (per agent, structure-of-arrays)

* `energy` in [0, 1], init 0.8. Falls by `basal_burn` (default 0.002/tick) plus `move_burn` (default 0.003) per tick of movement. Death at 0. Irreversible.
* `integrity` in [0, 1], init 1.0. Falls in hazards. Death at 0. Irreversible. No regeneration in Phase 1.
* `fatigue` in [0, 1], init 0.0. Rises by `fatigue_rate` (default 0.004) per tick of movement, falls by `rest_rate` (default 0.02) per tick of resting. Not lethal; at `fatigue = 1` movement speed is halved (linear penalty in between).

### Drives

Three drives, fixed order: `energy`, `safety`, `rest`. For each drive `d`, per agent:

* **Urgency** `u_d`, computed instantly from body state each tick, in [0, 1]:
  * `u_energy = 1 - energy`
  * `u_safety = danger(pos) * (1 - integrity/2)` (danger matters more the more damaged you already are; a continuous function of state inside the uniform law, not a branch)
  * `u_rest = fatigue`
* **Weight** `w_d`, the lagged valuation, init `w_d = u_d`:
  * `w_d <- w_d + (dt / tau_d) * (u_d - w_d)`
  * This is THE uniform law. One line, all drives, no exceptions, forever.
* **Time constants** `tau_d`, declared parameters, per-drive, set at initialization, never written again: defaults `tau_energy = 20`, `tau_safety = 12`, `tau_rest = 30` ticks.

### Actions

Four macro-actions, fixed frozen order: `seek_food`, `flee`, `rest`, `wander`.

* `seek_food`: move at speed `v` (default 1.0, fatigue-scaled) toward the nearest food source.
* `flee`: move at speed `v` down the danger gradient.
* `rest`: no movement.
* `wander`: move at speed `v` in a persistent random heading (per-agent stream; heading redrawn with probability 0.05/tick).

Action values: `V(a) = sum over d of w_d * E_d(a)`, where `E_d(a)` is the expected urgency reduction of drive `d` under action `a`, computed by fixed closed-form rules from current percepts (distance to food, local danger, fatigue). The table of `E_d(a)` formulas is part of the model definition and lives in `core/action.py` with per-formula plain-language comments. Selection is `argmax` with index tie-breaking. No lookahead, no planning, no anticipation of drive dynamics.

### Determinism harness

* Master seed via `np.random.SeedSequence(master).spawn(n_agents + 1)`: stream 0 is the world's, streams 1..n are per-agent.
* Config is a frozen dataclass; `config_hash` = sha256 of its canonical JSON.
* Every run writes `manifest.json`: seed, config hash, git SHA, package versions, timestamp.
* Golden hashes computed over trajectory arrays rounded to 8 decimals.

## Acceptance criteria

1. **Determinism.** Same seed, same config: identical trajectory hash across two runs. Spawning `n+1` agents leaves agents `1..n` with bit-identical draws (SeedSequence spawn test).
2. **Homeostasis.** Default config, 200 agents, 5,000 ticks, 10 seeds: at least 95% of agents alive at the end; population mean energy stays in [0.4, 0.9] after tick 500.
3. **Measurable lag.** Step-change protocol: clamp `u_safety` from 0 to 1 at tick `t0` on an isolated cohort (via an environment that jumps danger, not by touching drive code), record `w_safety`, fit a single exponential. Fitted tau within 5% of declared `tau_safety`, per drive, for all three drives under analogous protocols. Artifact: `results/phase-1-lag-validation.json` plus plot, with seed and config hash.
4. **Invariant tests pass.** Static analysis of `core/drives.py` and `core/action.py` finds no forbidden patterns; tau written only at initialization; drive state mutated nowhere outside `core/drives.py`.
5. **Golden run committed.** One default-config run's rounded trajectory hash under `tests/golden/`, with manifest.

## Non-goals (Phase 1 explicitly excludes)

Commitment, attachment, memory, social ties, grief, reproduction, learning, communication, heterogeneous time constants across agents (all agents share the declared taus in Phase 1; heterogeneity arrives as a swept axis later).

## Deviations from spec during build

(To be filled at end of implementation session.)
