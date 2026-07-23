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

### Amendment 2 (2026-07-23): heterogeneity is initialization, not circumstance

Amendment 1 forbids reading or modifying a time constant "based on circumstance, agent identity, or commitment level." That sentence was written against scripting, not against individuality. Clarification:

* Per-agent parameters (time constants, attachment depth) may differ across agents only as draws made once at spawn, from population distributions declared in config, using the agent's own stream. After spawn they are immutable for life.
* Everything Amendment 1 forbids stays forbidden: no post-init modification, ever, for any reason. Additionally forbidden: assignment rules that reference anything beyond the declared distribution (no trait by hand-picked agent, no trait by position, no trait by outcome), and distributions chosen to make a specific run produce sacrifice.
* Spread parameters default to zero. At zero, every agent carries the declared value exactly and all prior goldens are bit-identical.
* Enforcement: `tests/test_invariants.py` allows time-constant writes only in `core/config.py` (declaration) and init functions of `core/drives.py` (the one sanctioned draw site), and asserts at runtime that per-agent time constants never change over a run.

### Amendment 3 (2026-07-23): bounded attention, one law, no names

The update law gains an attention factor: each drive's urgency is *heard* in proportion to `(w_d / max_e w_e) ** kappa`, where `kappa` is `attention_sharpness`, declared in config, default 0, at which the factor is exactly 1 and the law is phase 1's bit for bit. Rules:

* **The attention law names no drive.** Static analysis forbids drive-index constants inside `update_weights`. Whatever dominance suppresses, it suppresses uniformly: a starving agent is deaf to danger exactly as a grieving one is deaf to hunger. Any per-drive sharpness, gate, floor, or exemption violates the Prime Invariant.
* `kappa` is declared, never modified at runtime, and swept as a phase-diagram axis like every timescale.
* Attention scales heard urgency only. It may not touch time constants (Amendment 1 stands in full).
* Raw urgencies remain the recorded truth. The heard urgency is reconstructible exactly from recorded weights and urgencies, and the transition identity extends to it: every weight transition must satisfy the attended law to machine precision.
* Forbidden: attention terms conditioned on mortality, threat, damage, or commitment state. Attention reads weights and nothing else.

**Addendum (2026-07-23), the whisper floor.** The heard ratio is clamped below: `heard_d = u_d * max(w_d / max_e w_e, attention_floor) ** kappa`. The floor is declared, default 0, one scalar for all drives (a per-drive floor violates the names-no-drive rule). At floor 0 the law is the zero-trap exactly: a never-felt drive is unhearable forever. That regime is preserved as the boundary of the axis, not deleted; the floor is swept like every other timescale. Phase 9's discovery (peacetime collapse, the seed-identical fear-deaf) lives at floor 0 and must remain reproducible there.

### Amendment 4 (2026-07-23): farsighted in consequences, myopic in values

Amendment 1's myopia clause ("action selection never anticipates its own reversion") protects the timing-failure mechanism. It is now split into what it was protecting and what it accidentally forbade:

* **Still forbidden, permanently**: predicting one's own future weights, urgencies-as-motivations, or reversion. The agent may never reason about what it will want.
* **Now permitted, under declaration**: action values may integrate predicted WORLD consequences over a declared horizon (`prospect_horizon`, default 0 = the phase 1 closed forms, bit for bit). The prediction uses the agent's declared physics: straight-line kinematics, known static fields, no other agents' future actions (agents predict physics, never minds), evaluated entirely under the agent's CURRENT weights, frozen during evaluation.
* No branch on predicted death, anywhere. Predicted harm enters action value only continuously, as integrated exposure along the predicted path. `core/action.py` may not reference integrity at all (static tripwire); the felt price of a path is its accumulated danger, not a death predicate.
* The horizon is declared, never modified at runtime, swept as an axis. Sacrifice under foresight, if it occurs, must remain the ordinary argmax of weight times predicted consequence, with no term that exists to produce it.

### Amendment 5 (2026-07-24): the other in the ledger

Until now no agent's valuation has ever counted another's condition; every price and every relief was self-denominated, and phase 13 proved the consequence: the up-front wager cannot exist in a ledger that contains no stake but one's own. This amendment permits exactly two additions, both default-zero and bit-inert:

* **The care term.** Bond urgency becomes `u_bond = b * clip(separation + care * peril_of_target, 0, 1)`, where `peril_of_target` is the world's danger field at the living bond target's location: physics seen at a place, never a mind read. `care` is declared in config, default 0, one scalar for all agents (spread as a later axis). A dead or absent target has no location and contributes zero: care needs a living beloved; grief remains pure separation, unchanged.
* **Assistance physics.** An agent within a declared radius of its gripped partner lends them speed: the partner's effective snare is scaled by `1 - help_strength`. World physics, symmetric, in `core/world.py`, never reading drive state (the standing chokepoint applies).
* The existing tripwires already fence this amendment and are reaffirmed: the update law still names no drive; `core/action.py` still may not reference integrity, so any priced expectation of helping is denominated in peril (danger), never in the target's health or death; no branch on any agent's mortality state anywhere in drives or action code.
* Forbidden: care terms conditioned on who the target is, on the target's mortality state discretely, or on outcomes; assistance that reads bond or weight state; any coefficient modified at runtime.

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
