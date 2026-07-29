# Phase 24: birth

Pre-registered 2026-07-29, spec before mechanisms. Amendment 10: the
population becomes self-sustaining, and selection stops being a
metaphor. The corpus's composition findings (phase 4 and 5: the dead
were deeper-bonded and, under gradual arrival, faster-clocked) were
one-generation autopsies; this phase lets the autopsy write the next
generation.

## The mechanism, declared

* **Birth**: each tick, alive agents with energy at least
  birth_threshold are parents-in-waiting; dead slots are cradles.
  Lowest-index parent fills lowest-index cradle, one child per parent
  per tick, until either runs out. The parent pays birth_cost from
  its energy; the child starts with exactly that energy, full
  integrity, zero fatigue, at the parent's position, with the
  parent's home.
* **Inheritance**: the child's tau row, kappa, horizon, wonder_span,
  and r_sight are the parent's, each multiplied by
  exp(birth_mutation times z), z standard normal from the SLOT'S
  dedicated birth stream (one per slot, spawned at init, consumed
  only on rebirth: behavior-dependent consumption of a dedicated
  stream replays exactly and touches no other stream). Horizon and
  wonder_span keep their floors (1); r_sight keeps the r_eat
  validity rule by clamping above it.
* **The fresh mind**: weights and urgencies zeroed, bond zero,
  partner none, memory slots and visited grid and novelty clock
  reset, no faith and no spent faith, credence to and from the slot
  reset to cred_init. The child owns nothing of its parent's world
  but the traits and the birthplace.
* **Write-site amendment, recorded**: the trait tripwire's
  sanctioned writers become state.py (allocation), Model.__init__
  (first spawn), and core/birth.py (rebirth), AST-enforced as ever.
* **Inertness**: birth_threshold 0.0 default means off, bit-inert,
  ritual-tested; birth streams are spawned regardless (draw-count
  discipline: stream creation consumes nothing).

## Registrations, before running

* **G1, inertness ritual, kill switch**: all goldens replay
  behaviorally bit-identical; configs refreshed; suite green.
* **G2, the loop lives, falsifiable**: in the famine arena (n_food
  60, sighted, threshold 0.9, cost 0.4), pooled births at least 500
  across seeds 1-24, and final population at least 20 percent above
  the birthless twin arm (same seeds). A birth mechanism that cannot
  outpace a famine is dead machinery.
* **G3, heritability, manipulation check**: parent-child Spearman
  rho on tau_safety at least 0.8 at birth_mutation 0.1, pooled over
  at least 300 recorded births. The channel must carry the trait.
* **G4, the world breeds its minds, the selection claim,
  falsifiable**: in the hazard-rich sighted world (default hazards,
  n_food 90, threshold 0.9, cost 0.4, tau_safety_spread 0.5, 6000
  ticks), the final living population's mean tau_safety is at least
  10 percent below the initial population's, pooled seeds 1-24: the
  corpus's own composition finding (slow fear dies) made
  generational. Refutation clause at full volume: if the dead do not
  write the children, selection is decorative at these coordinates
  and that is the result.
* Fresh seeds 31-54 replication for G2-G4 before packaging. Design
  checks on seeds 96-99 only, peeks recorded.

## Honesty notes

Slot rebirth means population is capped at n_agents forever: this is
carrying capacity as an artifact of the vessel, declared rather than
modeled. Children are motherless the moment they are born (no bond
to the parent): family, lineage love, and the grief of losing a
child are future amendments, deliberately withheld so this phase
measures inheritance alone. The one-body and worlds-not-minds
findings warn that selection pressure here acts through world-scale
mortality patterns, not individual drama.

## Deviations

* **Pre-commit audit, recorded**: G1 ritual passed (24 goldens
  bit-inert, configs refreshed). Chokepoints preserved rather than
  amended where possible: birth's drive-state and clock writes moved
  INTO drives.py (inherit_drive_state), so the sole-writer rules
  hold with one recorded allowlist addition (the tau scan admits
  inherit_drive_state, a child's clocks written once at ITS birth,
  exactly as the first generation's were). The trait scan admits
  birth.py by Amendment 10's text. Three stale-reference defects of
  the rebirth class were found and fixed in-house before any panel:
  the widow wedded to a stranger's newborn (others' partner pointers
  into the cradle now sever, preserving grief), told slots sourced
  from the former occupant (convert to owned), and believers whose
  mouth the cradle held (faith kept, no one left to bill). Three
  mutations RED: clone children, wedded widows, heirless cradles.
  The live-world switch's arena is hand-cradled and recorded as
  such: 30-agent equilibria refuse to die on their own in 600 ticks.
* **Panel decision, recorded**: a compact two-finder panel runs
  CONCURRENTLY with the protocol rather than before commit, because
  the sharpest risk class (stale cross-references into reborn slots)
  was already swept in-house; any confirmed finding triggers a fix
  commit before any G verdict is judged.


### Protocol run 1, recorded 2026-07-29: the instrument was blind to its subject

G2 reported zero births beside a birth-arm population held at the
full 4800 through a famine that killed a third of the birthless twin
(ratios 1.56 and 1.69 against the 1.2 bar): a contradiction that
diagnoses itself. Births backfill cradles in the SAME step as
deaths, so no between-tick alive snapshot ever shows the vacancy,
and the counter watching alive-flips saw nothing. G2 and G3 are VOID
by instrument blindness, mine, recorded; G4's measurement is real
(mean tau_safety -0.9 and -1.6 percent against the -10 bar) and is
held unjudged until the corrected instrument reruns everything
together. The corrected detector: a birth is a trait change, which
happens nowhere else by the write-site tripwires themselves: the
tripwire architecture doubles as the instrument's ground truth. Same
registration, same bars, corrected eyes.

### Panel results and fixes, recorded 2026-07-29

Ten agents, zero stalls: four clean verifications banked (energy
conservation exact to the float, pairing correct in both mismatch
directions, agent streams untouched by the birth-stream spawn,
ProcessPool replay bit-identical) and four minors. Fixed: the
novelty clock now resets at birth (behaviorally inert, the panel
itself proved the stale value was overwritten before any read, so
the protocol runs stand valid; the contract's letter is honored),
and a validity guard rejects configs where the threshold cannot
cover the cost (registered arenas unaffected). Declared rather than
changed: the child is born mid-stride, facing where its parent
faced, a correlation the wander redraw dissolves within tens of
ticks: adopted semantics, since redrawing the heading would consume
a birth-stream draw and invalidate the completed protocol for a
cosmetic gain. The no-cooldown fountain was confirmed to be exactly
what the spec registered, bounded in practice by energy recovery at
about one birth per two ticks.

## Results, recorded 2026-07-29: the loop lives, the channel carries, the world does not yet breed

Artifacts: `results/phase-24-birth.json` (seeds 1-24),
`phase-24-birth-replication.json` (fresh seeds 31-54), measured by
the corrected instrument (births are trait changes; the first
instrument's blindness is recorded above). Judged as declared, after
the panel, per the sequencing promise:

* **G2 PASSED, replicated**: 1031 and 1079 births against a floor of
  500; birth-arm populations held at the full 4800 through famines
  that cut the birthless twins to 3079 and 2839 (ratios 1.56 and
  1.69 against 1.2). The same-tick backfill that blinded the first
  instrument is the mechanism's signature: cradles refill before any
  snapshot can see the vacancy.
* **G3 PASSED, replicated**: parent-child rho on the fear clock
  0.978 and 0.970 against a bar of 0.8, over 471 and 660 attributed
  births through the exact position-kinship proxy. Inheritance is
  near-perfect transmission under a lognormal blur.
* **G4 FAILED, replicated, and the refutation clause fires at its
  promised volume**: mean tau_safety moved -0.9 and -1.6 percent
  against the demanded -10. At these coordinates selection is
  decorative: ambient drifting hazards at a population held at cap
  kill too few and too indiscriminately to write phase 5's autopsy
  into the generations. Slow fear died under sudden storms; a world
  that breeds quick fear needs recurring sudden mortality with a
  tau-selective signature, a future registration, not run.
* The capability roadmap completes with this phase: the corpus can
  now sustain societies whose minds are heritable, and the first
  thing the generational ledger recorded is a refusal.

## Addendum, pre-registered 2026-07-29 before running: the storm season

G4's refutation named its own missing ingredient: recurring sudden
tau-selective mortality. Phase 5 measured the gradient (sudden-storm
mortality 0.14 to 0.78 across tau_safety 3 to 48: slow fear dies);
the season brings that mortality back on a clock over a birthing
population. One mechanism: storm_season 0 default (off, bit-inert);
when positive, the storm recurs every storm_season ticks (intensity
is the single-storm profile of (tick - onset) mod season, active
from onset onward), storm duration bounded by storm_length ticks of
full intensity before dying back to zero until the next arrival.
Declared before running:

* **S1, inertness ritual, kill switch**: all goldens replay
  behaviorally bit-identical; configs refreshed; suite green.
* **S2, the season kills selectively, manipulation check**: pooled
  across storms and seeds 1-24, the mean tau_safety of agents dying
  inside storm windows exceeds the concurrent survivors' mean by at
  least 10 percent. The phase 5 gradient must be present in this
  arena, or the season cannot breed anything and stops here.
* **S3, the breeding claim, G4's bar in the declared harsher
  arena**: over 8000 ticks of seasonal storms (season 800, length
  120, sudden onset, damage 0.05) on a birthing population with
  heritable fear clocks (tau_safety_spread 0.5, births 0.9/0.4,
  n_food 90), the final living population's mean tau_safety is at
  least 10 percent below the initial: the same unmoved bar, the
  arena the refutation itself prescribed.
* Fresh seeds 31-54 replication before packaging. Panel decision,
  recorded: no panel for this one-modulo delta; the ritual, a
  deterministic switch, and the S2 gate carry it, per the
  third-guard precedent.


### Season run 1 and the re-registration, recorded 2026-07-29

Run 1: S2 stopped the addendum with zero recorded storm deaths, and
the diagnosis is two errors, both mine, recorded in full. First, the
arena omitted the killing regime's own coordinates: phase 3 and 5's
storm mortality lived at bond 1.0 (the pull that cycles agents back
into the storm) in a hazardless world (cold fear, so the lag can
kill), with exposure long enough for return-cycling: my arena had
default bond, default hazards, and a 120-tick pulse everyone
outruns. Second, and worse for being the SAME lesson twice in one
phase: the death detector watched alive-flips, which same-tick
rebirth makes blind: the corrected seed-96 check found 23 storm
deaths where the blind one saw zero, with the dead carrying slower
clocks than the living (14.16 against 13.19). The phase's most
repeated sentence, earned twice: in a world with same-tick rebirth,
the absence of visible death is not the absence of death.

Run 2, re-registered, same bars: arena corrected to the killing
regime's own coordinates (bond_init 1.0, n_hazard 0, storm_length
400, otherwise unchanged), detectors corrected (a death is an
alive-flip OR a trait change on a previously living slot). S2's
1.10 gate and S3's -10 percent bar stand exactly as first declared.

### Season results, recorded 2026-07-29: selection is real and fecundity outruns it

Artifacts: `results/phase-24-season.json` (seeds 1-24),
`phase-24-season-replication.json` (fresh seeds 31-54). Judged
exactly as declared, on the corrected arena and detectors:

* **S2 PASSED, replicated**: agents dying inside storm windows
  carried mean fear clocks of 15.28 and 15.65 against their
  surviving contemporaries' 13.05 and 12.97, ratios 1.17 and 1.21
  against the 1.10 bar, over 1025 and 998 storm deaths. Phase 5's
  gradient is alive and generational: the storm kills the slow of
  fear, exactly as the one-generation autopsy said.
* **S3 FAILED, replicated, with the direction right and the
  magnitude a third of the bar**: mean tau_safety fell -3.5 and -6.2
  percent against the demanded -10, with populations at the full
  4800 at the end of every run.
* **The finding this pair earns, and it is the corpus's first
  population-genetic result: FECUNDITY OUTRUNS SELECTION.** The
  storm is selective (S2, decisively, twice), heredity is nearly
  perfect (G3, rho 0.97), and ten seasons of selective killing still
  move the population mean by a third of what the bar demanded,
  because every cradle the storm opens is refilled within a tick by
  whichever well-fed survivor stands lowest in the index, quick of
  fear or slow. Death selects; birth does not. The vessel's
  same-tick backfill is not a modelling artifact here but the
  mechanism itself: a population that refills faster than it is
  culled cannot be steered by culling alone.
* Declared follow-up, not run: selection needs a reproductive
  channel, not just a mortality one. The registered route is
  differential fecundity (birth eligibility or cost tied to lived
  state, so the quick-feared breed more, not merely die less), which
  is an amendment-level mechanism decision and is deliberately not
  built to rescue a failed bar.
* The refusal count stands at seven consecutive designer stories
  refused, and this one refused a bar the model had itself
  prescribed one addendum earlier.