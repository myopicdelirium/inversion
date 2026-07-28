# Phase 21: the quest

Pre-registered 2026-07-28, spec before mechanisms. Amendment 7: the
capability gap phase 20 named, built and tested. Seeking the unknown
becomes an action; novelty becomes occupancy; and the pull-of-
elsewhere protocol re-registers on the new organ with the same
question and honest new bars.

## The mechanism, declared

* **Novelty is occupancy**: the lifetime visited grid (Amendment 6)
  upgrades from food-sighting to presence. Each tick, every living
  agent's own cell is marked known; insertions still mark as before
  (subsumed). Wonder's clock resets on first knowings only. This is
  a semantics upgrade to an existing organ: phase 19's N2/N3 results
  remain statements about the food-sighting semantics, pinned to
  their commit, and the honesty note below records the difference.
* **SEEK_NOVEL, the sixth action**: moves toward the nearest unknown
  cell (percept computed in memory.py: distance and unit direction
  to the nearest cell center not yet known; infinite when the world
  is fully known). Myopic pricing mirrors food exactly:
  wonder relief distance-discounted, movement burning what movement
  burns. Farsighted pricing mirrors food exactly: travel then held
  relief over the remaining horizon. No other row prices it; the
  action layer never knows why a cell is unknown.
* **The quest replaces serendipity in the table**: wonder's relief is
  per novelty event, and the quest is the reliable path to one, so
  WANDER's wonder row goes to zero in both tables. Wandering may
  still stumble onto novelty in fact; the agent simply no longer
  counts on luck it cannot estimate. Without this, a per-tick wander
  relief strictly dominates any quest with travel time and the sixth
  action is stillborn. Phase 19's N2/N3 stand as statements about
  the superseded pricing, commit-pinned.
* **Structural dominance when idle**: with wonder off or memory
  absent, SEEK_NOVEL pays wandering's costs with no prize and a
  strictly worse energy row than WANDER, so it is never selected:
  inertness by arithmetic, not by flag, tested by mutation and by
  golden replay.
* **Chokepoints**: memory.py alone touches the grid and computes the
  percept; drives.py is untouched this phase; action.py prices what
  it is handed. Tripwires extend the phase 17 and 19 scans to the
  new percept names.

## Registrations, before running

* **Q1, preservation, kill switch**: every wonder-off golden replays
  fully bit-identical (no recorded array changes shape this phase);
  the two wonder-on capability goldens (phase 19 wonder, if touched)
  are refreshed with the semantics-upgrade justification only after
  their wonder-off siblings prove bit-identity. Full suite green.
* **Q2, the quest exists, falsifiable**: in the phase 20 closure's
  best-powered arena (bond 0.6, horizon 100, relief 0.1, the mire on
  nest 0), wonder-ruled non-local crossings (energy above 0.7 and
  wonder the maximum weight at the crossing tick) number at least 50
  pooled on seeds 1-24 with directed exploration, against the
  recorded zero-at-every-coordinate of the undirected design checks.
  Mortality of those pilgrims inside the window is reported without
  bar: any deaths are the corpus's first inversions by staleness.
* **Q3, the Prime Invariant guard, kill switch**: entry rate of the
  bottom onset-staleness tercile in the directed arm stays within
  1.5x of the wonder-off arm. If the mechanism drags in the un-bored,
  the excess is machinery and not longing, and the phase stops.
* **Q4, dose and diffusion, reported without bar**: overall non-local
  entry rates for off, directed-quiet (relief 0.01), and directed-loud
  (relief 0.1) arms, both stages, for the record and the figure.
  Amendment before any run: the first wording promised an
  undirected-loud arm, which no longer exists in the code because the
  quest superseded priced serendipity; the undirected numbers live in
  phase 20's closure record and are cited, not rerun.
* Fresh seeds 31-54 replication for Q2 and Q3 before packaging.
  Design checks on seeds 96-99 only, peeks recorded.

## Honesty notes

Phase 19's discovery counts (N2) and survival gaps (N3) were measured
under food-sighting novelty and are not restated under occupancy
semantics; any future comparison re-runs them under registration. The
Q2 bar of 50 reuses phase 20's registered magnitude so the directed
mechanism is judged against the exact bar the undirected one could
not reach. If Q2 fails even with a real quest action, then staleness
cannot rule at the threshold in this architecture at any tested
coordinate, and the reserved question closes with a null at full
volume rather than staying open indefinitely.

## Results, recorded 2026-07-28: the guard fired, the phase stops rather than claims

Artifacts: `results/phase-21-quest.json` (seeds 1-24),
`phase-21-quest-replication.json` (fresh seeds 31-54). Judged exactly
as declared, in the declared order of authority:

* **Q3 FAILED, both stages, and it is the kill switch**: the bottom
  onset-staleness tercile entered at 0.705 and 0.699 against an
  off-arm rate of 0.441 and 0.440, ratio 1.6 against the declared
  1.5 bar, and above the loud arm's own average of 0.685. By the
  registration's words: the excess is machinery and not longing, and
  the phase stops rather than claims.
* **Q2 passed its bar and is NOT promoted**: 1176 and 1320 pooled
  wonder-ruled non-local crossings (bar 50; off arm exactly 0 both
  stages), pilgrim mortality 0.469 and 0.472. These numbers are
  reported because they were measured and are withheld from the
  findings ledger because their guard failed. 2496 apparent pilgrims
  and 1175 apparent inversions by staleness sit in the artifacts,
  unclaimed, until a guard they survive exists.
* **Q4, the dose ladder**: off 0.441/0.440, quiet 0.469/0.443, loud
  0.685/0.688.
* **Post hoc, flagged, the confound the guard exposed in itself**:
  under continuous questing, staleness at one instant is a bad proxy
  for boredom as a disposition, because the most exploration-active
  agents keep resetting their own clocks and therefore look calm at
  onset while standing at the frontier. Low staleness conflates the
  never-bored homebody with the just-satisfied quester. The declared
  follow-up, not run: re-register the guard on integrated pre-onset
  staleness (the time-average over the settling epoch), a
  disposition measure the quest cannot zero out, with the same 1.5x
  bar and Q2 re-judged only if that guard holds.
* The sentence the phase earns: the corpus's most wanted number
  arrived at fifty times its bar, twice, and the ledger's own
  machinery refused it. That refusal is worth more to the program
  than the claim would have been.

## Deviations

* **Pre-review mutation audit, recorded**: dead myopic quest pricing
  RED (two tests), dead occupancy RED, percept-blind-to-known-cells
  RED. The superseded wander-serendipity pricing test was replaced by
  the deterministic quest-pricing switch, with the supersession noted
  in the test body. Q1's first clause proved itself in passing: all
  twenty wonder-off goldens replayed fully bit-identical with no
  refresh (this phase changes no recorded array shapes); only the
  wonder-on capability golden was refreshed, under the occupancy and
  pricing semantics change, justification in its description and
  here. Two harness tests were updated because their agents
  teleported into never-known cells, which under occupancy semantics
  IS discovery, correctly.
* **Adversarial review, 2026-07-28, three defects confirmed and
  fixed pre-commit, two explicit no-defect verifications, zero
  main-tree writes (nine agents, isolated worktrees).** (1) Major:
  phantom cell centers. At world sizes that do not divide by the
  cell edge, the truncated last cell's nominal center (i+0.5)*cell
  could wrap across the torus into cell 0's territory: a target zero
  travel away that standing on could never extinguish, with the
  myopic price maximized at travel 0. Latent (every current config
  divides evenly), real (the code claims non-multiple support).
  Centers are now true midpoints of possibly-truncated cells;
  regression pinned at world 13, r_eat 3. (2) Major: the farsighted
  quest energy row charged movement for the whole horizon as if the
  quester never arrives, the phase 11 arrival-cap lesson recurring
  in a new row; now mirrors SEEK_FOOD's arrival-capped cost exactly.
  (3) Minor: the percept lacked an alive gate in the chokepoint
  file, inert today behind world.py's movement gate; the dead now
  quest nowhere (infinite distance, zero direction). Verified
  no-defect, for the record: the flat-index arithmetic agrees
  exactly with the occupancy grid's cell convention (no
  transposition), and the occupancy and insertion paths are properly
  alive-gated. The dominance finder returned zero findings: the
  strict-dominance argument for wonder-off worlds held under attack,
  including degenerate states.


## Addendum, pre-registered 2026-07-29 before running: the second guard

The first guard's proxy failed its own purpose: instantaneous
staleness cannot distinguish the never-bored from the just-satisfied
quester, because active explorers reset their own clocks. The honest
disposition measure already exists in the organ: w_wonder at onset,
the tau-discounted integral of lived staleness, the pressure the
drive actually exerts. And one proxy swap is not enough to close the
question, so this addendum also registers the surgical arm the first
design lacked. Declared before running:

* **G1, the guard, re-registered on the organ's own integral**: in
  the loud arm, the entry rate of the bottom tercile of w_wonder at
  onset stays within 1.5x of the off-arm rate. Same bar as Q3, new
  proxy, nothing else moved. Q2's 2496 unclaimed pilgrims are
  re-judged if and only if G1 holds.
* **G2, the gradient, reported without bar**: entry rate by
  w_wonder-at-onset tercile, both stages. Longing should grade;
  machinery should not.
* **G3, the geometry confound made visible, reported without bar**:
  median distance to the storm rim at onset, per tercile. If the
  low-pressure tercile simply starts nearer the frontier, the
  confound is exposed and quantified rather than argued about.
* **G4, the amputation arm, falsifiable**: a fourth arm identical to
  loud until the tick of onset, at which point wonder's pricing is
  amputated (relief set to zero by the instrument; histories, weights,
  and positions untouched; no RNG consumed by the cut). If the loud
  arm's entry excess over off survives amputation, it was accumulated
  geometry, not live longing; if it collapses, the pull was the drive
  itself, alive at the moment of choosing. Bar: amputation must
  remove at least half of the loud-minus-off entry excess for the
  pull to be judged live. G4 informs interpretation either way and
  does not gate Q2; only G1 gates Q2.
* Seeds 1-24 declared, fresh seeds 31-54 replication before
  packaging. The off and loud arms are byte-identical reruns of the
  phase 21 protocol cells (config hashes verified against stored
  rows before launch); only the measurement and the fourth arm are
  new.

## Second-guard results, recorded 2026-07-29: the pull is real, the pilgrim remains unclaimed

Artifacts: `results/phase-21-guard.json` (seeds 1-24),
`phase-21-guard-replication.json` (fresh seeds 31-54). Config hashes
of the off and loud arms verified against the stored phase 21 rows
before launch. Judged exactly as declared:

* **G1 SPLIT AND THEREFORE FAILED**: low-pressure-tercile entry 0.6612
  against a bar of 1.5 x 0.4413 = 0.6620 on the declared seeds, a
  pass by eight ten-thousandths, then 0.6844 against 0.6602 on fresh
  seeds, a failure. The corpus's own precedent governs (the refused
  G2 pass of the grief-geometry phase): a razor pass that fails
  replication gates nothing. Q2's pilgrims, now 2496 measured twice,
  REMAIN UNCLAIMED.
* **G4 PASSED, replicated, and it is the finding**: amputating
  wonder's pricing at the tick of onset, histories and weights and
  positions untouched, removed 121 and 118 percent of the loud-over-
  off entry excess: the amputated arm (0.3895, 0.3968) fell BELOW the
  off arm (0.4413, 0.4401). The pull of elsewhere is entirely live
  longing at the moment of choosing, zero accumulated geometry. This
  is promotable and promoted: LIVE WONDER PRICING CAUSES THE ENTRY
  EXCESS, at about 24 points of entry rate, established by surgical
  removal, both seed stages.
* **G3, no confound**: median rim distance at onset is flat across
  disposition terciles (24.7/26.1/25.7 and 24.1/26.2/24.9): the
  low-pressure agents do NOT start nearer the frontier. The phase 20
  geometry suspicion is refuted by measurement.
* **G2, the explanation of the guard's own failures**: the entry
  gradient across disposition terciles is nearly flat (0.661/0.677/
  0.718 and 0.684/0.685/0.693). At horizon 100 in this arena,
  boredom is ambient: staleness cycles fast enough that even the
  bottom tercile carries operative pressure, so no subpopulation can
  play the innocent control. The guard is not failing because the
  drive is fake (G4 proves it live); it fails because this world
  contains no genuinely un-bored agents to protect.
* **Post hoc, flagged, unclaimed**: the amputation UNDERSHOOT
  (removed more than 100 percent): agents with questing histories
  and dead pricing entered LESS than never-wondering agents. The
  traveled are harder to lure; candidate mechanisms (their maps
  already contain the storm sector; their food memories pull
  elsewhere) are for a future registration.
* **Declared follow-up, the third guard, a different population
  rather than a different bar**: the trait-panel machinery (phase
  18) makes wonder_horizon personal; a spread population contains
  genuinely un-bored agents by construction. The guard re-registers
  there, same 1.5x bar, and the pilgrims are re-judged only if it
  holds. Every guard iteration has moved the design and never the
  bar, and this entry records the same promise for the third.

The standing sentence: the pull of elsewhere is now a established
causal force in this architecture, and the individual pilgrim stays
in the artifacts, twice measured, twice refused, awaiting a world
that contains anyone who could have stayed home.