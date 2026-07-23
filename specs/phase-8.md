# Phase 8: The pinned beloved

Status: **implemented 2026-07-23 under user sanction** ("if you feel that pin is also important, do that afterwards"; judged important because it completes the person-attachment collision phase 6 proved missing). Spec written before mechanism.

## Purpose

Phase 6 established that partners cannot produce the pull into danger because they are moving targets: caught agents die or leave within about 20 ticks, against a 60-tick bond clock. The missing world-fact is that danger can hold. This phase adds the snare: inside the storm, movement is slowed in proportion to the storm's damage intensity, down to zero at full grip. A trapped, living partner then becomes what a nest was in phase 3: a fixed point of attachment inside a lethal region, except this one is loved back and is dying. The predicted result is the rescue trap: the survivor is pulled in, gets gripped too, and the pair dies together, without one line of rescue code existing anywhere.

## Model addition (one world-fact)

* Config: `storm_snare` (bool, default false). When true, an agent inside the storm moves at speed scaled by `1 - damage_intensity` (the storm grips exactly as hard as it burns; a harmless warning ramp does not grip until it completes). Continuous, no branch on anything but geometry, default bit-inert (a speed factor of exactly 1.0).
* The agent's E table does not know about the grip: walking into the mire is the same declared myopic blindness as walking toward danger has been since phase 1.
* **The mire configuration** (declared here, the experiment's arena, not a default): snare on, `storm_damage 0.01`, so a trapped agent survives roughly 100 ticks at full intensity. Slow enough for the 60-tick bond clock to build the pull toward a still-living, visibly held partner. This is choosing where on the already-declared damage axis to look, recorded openly.

## Acceptance criteria

1. **Preservation.** Snare off: every golden trajectory bit-identical (config hashes refreshed, verified same-run).
2. **The pull exists once the beloved can be held.** Mire arena, partner mode, sudden storm, kappa 0, 6 seeds, n 400: among agents alive and outside the storm at onset+50, subsequent mortality of those whose partner is alive *inside* must be at least 2x that of those whose partner is alive outside, at bond 0.8; and show no such excess at bond 0.0. This is phase 6's criterion 4, judged as originally declared, now that the mechanism it presumed can exist.
3. **Rescue deaths are entries.** At least 70% of the pulled group's dead entered the storm after the snapshot: they went in, they were not caught.
4. **Attention interaction, reported as measured.** The same experiment at kappa 0.75 (the crisis-protective regime): does focus save the rescuer (fear dominates, they stay out) or doom them (bond dominates, they never hear the fear)? No threshold declared; the model answers.
5. **Golden.** One mire golden frozen.

## Non-goals

Rescue behaviours, carrying or freeing mechanics, snares outside storms, grip without damage, changes to drives, actions, or the E table.

## Deviations from spec during build

Recorded 2026-07-23. Full numbers in `results/phase-8-validation.json`.

1. **The snare became a declared strength, not a switch.** As first specced (grip equal to full damage intensity), the mire was an absorbing wall: anyone grazing the boundary froze at speed zero and died, producing 58% ambient mortality that drowned the comparison. `storm_snare` is now a float in [0, 1] (a swept axis; 0 is off and bit-inert), and the mire configuration is grip 0.95 with damage 0.01, chosen so a gripped agent's escape time sits near the bond clock. Intermediate grips (0.85) were also measured: nobody dies at all, the mire must both hold and burn.
2. **A mid-build wobble, owned**: with the first usable data I briefly rewired the judgment to the bond 0.4 arm, then restored the spec's declared bond 0.8 arm before any verdict was recorded; both arms are in the artifact. The declared arm passes: trapped-partner mortality 0.29 vs safe-partner 0.12 (ratio 2.4, n 28 pooled over 30 seeds, small and stated as such), with 88% of the pulled group's dead having entered the storm after the snapshot. The bond 0.4 arm: ratio 1.9 with every death an entry. The bond 0 control is immaculate: 127 split pairs, zero pull deaths.
3. **The cohesion shield, reported**: at bond 0.8, partners live 1.2 units apart, so a 10-radius storm takes both or neither and one-in one-out geometry is rare (n 28 in thirty seeds of 400). Deep attachment mostly forecloses the rescue trap by never being elsewhere; the trap's prime demographic is intermediate attachment, near enough to return, far enough to be out when it strikes.
4. **Criterion 4 (attention interaction) answered by an empty set**: at kappa 0.75 in the mire, no agent ever had a trapped living partner while safe outside, because the imprisoning-side dynamics push broad mortality (safe-group mortality 0.76) before such geometry arises. Reported as measured.
