# Phase 17: the world you know

Pre-registered 2026-07-27, spec before mechanisms. This phase ends the
agent's omniscience. Today every agent knows the nearest active food in
the entire world the moment it exists; that is an oracle, not a
creature. After this phase an agent sees only within its own sight
radius, remembers only the places it has actually seen, forgets them as
they go stale, and discovers their emptiness by walking there. Two
agents standing side by side live in different worlds, each the size of
one biography. This is the keystone of individual richness: every later
capability, rumor of food, the friend who knows a better valley, the
elder who remembers the old famine, requires a private, partial,
sometimes wrong world-model to exist first.

## The mechanism, declared

* **Sight**: r_sight 0.0 default means unlimited, the shipped
  omniscience, bit-inert. When positive, perceive_food returns the
  nearest ACTIVE food within the agent's own radius; nothing beyond it
  exists for that agent. Personal radii come from r_sight_spread,
  lognormal around the declared median, drawn once at birth
  (Amendment 2), consumed only when the spread knob is nonzero so
  draw-count discipline is preserved.
* **Memory of places**: per agent, memory_slots 8 remembered food
  sites, each a position and a last-seen tick. Seeing food refreshes
  or inserts (evict the stalest, deterministic). Memory expires after
  memory_horizon 600 ticks. Arriving within r_eat of a remembered site
  and finding no active food there clears the slot: disappointment is
  how forgetting gets ahead of the calendar.
* **Seeking**: the food target is the nearest visible active food if
  any, else the freshest unexpired remembered site, else nothing and
  the agent wanders. The action layer prices the target's distance
  exactly as it prices dist_food today; farsight rolls the remembered
  destination forward the same way. No new decision rule: ignorance
  changes what the agent knows, never how it wants.
* **Scope limit, declared**: danger stays perceptual this phase.
  Danger is loud and near by nature; places are what memory is for.
  Danger memory, and rumor of places through the phase 16 credence
  organ, are later phases.
* **Chokepoints**: memory lives in its own arrays and is written in
  exactly one new function; drives.py and the action layer stay blind
  to memory internals, seeing only the composite food percept. A
  tripwire enforces that action.py never references memory. No new
  RNG anywhere in the perception or memory path.

## Registrations, before running

* **V1, inertness ritual, kill switch**: r_sight 0.0 replays every
  stored golden behaviorally bit-identical; configs refreshed with the
  new axes; full suite green.
* **V2, the private world exists, manipulation check**: at r_sight 12,
  memory_slots 8, by tick 2000 in the default world, the mean fraction
  of active food sites an agent knows (visible now or remembered
  unexpired) is below 0.2, and the mean pairwise Jaccard overlap of
  remembered site sets is below 0.3. If agents still effectively share
  one world, the phase has not done its job and stops here.
* **V3, memory must earn its existence, falsifiable**: starvation rate
  is monotone worsening across r_sight {0 omniscient, 24, 12, 6} with
  memory off, and at r_sight 12 turning memory on (slots 8 vs 0) cuts
  the starvation rate by at least 25 percent relative. If memory buys
  nothing back, that is reported and the slot machinery is suspect.
* **V4, depth shapes the aggregate, the founding sentence made
  measurable**: with r_sight_spread 0.5 at matched median 12,
  individual lifetime intake correlates with the agent's own r_sight
  (Spearman rho at least 0.3), and the population famine outcome
  (n_food 60 arena, starvation rate by tick 3000) differs between the
  spread and no-spread worlds by at least 5 points at matched median:
  the same average endowment, distributed unequally, is a different
  society. No desired direction on the sign of that difference.
* Seeds 1-24 declared for all of V2-V4, fresh seeds 31-54 replication
  before packaging. All design checks on seeds 96-99 only, every peek
  recorded.

## Honesty notes

The omniscient default remains the arena for every existing golden and
finding; nothing already published changes meaning. Sight and memory
are opt-in axes until a future phase declares a sighted default, which
would be a constitutional event with its own golden refresh.

## Deviations

(recorded as they occur)
