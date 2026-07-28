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
