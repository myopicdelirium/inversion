# Phase 22: the told place

Pre-registered 2026-07-29, spec before mechanisms. Amendment 8:
socially settable knowledge, the first stone of the Xhosa-critical
road. A rumor of food enters a listener's private world on a
teller's credence, carries its teller's name, and is settled later
by the listener's own feet.

## The mechanism, declared

* **What may be told**: each tick, for each listener with a free or
  stale slot, the best candidate is the freshest remembered site
  among neighbors within r_social whose credence in the listener's
  ledger is at least tell_threshold 0.5, restricted to sites the
  listener does not already hold (nothing within r_eat of an
  existing slot). One telling per listener per tick, the freshest
  wins, ties by lowest teller index: deterministic, no RNG.
  Computed in social.py (it owns credence and neighborhoods),
  returned as a percept; memory.py applies the insertion (it owns
  the slots). The told slot records teller identity (mem_source) and
  the TELLER'S last-seen tick as its freshness: secondhand news ages
  from when the teller saw it, not from when it was repeated.
* **Provenance and settlement**: mem_told marks secondhand slots;
  mem_source names the teller. Refined pre-run, before any code ran:
  settlement TRUE is by SIGHT, the existing match branch, when the
  listener's own eyes find food at the told place (one credence-law
  step with score 1 toward the teller, slot converts to owned).
  Told-slot disappointment (the site seen empty) scores the teller 0
  through the same law; calendar expiry unvisited settles nothing.
  Settlement events are computed in memory.py and applied to
  credence in social.py: each organ writes only its own state,
  values flow between.
* **Told places do not reset wonder's clock**: hearing is not
  discovery; only feet and eyes are (Amendment 7 semantics
  preserved). The visited grid is untouched by telling.
* **Inertness**: tell_places False default; the intake requires the
  social organ (r_social > 0), sight and memory (r_sight > 0,
  slots > 0). Off is bit-inert by flag AND structurally absent
  without the prerequisite organs.
* **Chokepoint refinement, recorded pre-run, cleaner than first
  drafted**: memory.py never sees credence at all. social.py
  computes a boolean eligibility mask (in social range AND credence
  at least tell_threshold) and hands it over as a value; memory.py
  does freshness selection and insertion against its own slots;
  settlement events flow back and social.py applies them through the
  law as its second credence write site, sole-writer rule intact and
  the blind-to-the-mind scan unamended.

## Registrations, before running

* **B1, inertness ritual, kill switch**: all goldens replay
  behaviorally bit-identical with tell_places False and with it True
  in worlds lacking any prerequisite organ; configs refreshed; suite
  green.
* **B2, rumors nourish, falsifiable**: sighted famine world (n_food
  60, r_sight 12, slots 8, r_social 8, testimony 0) with telling on,
  seeds 1-24: at least 500 pooled told-site settlements TRUE (meals
  eaten at places known only by word of mouth), and starvation at
  least 3 points lower than the telling-off arm. If hearsay feeds
  nobody, the channel is dead and that is reported.
* **B3, secondhand news ages worse, falsifiable**: told slots
  disappoint at a rate at least 1.5x owned slots' disappointment
  rate, pooled (secondhand freshness plus travel lag must show up as
  error, or the provenance machinery is suspect).
* **B4, gossip builds reputation, falsifiable**: pooled across
  listeners, mean credence toward tellers whose tellings settled
  TRUE for that listener at least 0.15 above mean credence toward
  tellers whose tellings disappointed. The feedback loop must
  separate the reliable from the stale-voiced within lived
  experience, or the settlement wiring is dead.
* Fresh seeds 31-54 replication for B2-B4 before packaging. Design
  checks on seeds 96-99 only, peeks recorded.

## Honesty notes

Nothing here can lie: every false rumor is honest staleness relayed
in good faith, so phase 22 establishes the CHANNEL, not deception.
The Xhosa-shaped question, whether a society can starve on a story,
needs this channel plus a belief that commands sacrifice, which is a
later registration; B2-B4 only prove the word carries, errs, and is
priced. The one-body, mortal-knee, and worlds-not-minds findings all
warn against expecting individual variation to dominate: the channel
claims here are population-level.

## Deviations

* **The review panel stalled and is NOT booked as a pass**: all three
  finder agents stalled on every attempt and returned nothing, so the
  workflow's empty findings list means zero coverage, not a clean
  bill. Recorded honestly. In its place, the three named risks were
  probed in-house with concrete harnesses, results below, and the
  B1 ritual already constitutes the inertness-versus-prior-code
  proof (the stored golden hashes it replayed bit-identically were
  produced by the pre-diff code).
* **In-house probe, rumor-of-rumor, clean, semantics adopted**:
  told slots may be re-told. Freshness propagates from the ORIGINAL
  sighting tick however many mouths the rumor passes, so secondhand
  news ages truthfully along chains; accountability bills the
  immediate teller. You vouch for what you repeat: adopted reading,
  now in the spec.
* **In-house probe, stale billing, clean**: a told slot evicted by
  own insertions emits no ghost settlement when the old coordinates
  are later resighted; provenance clears with the slot everywhere
  (eviction, expiry, disappointment, conversion) and events read
  their source in the same expression that clears it.
* **Mutation audit**: dead provenance, dead true-settlement, dead
  feedback law, unwired intake: all four RED. The blind-to-the-mind
  tripwire fired on this phase's own comments for containing the
  ledger's name; the prose was reworded rather than the scan
  weakened.


## Results, recorded 2026-07-29: the tragedy of the told commons

Artifacts: `results/phase-22-told.json` (seeds 1-24),
`phase-22-told-replication.json` (fresh seeds 31-54). Judged exactly
as declared, and two of three registered stories were refused with
inverted signs:

* **B2 FAILED both stages, sign inverted, and the refusal is the
  finding**: the channel fed individuals beyond any doubt, 80,021
  and 65,696 true settlements against a floor of 500, and the
  telling worlds still starved MORE: 0.474 against 0.350, then 0.533
  against 0.375, the rumor network costing 12.4 and 15.9 points of
  survival. Honest, accurate, well-meant word of mouth raised famine
  mortality by a third, replicated.
* **B3 FAILED both stages, sign inverted**: told slots disappointed
  at 0.496 and 0.499 against owned slots' 0.667 and 0.655. Hearsay
  is FRESHER than memory. Post hoc, flagged: what gets told is each
  teller's freshest slot, so transmission curates, while private
  memory carries its whole stale tail. The channel transmits the
  best of every mind and still kills the crowd that listens.
* **B4 PASSED both stages, promoted**: mean credence toward tellers
  whose tips settled true, 0.333 and 0.344, against 0.103 and 0.104
  toward the stale-voiced: gaps 0.230 and 0.240 against the 0.15
  bar, built purely from lived settlements. Gossip prices its
  sources.
* **The post hoc mechanism, flagged, unclaimed, and the next
  registration's target**: synchronization. Rumors concentrate
  foragers onto the same few freshest patches; the patch pays
  whoever arrives first and burns everyone else's travel; ignorant
  populations spread out and harvest the commons asynchronously.
  If that is the mechanism, telling should measurably concentrate
  the population (co-arrival rates, pairwise distances), which is a
  declared follow-up, not run. Whatever the mechanism, the measured
  fact stands at full volume: in this arena, a society of honest
  tellers starves faster than a society of the ignorant, while its
  reputation system works exactly as designed.
* The sentence the phase earns, and the Xhosa road just got darker:
  no false prophecy is needed to starve a society on words. Synchrony
  alone can do it, with every single rumor true.