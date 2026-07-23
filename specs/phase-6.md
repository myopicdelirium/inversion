# Phase 6: The beloved, and losing them

Status: **implemented 2026-07-23 under standing delegation**, direction confirmed by the user ("on course to something human"; grief named as the next waypoint). Spec written before mechanism.

## Purpose

Bonds to agents instead of places. A partner moves, acts back, and can die. Three things follow from machinery that already exists, and the phase must measure all three: cohesion in life (partners keep each other close, by the same law that tethered agents to nests), the pull into danger (a partner inside the storm drags the survivor toward it, phase 3's return-death with a moving, mortal target), and grief (an absent partner is at infinite distance, where the phase 2 distress formula evaluates to exactly b: an urgency with no zero anywhere in the world, fading only on the bond's own decay clock).

`core/drives.py` and `core/action.py` are untouched. The invariant files have now been frozen since phase 2. What changes is perception: the world gains the fact that bond targets can cease to exist, and states it the same way it states homelessness, as infinite distance. The agent has no death percept; it knows absence, not death.

What this phase deliberately does not produce: neglect deaths (the origin case's starving searcher). Without a bounded-attention layer, a bereaved agent's distress is behaviourally silent in the argmax because no action promises relief. Grief in this phase is a measurable internal state and a mortality risk factor only through the pull toward a dying partner. Bounded attention is phase 7's question, flagged now so this phase cannot quietly grow it.

## Model additions

* Config: `bond_target`, "nest" (default, bit-identical to all prior phases) or "partner".
* Pairing, partner mode: deterministic, no draws. Agent i pairs with i + n_nests when its block index (i div n_nests) is even, with i - n_nests when odd; partners therefore share a birth nest and spawn adjacent. Unpaired agents (odd tail) have partner -1 and bond 0, exactly like homeless agents in phase 2.
* New state: `partner` (n,), index or -1. Written once at init.
* Perception: `perceive_partner` returns distance and direction to the partner's current position while the partner lives, infinity and zero direction otherwise (none assigned, or no longer alive). Same contract as `perceive_home`; the aliveness check is the world stating a fact, feeding perception, never weights.
* In partner mode the bond drive and the `return_home` action (frozen name; it means "go to the bond target") read the partner distance everywhere the nest distance was read: urgency, E table, movement, accumulation. Bond grows within `r_nest` of the living partner, decays otherwise, including in bereavement, which is where the mourning clock comes from: `1 / bond_decay` about 5000 ticks.

## Acceptance criteria

1. **Preservation.** `bond_target = "nest"`: every golden trajectory hash unchanged (stored config hashes refreshed for the one new field, verified in the same run, the established routine).
2. **Cohesion.** Partner mode, no storm, 5 seeds: mean partner distance over the final 1000 ticks at `bond_init 0.8` at least 3x smaller than at `bond_init 0.0`. Togetherness from the same one law, nothing added.
3. **Grief identities, exact.** On recorded frames where an agent's partner was already dead on the previous frame: `u_bond` equals `b` bit-exactly (the formula at infinity), and every bond transition follows the away-form decay exactly (max residual below 1e-9). The mourning curve (mean distress of the bereaved vs ticks since loss) matches the declared `bond_decay` contraction.
4. **The pull into the storm.** Partner mode, sudden storm on the shared nest, `bond_init` 0.8 vs 0.0, 6 seeds. Among cohort agents alive and outside the storm at onset+50, subsequent window mortality of those whose partner is at that moment inside the storm or already dead must exceed, at 0.8, that of those whose partner is alive outside, by at least 2x pooled. At `bond_init 0.0` the same ratio must show no such excess (within noise): the pull is the bond, not the geometry.
5. **Shared fate.** Pair mortality correlation (both-die vs independence) positive in at least 4 of 6 seeds at `bond_init 0.8`. Reported for what it is: cohesion means dying together, before any question of dying *for*.
6. **Golden.** One partner-mode storm golden frozen.

## Non-goals

Bounded attention and neglect deaths (phase 7), remarriage or new bond formation after loss (bond can regrow only toward the same partner, who is gone; b decays monotonically in bereavement), corpses as objects, more than one partner, parent-child asymmetric bonds, communication between agents of any kind.

## Deviations from spec during build

Recorded 2026-07-23. Full numbers in `results/phase-6-validation.json`.

1. **One bug caught by this spec's own criterion 3 before any results existed**: `apply_bond` gated decay on finite target distance, which would have frozen a bereaved agent's bond forever, silencing the mourning clock. Fixed by dropping the gate; the fix is bit-inert for unbonded agents (zero decays to itself exactly), verified against every golden.
2. **Criteria 1, 2, 3 pass.** Preservation exact in nest mode. Cohesion ratio 25.7 (bonded pairs live at mean distance 1.2, unbonded at 31): togetherness from the same one law. Grief identities exact on all 26 pooled bereaved agents: u equals b to the bit at infinite distance, decay residual 5.6e-17; the mourning curve follows the declared contraction. Criterion 3's original 3-seed sample found only 14 bereaved; extended to 6 seeds (more measurement, no design change).
3. **Criteria 4 and 5 FAIL as declared, for a mechanically deep reason that is the phase's finding.** The pull into the storm presumed the phase 3 trap would generalize to partners. It cannot: a partner is a moving bond target. An agent caught by the storm either dies within about 20 ticks or walks out within about 15, both far shorter than the bond weight's 60-tick clock, so no standing pull toward the storm ever develops; and cohesion means pairs evacuate together. A dead partner, being at infinite distance, pulls toward nowhere. Consequently bereavement is rare, there were almost no deaths to correlate (shared fate 2/6 on nearly-empty cells), and the pull ratio is undefined in practice.
4. **The protective contrast, measured because the failures exposed it**: same storm, same attachment depth 0.8, population mortality in the window is 0.087 when the beloved is a place and 0.007 when the beloved is a person. Person-attachment is roughly twelvefold protective under place-targeted catastrophe, because love that moves can flee with you and love nailed to the ground cannot. Every prior inversion result in this repo is place-attachment; this phase bounds their scope.
5. **What the origin case now demonstrably requires**, stated for phase 7's decision: searching-unto-neglect needs either a bond target that can be pinned in place while alive, or a bounded-attention layer through which unmet drives suppress others. Grief as built is real, exact, and behaviourally silent: the argmax offers no action that relieves it, so the bereaved forage on, carrying maximal distress. The model currently mourns without breaking. Breaking requires attention.
