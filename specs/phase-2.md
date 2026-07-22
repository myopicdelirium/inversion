# Phase 2: Commitment as an ordinary drive

Status: **implemented 2026-07-22 under delegated approval**. The user granted implementation authority for the next phase; this spec was written before the mechanism, per the constitution, and stands for review at any time.

## Purpose

Introduce the first commitment: attachment to a home place, as a fourth drive of the same class as energy, safety, and rest. Same urgency-weight structure, same uniform law, no new mechanism. Three things must be proven: with no homes in the world, behaviour is bit-identical to Phase 1; attachment obeys its declared timescales exactly; and bonded agents show emergent tethering, the first behaviour in the model caused by an agent's history rather than its body.

## Model additions

### Nests and imprinting

* `n_nests` fixed nest locations (default 5), drawn from the world stream after hazards. Static, no drift.
* Each agent's home is assigned round-robin by agent index (`nests[i % n_nests]`), fixed for life.
* Agents are born at home: spawn position is the home plus a uniform jitter within `r_nest`, drawn from the agent's own stream (two draws, same count as the Phase 1 uniform spawn, so the no-nest branch consumes identical draws).
* With `n_nests = 0` there are no homes: spawn is uniform over the arena exactly as Phase 1, attachment stays zero, and every behavioural array is bit-identical to Phase 1 (verified against the recorded per-array golden hashes).

### Attachment state

* `bond` b in [0, 1] per agent. Init `bond_init` (default 0.5) for agents with a home, 0 otherwise: agents are born attached, which solves the cold start (attachment can only grow at home, but nothing pulls an unattached agent home).
* While within `r_nest` (default 3.0) of home: `b += bond_grow * (1 - b)` (default 0.002, roughly a 500-tick approach to full attachment).
* While away from home: `b -= bond_decay * b` (default 0.0002, roughly a 5000-tick fading).
* Body-state mechanics, written in `core/world.py` like fatigue. No clipping needed: both updates are contractions within [0, 1].

### The bond drive

* Drive order becomes `energy, safety, rest, bond` (appended, existing indices frozen).
* Urgency, separation distress: `u_bond = b * (1 - exp(-d_home / r_bond))`, `r_bond` default 25.0. Zero at home, approaches b far away. Instant, continuous, no branches. Homeless agents have b = 0, so u_bond = 0.
* Weight: the same one law, `tau_bond` default 60.0, the slowest drive. Declared in config, written nowhere.

### The return action

* Action order becomes `seek_food, flee, rest, wander, return_home` (appended, existing indices frozen).
* `return_home`: move at `v_eff` toward home. Fallback to heading direction when there is no home (never selected in that case, see below).
* E-table column: `E_bond(return_home) = b * exp(-d_home / r_bond) * (exp(v_eff / r_bond) - 1)`, the closed-form one-step reduction of u_bond. `E_energy(return_home) = -move_burn`, `E_rest(return_home) = -fatigue_rate`, `E_safety(return_home) = 0`. `E_bond` of every other action is 0, the same declared myopic blindness as safety.
* Preservation argument for the no-nest world: w_bond is identically 0, so it contributes exactly +0.0 to every action value; `V(return_home) = -move_burn * w_energy - fatigue_rate * w_rest <= 0 <= V(rest)`, and rest precedes return_home in the frozen order, so return_home is never selected. Trajectories are bit-identical.

### Tick order

Bond accumulation runs after eating and before damage, using post-move positions (an agent that reaches home this tick is at home this tick).

### Recording

`bond` is appended to the recorded arrays (after `urgency`). The combined Phase 1 golden hash is superseded by this shape change; the behavioural per-array hashes recorded in the prep commit are the preserved quantity. New full golden for Phase 2 defaults.

## Acceptance criteria

1. **Phase 1 preservation (exact).** With `n_nests = 0`, seed 42, 2000 ticks: per-array sha256 of x, y, energy, integrity, fatigue, alive all equal the Phase 1 golden per-array hashes. Enforced as a permanent test.
2. **Accumulation identity (exact).** Default config, `record_every = 1`: every bond transition of every living agent with a home satisfies the declared law (grow form at home, decay form away), max residual below 1e-9.
3. **Weight law identity (exact).** Criterion 3c of Phase 1 extended to four drives: regressed tau within 0.1% of declared, max residual below 1e-9, for energy, safety, rest, and bond.
4. **Emergent tethering.** Sweep `bond_init` in {0.0, 0.5, 1.0}, three seeds each, 3000 ticks, default nests: population mean distance-to-home over the final 1000 ticks is strictly decreasing in bond_init. This is the phase's behavioural product: attachment measurably pulls the foraging range toward home, and nothing in the code mentions territory, home range, or tethering.
5. **Homeostasis preserved.** Default config (nests present, bond_init 0.5), seeds 1-5, 5000 ticks: at least 95% survival, population mean energy in [0.4, 0.97] after tick 500.
6. **Golden.** `tests/golden/phase2_default.json` committed with combined and per-array hashes and manifest.

## Non-goals (Phase 2 explicitly excludes)

Bonds to other agents, loss of the bond target and grief, threat-onset collision environments, any commitment-versus-survival tradeoff (nests are never dangerous in Phase 2), heterogeneous bond parameters across agents, more than one home per agent.

## Deviations from spec during build

None. Implemented as specified; every default survived validation without recalibration.

Validation results, from `results/phase-2-validation.json`: behavioural preservation exact (all six phase 1 per-array hashes matched under n_nests = 0); bond accumulation identity exact, max residual 5.6e-17 over 100,000 transitions; weight law identity exact for all four drives (regressed taus 20.0000 / 12.0000 / 30.0000 / 60.0000); tethering strictly monotone, mean distance-to-home 36.08 (bond_init 0) vs 11.40 (0.5) vs 9.50 (1.0) over three seeds each; homeostasis worst seed 196/200 (98%). Phase 1 validation rerun under phase 2 code in a nest-free world reproduces the phase 1 numbers identically (safety 11.846, energy 20.000, identities exact).
