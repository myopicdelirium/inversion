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
