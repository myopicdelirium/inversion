# Phase 4: Sweep machinery and heterogeneous individuals

Status: **implemented 2026-07-23 under standing delegation** ("your job... move forward with the next step"). Spec written before mechanism; tripwire tests updated before the mechanism they constrain.

## Purpose

Two additions that make the phase diagram producible and give it the individual-depth axis. First, the sweep runner: declared parameter grids, parallel across runs only, deterministic aggregate output, every run carrying its seed and config hash. Second, heterogeneity: per-agent time constants and attachment depth drawn once at birth from declared population distributions, immutable for life (CLAUDE.md Amendment 2). The scientific target is representative agents in the strict sense: two populations identical in every declared parameter, differing only in spread, must be shown to produce different aggregate outcomes, and the storm's dead must be shown to be a biased sample of the traits, not a random one.

## Model additions

### Heterogeneity (the only kernel change)

* New per-agent state: `tau` (n, n_drives), each agent's own time constants, written once by `init_timescales` in `core/drives.py` and never again. The uniform law becomes `w += (dt / tau_i) * (u - w)` per agent: same law, personal clock.
* Draws, per agent, from the agent's own stream, at spawn, in fixed order, each made only when its spread knob is nonzero (draw count depends on config alone, never on behaviour):
  * `tau_safety_i = tau_safety * exp(tau_safety_spread * z)`, z standard normal. Lognormal; the declared value is the population median.
  * `tau_bond_i = tau_bond * exp(tau_bond_spread * z)`, likewise.
  * `bond_init_i = clip(bond_init + bond_init_spread * (2u - 1), 0, 1)`, u uniform.
* Config: `tau_safety_spread`, `tau_bond_spread`, `bond_init_spread`, all default 0.0. At zero there are no draws and no arithmetic change: all prior goldens must be bit-identical.
* Energy and rest time constants stay homogeneous this phase (axes for later, declared now).

### Sweep runner (infrastructure, `core/sweep.py`)

* A sweep is: base config overrides, ordered axes (config field to value list), seeds per cell, ticks.
* Parallel across runs only (constitution); results keyed and sorted by (cell, seed) so the output is byte-identical regardless of worker count or completion order.
* Per run: seed, config hash, survival, cohort storm mortality (window as in phase 3), trait summaries of dead and surviving cohort members.
* Output: one JSON artifact per sweep, with a manifest.

## Acceptance criteria

1. **Preservation.** All spreads zero: phase 1 behavioural hashes, phase 2 golden, and both phase 3 regime goldens all bit-identical (stored config hashes refreshed for the new fields, trajectory hashes verified unchanged in the same run, same routine as phase 3).
2. **Immutability.** Runtime test: per-agent time constants copied at init are bit-identical after 300 ticks under a storm with all spreads nonzero. Static test: time-constant writes exist only in `core/config.py` and init functions of `core/drives.py`.
3. **Distribution fidelity.** n = 2000 agents, spreads (0.5, 0.5, 0.25): sample median of each heterogeneous tau within 5% of declared, sample sigma of log-tau within 5% of declared spread; bond_init sample mean within 0.02 of declared.
4. **Sweep determinism.** The same sweep spec run with 1 worker and with 4 workers produces identical JSON bytes (hash equality).
5. **Spread shapes aggregates.** Flagship storm cell (sudden storm, bond 1.0), homogeneous vs `tau_bond_spread = 0.5` (same declared median 60), 5 seeds each: pooled cohort mortality differs by more than twice the between-seed standard deviation. Same declared parameters, different populations, different death tolls: the mean is not the model.
6. **The dead are a biased sample.** In the heterogeneous flagship cell: the median `tau_bond` of storm-dead differs from that of surviving cohort members with consistent sign in at least 4 of 5 seeds; same test for `bond_init` under `bond_init_spread = 0.25`. Report effect sizes.
7. **Golden.** One heterogeneous storm golden committed (all three spreads nonzero) plus the sweep-determinism artifact.

## Non-goals

Heterogeneous energy/rest taus, bond_grow/bond_decay/r_bond spreads, correlated traits, inheritance or trait evolution, the full production phase diagram (Phase 5), any change to urgencies, the E table, or action selection.

## Deviations from spec during build

Recorded 2026-07-23. Full numbers in `results/phase-4-validation.json`.

1. **Criterion 5 FAILS as declared, and the extension refutes the fallback hypothesis too.** At the flagship cell, homogeneous and heterogeneous pooled mortality are 0.251 vs 0.251. Extending along the already-declared ramp axis: 0.251/0.251, 0.487/0.482, 1.000/1.000, 1.000/1.000. Spread does not move the aggregate death rate anywhere on the measured map, including at saturation, where the expectation was that slow-clocked individuals would survive the slow cook (they do not: in the gradual-arrival regime no moment ever justifies leaving, for any clock speed on the drawn range).
2. **Criterion 6 PASSES strongly, which makes deviation 1 a finding rather than a null.** In the same runs whose aggregate is spread-invariant, the dead are a heavily biased sample: median tau_bond of storm-dead 58.6 vs 67.7 for survivors (fast attachment clocks return sooner and die), bond_init of dead 0.603 vs 0.479 for survivors, signs consistent across seeds. Stated plainly: in this system individual depth does not change how many die; it determines who. The toll is a property of the environment and the shared law; the names on the toll are a property of the individuals. For Phase 5 this cuts both ways: the mortality phase diagram is likely robust to trait spread (good for its generality), and survivor-composition maps are a second, separate product worth producing.
3. **A consistency-check bug was fixed during validation, before any judgment was recorded**: the 4-of-5 sign rule was implemented as requiring |sum of signs| >= n-1, which demands near-unanimity; corrected to the arithmetic the spec states (|sum| >= 2k - n).
4. **Stored config hashes of the phase 2 and phase 3 goldens refreshed** for the three new spread fields, each after verifying the golden trajectory hashes bit-identical in the same run, including through the per-agent tau-array refactor of the update law (division by a filled array vs a broadcast vector is bit-identical at zero spread).
