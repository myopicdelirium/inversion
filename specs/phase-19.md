# Phase 19: wonder

Pre-registered 2026-07-27, spec written with the mechanism staged but
before any run, any golden refresh, or any outcome data. This is a
constitutional event: Amendment 6, the first change to DRIVE_NAMES
since phase 2. The agent gains a fifth drive, wonder, the first want
about the inner map rather than the body.

## The mechanism, declared

* **The urgency is staleness**: ticks since a genuinely new place
  entered the memory of places (an insertion, not a refresh), over
  wonder_horizon 400, clipped to [0, 1]. Computed in core/memory.py,
  which owns the novelty clock (mem_last_novel, written nowhere
  else), and handed to core/drives.py as a percept exactly like
  testimony. Only drives.py writes the urgency. The one law gains a
  row, never a clause: tau_wonder 45 enters init_timescales beside
  the other four constants.
* **Relief is wandering**: the pricing tables value WANDER for wonder
  at wonder_relief 0.01 per tick (myopic) and wonder_relief times the
  agent's own horizon (farsighted). No new action exists: the fifth
  drive re-prices an old one.
* **Structural inertness**: in any world without sight and memory,
  nothing is ever novel, staleness is never computed, the urgency
  stays zero, and the weight stays zero forever. Every pre-amendment
  finding keeps its meaning. This is not a flag: it is a consequence
  of wonder's definition, and N1b tests it as a consequence, with
  wonder_relief cranked high in an omniscient world and the
  trajectory required to stay bit-identical.
* **The shape event**: weights, urgency, and tau arrays widen to five
  columns, so the FULL golden hashes change for every stored golden
  while the six behavioral arrays (x, y, energy, integrity, fatigue,
  alive) must stay bit-identical. This is the phase 2 precedent: the
  refresh is legal only with the behavioral proof attached, and the
  commit body must say exactly this.

## Registrations, before running

* **N1a, behavioral preservation, kill switch**: every stored golden
  replays with all six behavioral arrays bit-identical; weights and
  urgency hashes refreshed with the shape-change justification;
  suite green.
* **N1b, inertness as consequence, kill switch**: an omniscient
  default world with wonder_relief 1.0 runs bit-identical to the same
  world at wonder_relief 0.0. If pricing leaks into a world where
  novelty cannot exist, the amendment is broken and the phase stops.
* **N2, wonder must move behavior, falsifiable**: sighted world
  (r_sight 12, slots 8, default food), seeds 1-24: lifetime distinct
  places remembered per agent (cumulative insertions) is at least 25
  percent higher with wonder on (relief 0.01) than off (relief 0).
  If the drive prices wandering and nobody wanders more, the relief
  constant is dead and that is reported.
* **N3, curiosity's price, no desired direction**: the same sighted
  world with default hazards restored: mortality and starvation with
  wonder on versus off, both stages, reported with sign. Whether
  curiosity kills, protects (dispersal finds food), or does nothing
  is the model's answer, not ours.
* Fresh seeds 31-54 replication for N2 and N3 before packaging.
  Design checks on seeds 96-99 only, peeks recorded.

## Honesty notes

Wonder names no destination and no danger: the drive knows only that
nothing has been new lately. Any storm-entry excess among the bored,
if it ever appears, must emerge from pricing wander in a world whose
novelty happens to live near the rim, never from a rule. The
inversion pathway this opens (leaving safety because the known world
stopped being enough) is a hypothesis for a FUTURE registered
protocol, not this one; N2 and N3 only establish that the drive is
alive and what it costs.

## Deviations

* **N1a's first run failed, and the failure was a design error worth
  its line**: wonder shipped default-on (relief 0.01 with no off
  switch), so the sighted phase 17 golden legitimately changed
  behavior while all nineteen memoryless goldens stayed bit-identical.
  That violated the corpus's inert-by-default convention (every
  capability since care has entered switched off). Fixed before any
  outcome data: wonder_horizon 0 default means no staleness percept
  exists anywhere until a world declares one; the stored golden
  configs are migrated in this one refresh by dropping the wonder
  keys so the new defaults apply, recorded here. The ritual was then
  rerun from scratch.
* **Pre-review mutation audit, recorded**: three hand mutations run
  before the review panel: dead wonder urgency (RED, two tests), dead
  novelty clock (RED), dead myopic pricing row (GREEN on first try,
  the phase 18 disease caught in-house this time: the load-bearing
  switch compared full hashes, which the drive's bookkeeping arrays
  change even when its pricing is dead). The switch was rewritten to
  demand BEHAVIORAL divergence at cranked relief, and the retried
  mutation goes red. All three now bite.
* **Adversarial review, 2026-07-28, four findings confirmed, all
  fixed before commit, worktree isolation held (ten agents, zero
  main-tree writes).** (1) Major, the finding that mattered:
  FAMILIARITY WAS COUNTED AS DISCOVERY. The novelty clock reset on
  any insertion, so re-learning a calendar-forgotten place cured
  saturated boredom, an agent shuttling among more familiar sites
  than it has slots was never bored, and 58.8 percent of "novel"
  insertions in a default sighted world were the agent's own past
  places against a 10.6 percent coincidence baseline. Fixed with the
  lifetime visited grid: the world is cut into eating-diameter cells,
  an insertion resets wonder's clock only in a cell the agent has
  never known, and both mutation replays (clock dead; every insertion
  novel again) go red. N2's metric wording amends accordingly, before
  any declared run: discoveries mean genuine new-cell events. (2 and
  3) Major pair: the five-drive layout silently broke two legacy
  validation scripts, a hardcoded four-column buffer in the phase 15
  attention instrument and a KeyError plus 0/0 tau regression on the
  inert drive in the phase 2 identity check; both fixed, with the
  inert drive residual-checked and reported as inert rather than
  regressed. (4) Minor, documented as semantics rather than changed:
  the clock is birth-anchored, so a life that never finds anything
  grows stale against the calendar of its birth. Born fresh, bored by
  a world that gives nothing: adopted reading, now in the spec.
* **Design peek, seed 97, recorded**: under lifetime novelty at
  default relief 0.01, wonder-on and wonder-off discoveries tied
  (4475 vs 4483 over 1500 ticks, n 60). N2 runs as declared; if the
  relief constant is too quiet to clear the 1.25x bar, that failure
  is the phase's honest result.
