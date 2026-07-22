# CLAUDE.md: Project Constitution

This file is loaded at the start of every session. It is binding. Read `docs/BUILD_BRIEF.md` before writing code in a new phase.

## What this project is

A population-scale agent-based model in which agents develop commitments that can, under discoverable conditions, outrank their own survival.

The scientific product is not "agents can self-sacrifice." It is the phase diagram: the map of exactly which environmental and psychological parameter regions produce preference inversion, and which do not. A model that produces inversion everywhere is as worthless as one that produces it nowhere.

## THE PRIME INVARIANT

Preference inversion must be emergent. Never scripted.

Concretely, the following are forbidden anywhere in the codebase:

* Any conditional branching on death, mortality, threat level, damage, or health state that assigns, scales, or overrides a drive weight.
* Any `if commitment > X` (or equivalent) that grants a drive priority.
* Any special-case, flag, or code path named or scoped to sacrifice, martyrdom, heroism, altruism, or equivalent.
* Any hand-tuning of parameters whose purpose is to make a specific agent or run produce sacrifice.

Sacrifice must be the ordinary output of `argmax` over the standard action-value function, with no term that exists to produce it. If it appears, it appears because the accumulation dynamics and the environment made it the highest-valued action.

This invariant is enforced by `tests/test_invariants.py::test_no_scripted_override`, which performs static analysis of `core/drives.py` and `core/action.py`. Do not modify, weaken, skip, or exclude that test. If it fails, the code is wrong, not the test.

If you believe the invariant makes a requested feature impossible: stop, and say so in your response. Do not route around it.

### Amendment 1 (2026-07-22): the protected quantity is the time constant

Survival is the base attractor. Every drive, survival included, responds to body state through one uniform lagged update law. Inversion, when it occurs, is a timing failure: commitment has absorbed valuation over time and the reversion dynamics cannot restore survival's dominance before the decision is forced. Nothing ever ranks a commitment above life; life fails to reassert itself in time.

Therefore the invariant protects the timescales, in both directions:

* Drive weights respond to urgencies only through the uniform lagged update law. No code path may bypass the lag.
* Reversion time constants are declared parameters, set at initialization or evolving only through the declared accumulation dynamics. No code path may read, speed up, slow down, or override a time constant based on circumstance, agent identity, or commitment level.
* An instant survival override (`if threatened: weight = max`) violates the invariant exactly as much as scripted martyrdom does.
* Time constants are swept axes of the phase diagram, never constants tuned to a value chosen because sacrifice happens there.
* Action selection is myopic argmax over the current lagged drive state. It never anticipates its own reversion. All mechanism lives in the drive-update law.
* Commitment, when introduced, is an instance of the same drive class as every base drive, distinguished only by its accumulation dynamics. It is not a new mechanism.
* Tuning parameters to suppress inversion where it inconveniently appears is the same sin as tuning to produce it. Null regions are findings and get golden tests too.

## Hard rules

### Golden runs

Behavioural regression is caught by hashed golden runs in `tests/golden/`.

Never update a golden hash to make a test pass. A changed hash means the dynamics changed. That requires human sign-off and a documented justification in the commit body. If a golden test fails, report it and stop.

Golden hashes are computed over arrays rounded to 8 decimal places, not raw float bytes, so they survive BLAS and platform variation. The environment is pinned by the lockfile.

### Determinism

* One RNG, owned by the model, passed explicitly. Never import or call global `random` or `np.random` module-level functions.
* Per-agent RNG streams derived from the master seed via `np.random.SeedSequence(master).spawn(n)`, so adding an agent does not shift another agent's draws.
* Never iterate over a `set`, or over a `dict` whose insertion order is not itself deterministic, anywhere that affects simulation state.
* Action order is part of the model definition and is frozen: `argmax` ties resolve by index, so reordering actions changes behaviour at exactly the boundaries the phase diagram cares about.
* Parallelism across runs only. Never within a run's state updates.
* Every run writes `manifest.json`: seed, config hash, git SHA, package versions, timestamp.

### State layout

Agent state lives in structure-of-arrays (`numpy`), not object-per-agent. Agent logic is written as readable functions over array slices. This is not premature optimisation: Phase 5 requires thousands of runs at 10k+ agents, and object-per-agent makes that infeasible. Do not refactor to OOP agents.

Drive state is mutated only in `core/drives.py`. No other file writes to weights, urgencies, or time constants. This chokepoint is what makes the static analysis in `tests/test_invariants.py` sound.

### Specs

No implementation without a spec in `specs/phase-N.md` containing acceptance criteria. If asked to build something with no spec, write the spec first and request review before implementing.

### Phase gates

Do not begin phase N+1 until phase N's validation artifact exists, is committed under `results/`, and its acceptance criteria are met.

## Working style

* One phase-slice per session. State the acceptance criteria you are targeting at the start.
* Write invariant tests before the mechanism they constrain.
* End each session by updating `specs/phase-N.md` to match what was actually built, including deviations.
* Prefer boring, explicit, inspectable code. The core model is ~300-500 lines and will be read line by line by a human. Cleverness in the model kernel is a defect.
* Vectorised code must carry a comment stating the equivalent per-agent operation in plain language.
* Every message that improves the agent opens with three sentences, in plain mechanical terms, on how the change moves the agent closer to humanity. After the work, report precisely and directly what was done, as raw material for the project logbook.

## Never do

* Silently change a model parameter to make a result look better.
* Report a result without the seed and config hash that produced it.
* Describe an unvalidated output as a finding.
* Add a dependency without recording it in the lockfile.
* "Fix" a failing scientific test by adjusting the test.
