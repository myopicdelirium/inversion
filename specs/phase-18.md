# Phase 18: the shapes of minds

Pre-registered 2026-07-27, spec before mechanisms. The corpus so far
treats attention sharpness (kappa) and foresight depth (the prospect
horizon) as properties of worlds: every finding of the form "at kappa
2 the bereaved starve" or "foresight abolishes inversion" compares
one uniform society against another. Humans do not live in uniform
societies. This phase makes both quantities personal traits, drawn
once at birth and immutable forever (Amendment 2: heterogeneity is
initialization), so that one population contains sharp and diffuse
attention, long and short sight, and the storms sort them.

## The mechanism, declared

* **Personal sharpness**: arrays.kappa, one exponent per agent,
  filled with attention_sharpness at spawn; when attention_spread is
  positive, kappa_i = attention_sharpness times exp(spread times z),
  z standard normal from the agent's own stream, consumed only when
  the knob is on. The one law's FORM does not change: heard is still
  u times gate to the kappa, only the exponent is now the agent's
  own. drives.py remains the only writer of drive state; kappa is
  written once, at spawn, in model init, and never again (tripwired
  like tau).
* **Personal horizon**: arrays.horizon, one depth per agent, filled
  with prospect_horizon at spawn; when prospect_spread is positive,
  h_i = round(prospect_horizon times exp(spread times z)), clamped to
  at least 1, drawn the same way. Every closed-form rollout in
  action.py prices with the agent's own h_i. Scope limit, declared:
  the farsighted/myopic dispatch stays global this phase (a world
  with prospect_horizon 0 is uniformly myopic, as ever); mixing
  sighted and blind DECISION architectures in one world is a later
  phase, this one mixes depths among the sighted.
* **Chokepoints and tripwires, written before mechanisms**: kappa and
  horizon are written at exactly one site each (spawn); action.py may
  not reference kappa (attention is hearing, not pricing); drives.py
  may not reference horizon (wanting does not see ahead); the
  timescale-immutability test pattern extends to both new traits.
* Zero-spread worlds must be bit-identical to the scalar code they
  replace: the exponent and horizon arrays carry the same values the
  scalars did, through the same ufuncs.

## Registrations, before running

* **T1, inertness ritual, kill switch**: with both spreads 0, every
  stored golden replays behaviorally bit-identical, configs
  refreshed; full suite green. This covers worlds where kappa and
  horizon are nonzero scalars today, which the goldens do (phase 7
  attention, phase 11 foresight, phase 13 threshold among them).
* **T2, grief sorts on attention style, falsifiable**: the origin
  arena (the phase 7 grief coordinates: partner mode, kappa median
  2.0, floor 0) with attention_spread 0.5. Within single populations,
  pooling bereaved agents across seeds 1-24: Spearman rho between an
  agent's own kappa_i and starving after loss is at least +0.3. The
  existing corpus says sharp WORLDS kill mourners; this claims sharp
  MINDS die in a mixed world while diffuse minds beside them survive.
  If the correlation fails, grief mortality is a property of worlds
  and not of minds, and that refutation is reported at full volume.
* **T3, the storm sorts on foresight, falsifiable**: the phase 11
  mire coordinates with prospect_spread 0.5 at median 60. Pooling
  agents alive at onset across seeds 1-24: Spearman rho between own
  h_i and dying in the storm window is at most -0.3 (the
  longer-sighted die less). Same refutation clause: if foresight
  only protects as a world property, not an individual one, say so.
* **T4, composition, reported without bar**: mortality of the mixed
  world versus the uniform world at matched medians, both arenas.
  The phase 5 and V4 lessons stand: magnitude bars on society-level
  gaps have gone 1 for 2, so this is measurement, not a claim.
* Fresh seeds 31-54 replication for T2 and T3 before packaging.
  Design checks on seeds 96-99 only, peeks recorded.

## Honesty notes

Trait values enter through the same lognormal convention as every
existing spread. Bereavement and window definitions reuse the
phase 15 measurement code paths. Nothing in this phase adds a drive,
a decision rule, or a social channel: it only lets minds differ in
two dimensions they already possessed.

## Deviations

* **Adversarial review, 2026-07-27, four findings confirmed, all
  fixed before commit.** (1) Blocker, the phase 16 disease again:
  reverting the personal kappa to the config scalar passed the whole
  suite, so the trait was decorative to the tests. New kill switches
  drive the organs directly (per-row law exactness, machine exact)
  and use the flatten trick: two models on identical RNG streams, one
  with its trait array overwritten post-spawn, must diverge. Both
  mutations now turn tests red, verified. (2) Major: at extreme
  personal horizons a toward-danger path overflowed factor**steps in
  the geometric closed forms and poisoned the value table with nan
  via 0 times inf, and argmax picks nan, so the longest-sighted agent
  in the tail would walk INTO danger. Unreachable at the registered
  T3 coordinates (needs z near 9), roughly 1 in 10 hundred-agent runs
  at spread 1.5. Clamped to the largest finite penalty past overflow,
  bit-identical below it; regression test pinned. (3) The reviewer's
  tick-60 trait rewrite (mutation 3c) passed every trait test: the
  runtime immutability check stopped at tick 50 and the write-site
  scan exempted model.py wholesale. The scan now permits trait writes
  only inside Model.__init__ by AST span, and the 3c replay goes red.
  (4) Process incident, recorded in full: the review's mutation
  auditor runs concurrently with other reviewers in the shared
  working tree, which produced transient phantom test failures for
  the other agents mid-review and once left mutation 3c sitting in
  core/model.py after the workflow ended. The tree was restored by
  hand, verified against the intended diff, and the inertness ritual
  was re-executed on the quiesced tree as the review made mandatory
  (all 19 goldens bit-inert). Standing lesson, adopted: mutation
  audits get an isolated worktree next time; one writer per
  repository is the incident-doc rule and reviews are not exempt.
