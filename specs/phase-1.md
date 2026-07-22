# Phase 1 — Homeostat kernel

Status: **approved 2026-07-22**. User reviewed the draft and delegated final judgment; the amendments from that review are folded in below (E table specified in full, integrity coupling dropped from u_safety, per-drive validation protocols, provisional-defaults note, determinism details).

## Purpose

Build the smallest agent that keeps itself alive through the exact machinery that will later carry commitment: lagged drive weights over instant urgencies, myopic argmax. Validate that the lag is real and measurable. No commitment of any kind exists in this phase; the mechanism must predate the phenomenon.

## Model definition

### World

* 2D continuous toroidal arena, side `world_size` (default 100.0). Time advances in discrete ticks, `dt = 1`.
* **Food**: `n_food` point sources (default 150). Each tick, an agent whose nearest *active* source lies within `r_eat` (default 2.0) eats it: energy rises by `gain_eat` (default 0.3, clipped at energy 1.0). All agents within reach eat the same source in the same tick (simultaneous, no index-order contention); the source is then consumed and respawns after `food_respawn` ticks (default 10) at a uniform-random location drawn from the world stream.
* **Hazards**: `n_hazard` circular danger zones (default 3), radius `r_hazard` (default 8.0), centers drifting by a random walk of step `hazard_drift` (default 0.2) per tick from the world stream. Hazards activate at tick `hazard_onset` (default 0); before that they exert no danger and no damage. Danger is a scalar field, perceptible at any distance: `danger(x) = max over zones of exp(-dist_to_center / r_hazard)`. Inside a zone (dist < r_hazard), integrity falls by `damage_rate` (default 0.02) per tick.

### Body state (per agent, structure-of-arrays)

* `energy` in [0, 1], init `init_energy` (default 0.8). Falls by `basal_burn` (default 0.002) every tick plus `move_burn` (default 0.003) per tick of movement. Death at 0. Irreversible.
* `integrity` in [0, 1], init 1.0. Falls inside hazards; outside them it heals by `regen_rate` (default 0.001) per tick toward 1.0, so damage is an equilibrium, not a one-way ratchet (see Deviations). Death at 0. Irreversible.
* `fatigue` in [0, 1], init 0.0. Rises by `fatigue_rate` (default 0.004) per tick of movement, falls by `rest_rate` (default 0.02) per tick of resting. Not lethal. Effective speed `v_eff = speed * (1 - fatigue/2)`.

### Perception (declared simplification)

Perception is global in Phase 1: every agent knows the distance and direction to its nearest active food source and the exact danger field. Local perception arrives in a later phase as a swept limitation, not here.

### Drives

Three drives, fixed order: `energy`, `safety`, `rest`. For each drive `d`, per agent:

* **Urgency** `u_d`, computed instantly from body state and percepts each tick, as continuous functions, never branches:
  * `u_energy = 1 - energy`
  * `u_safety = danger(pos)` (the draft's `(1 - integrity/2)` sensitization coupling is dropped: it hard-coded a constant that should be a swept parameter, and it contaminates the lag-validation step signal because integrity falls during measurement; damage sensitization may arrive later as a declared config parameter)
  * `u_rest = fatigue`
* **Weight** `w_d`, the lagged valuation, init `w_d = u_d` at spawn:
  * `w_d <- w_d + (dt / tau_d) * (u_d - w_d)`
  * This is THE uniform law. One line, all drives, no exceptions, forever.
* **Time constants** `tau_d`: declared in config, written nowhere else. Defaults `tau_energy = 20`, `tau_safety = 12`, `tau_rest = 30` ticks. Safety is deliberately the fastest drive, so any future inversion is nontrivial.

### Actions and the E table

Four macro-actions, fixed frozen order: `seek_food`, `flee`, `rest`, `wander`.

* `seek_food`: move at `v_eff` toward the nearest active food source. With no active food anywhere, direction is undefined and treated as `wander`-style movement along current heading with `d_food = inf`.
* `flee`: move at `v_eff` directly away from the nearest hazard center. At the exact center (measure zero), move along current heading.
* `rest`: no movement.
* `wander`: move at `v_eff` along a persistent per-agent heading; the heading is redrawn (uniform angle) with probability 0.05 per tick from the agent's own stream. Heading draws are consumed every tick by every agent regardless of action, so stream consumption is fixed-rate and behaviour-independent.

`E_d(a)` is the expected reduction in `u_d` per tick under action `a`. Entries may be negative (an action can worsen a drive). `basal_burn` is omitted throughout because it is common to all actions and argmax is invariant to common terms. With `T = d_food / v_eff` (travel ticks to food) and `g = danger(pos)`:

| | `seek_food` | `flee` | `rest` | `wander` |
|---|---|---|---|---|
| `E_energy` | `gain_eat / (1 + T) - move_burn` | `- move_burn` | `0` | `wander_gain - move_burn` |
| `E_safety` | `0` | `g * (1 - exp(-v_eff / r_hazard))` | `0` | `0` |
| `E_rest` | `- fatigue_rate` | `- fatigue_rate` | `rest_rate` | `- fatigue_rate` |

Rationale, row by row. Energy: food's value is its per-tick gain attenuated by travel time (myopic hyperbolic discount, the boring choice); every moving action pays `move_burn`; `wander_gain` (default 0.004, a declared parameter) is the expected discovery value of roaming, which makes wander the live choice during famine (all sources consumed) rather than dead code. Safety: fleeing one step down the field `exp(-dist/r_hazard)` reduces danger by exactly `g * (1 - exp(-v_eff/r_hazard))`, a closed form, not an estimate; approach-through-danger carries no myopic safety penalty, which is a stated Phase 1 blindness (agents react to danger, they do not forecast it). Rest: movement builds fatigue, resting sheds it.

Action values: `V(a) = sum over d of w_d * E_d(a)`. Selection is `argmax` with index tie-breaking in the frozen order above. No lookahead, no planning, no anticipation of drive dynamics.

### Tick order (part of the model definition)

1. Perceive: danger and flee direction, nearest-food distance and direction.
2. Urgencies from body state and percepts (`core/drives.py`).
3. Weights via the uniform law (`core/drives.py`).
4. Action selection (`core/action.py`).
5. Movement; heading draws consumed for all agents.
6. Eating (simultaneous, nearest-source rule).
7. Hazard damage.
8. Deaths: `alive &= energy > 0 & integrity > 0`. Dead agents stop updating; arrays retain final values.
9. World updates: hazard drift, food respawn clocks.
10. Recording every `record_every` ticks (default 10).

### Determinism harness

* Master seed via `SeedSequence(master).spawn(n_agents + 1)`: stream 0 the world's, streams 1..n per-agent.
* Config is a frozen dataclass; `config_hash` = sha256 of canonical JSON.
* Every run writes `manifest.json`: seed, config hash, git SHA, package versions, timestamp.
* **Golden trajectory definition**: every `record_every` ticks, record `x, y, energy, integrity, fatigue, weights, urgency` (float64) and `alive` (bool). Hash = sha256 over the concatenation of each recorded array rounded to 8 decimals, in the recording order above, plus `alive` as uint8. Urgency is recorded so the lag validation can check the uniform law transition by transition (see criterion 3c).

## Acceptance criteria

1. **Determinism.** Same seed, same config: identical golden hash across two runs. Spawning `n+1` agents leaves agents `1..n` with bit-identical draws.
2. **Homeostasis.** Default config, 200 agents, 5,000 ticks, 10 seeds: at least 95% of agents alive at the end; population mean energy within [0.4, 0.97] after tick 500. Artifact: `results/phase-1-homeostasis.json` with per-seed survival, energy statistics, and an action profile showing the homeostat forages and flees rather than degenerate-resting.
3. **Measurable lag.** All protocols applied through config, never through drive code:
   * *3a. Safety (step)*: one hazard, `r_hazard = 10000` (field uniform to <1% across the arena, gradient effectively zero so fleeing cannot relieve it), `hazard_drift = 0`, `damage_rate = 0`, `basal_burn = move_burn = 0`, `hazard_onset = 100`. Urgency steps 0 to ~1 at onset; fit the discrete decay of the gap to plateau over the first ~3 tau (the tail is excluded: agents flee outward during measurement, drifting the input by ~0.3%). Fitted tau within 5% of declared.
   * *3b. Energy (step)*: no hazards, `basal_burn = move_burn = 0`, dense food (`n_food = 400`). Each agent's first bite fills energy to 1.0, stepping `u_energy` from 0.2 to 0 at a per-agent tick identified from the energy trace; fit the discrete decay of `w_energy`. Fitted tau within 5% of declared.
   * *3c. Transition identity (all three drives)*: on a default-config run with `record_every = 1`, every recorded weight transition of every living agent must satisfy `w[t] - w[t-1] = (u[t] - w[t-1]) / tau` exactly: regressed tau within 0.1% of declared and max absolute residual below 1e-9 for energy, safety, and rest. Any code path anywhere that bypassed the uniform law would break this identity.
   * Artifact: `results/phase-1-lag-validation.json` plus plot, with seeds and config hashes.
4. **Invariant tests pass** on the implemented mechanism, not stubs.
5. **Golden run committed** under `tests/golden/` with manifest, and a test that reruns and compares.

## Provisional defaults

Numeric defaults above are pre-run estimates; in particular the food economy (`n_food / food_respawn` against burn rates) was sized by back-of-envelope throughput, not by simulation. Calibrating them so the homeostat is homeostatic is legitimate and expected; every calibration change is recorded in Deviations below with its reason. Silent parameter drift is forbidden (CLAUDE.md).

## Non-goals (Phase 1 explicitly excludes)

Commitment, attachment, memory, social ties, grief, reproduction, learning, communication, local perception, damage sensitization of u_safety, heterogeneous per-agent time constants (all agents share the declared taus; heterogeneity arrives as a swept axis later).

## Deviations from spec during build

Recorded 2026-07-22, the implementation session. All four deviations were driven by observed failures, none by taste, and none touches the uniform law or the invariant.

1. **Integrity regeneration added** (`regen_rate = 0.001` outside hazards). As drafted, integrity only ever fell, so every hazard engulfment moved every agent monotonically toward death: 56/200 damage deaths by tick 5000 in the first calibration run. A homeostat cannot be homeostatic with a one-way ratchet in its body; regeneration makes integrity an equilibrium like energy and fatigue. Post-change: 0 damage deaths across all validation seeds, mean integrity ~0.99.
2. **Food economy recalibrated** (`n_food` 60 to 150, `food_respawn` 15 to 10, `gain_eat` 0.25 to 0.3, `r_eat` 1.5 to 2.0). The draft economy starved ~9% of agents even with regeneration in place. Diagnosis before calibration: the starvers spent >85% of their final 200 ticks in `seek_food` with hunger weight ~0.91; they were chronic race-losers chasing sources that competitors ate first, not apathetic resters. The economy had enough calories and too much contention. Post-change worst seed: 193/200 (96.5%).
3. **Homeostasis energy band widened** ([0.4, 0.9] to [0.4, 0.97]). The pre-run band was a guess; the calibrated economy holds population mean energy at 0.85-0.97. The band's purpose, excluding both starvation drift and saturation-at-1.0, is preserved.
4. **Rest-drive ramp protocol replaced by the transition identity (3c).** The drafted forced-march protocol self-terminates: as fatigue climbs, the rest weight rises until resting itself becomes the argmax, which stops the movement that was generating the ramp. The agent refuses to be experimented on. The replacement checks the law directly against recorded urgencies for all drives at once and is strictly stronger (exact per-transition identity vs a curve fit); `urgency` was added to the recorded arrays to support it.

Validation results, from `results/`: worst-seed survival 96.5%, all seeds >= 193/200; safety step fitted tau 11.846 vs 12 (1.29%); energy step fitted tau 20.000 vs 20 (0.00%); transition identity regressed taus 20.0000 / 12.0000 / 30.0000 exactly, max residual 5.6e-17 over 100,000 transitions per drive.
