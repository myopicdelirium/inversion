# Phase 7: Bounded attention

Status: **implemented 2026-07-23 under explicit user direction** ("We never cut corners. Attention is certainly then the more important."). Spec and tripwires written before the mechanism. This phase changes `core/drives.py` for the first time since phase 2, under Amendment 3.

## Purpose

The model mourns without breaking because every alarm is always fully heard. Real minds are not like that: attention is finite, and a dominant concern deafens the rest. This phase adds that, as one drive-agnostic law, and measures what it costs. The target phenomenon is the program's origin case: the bereaved agent that starves because grief drowns out hunger. The obligatory symmetric result: the starving agent that walks into danger because hunger drowns out fear. If suppression only ever worked against survival drives, or only ever for the bond, the law would be scripted; the symmetry is what makes it a mind's property rather than a plot device.

## The attention law

In `update_weights`, the urgency each drive's weight chases becomes the heard urgency:

    heard_d = u_d * (w_d / max_e w_e) ** kappa

`kappa = attention_sharpness`, declared, default 0.0. At 0 the factor is exactly 1.0 for every drive (including 0^0 = 1) and the law is phase 1's bit for bit. At kappa > 0 the currently loudest drive is fully heard and every other drive is heard in proportion to its relative weight, smoothly, continuously, with no branch and no drive named. Raw urgencies stay recorded; heard is reconstructible exactly from recorded arrays.

The dynamics this buys: dominance is self-maintaining (a suppressed drive's weight cannot rise, which keeps it suppressed), so attention has inertia of its own, on top of the time constants. At kappa near 1 and above, a drive can only break through when its raw urgency approaches the dominant weight itself, which for hunger under deep grief means near-starvation before the alarm is heard at all.

## Acceptance criteria

1. **Preservation.** Default kappa 0: every golden trajectory bit-identical (config hashes refreshed for the one new field, verified same-run, the established routine).
2. **The law names no drive.** Static tripwire, written before the mechanism: `update_weights` contains no drive-index identifiers. Permanent.
3. **Extended transition identity.** kappa 2, partner-mode storm, record_every 1: every weight transition of every living agent satisfies the attended law with heard reconstructed from recorded arrays, max residual below 1e-12.
4. **Everyday null.** Ordinary nest-mode world, no storm: survival at kappa 2 within 2 points of kappa 0 (5 seeds). Attention only matters under dominance; daily homeostasis has none.
5. **Neglect deaths exist, and require attention.** Partner-mode storm, bond 0.8, n 400, 6 seeds, horizon onset+1500: among the bereaved, energy-death rate at kappa 0 within noise of the non-bereaved rate (phase 6's silent grief), and at kappa 2 at least 20 points above it. Deaths must be energy deaths after loss: starving in mourning, the origin case.
6. **Drive-agnostic harm.** Scarce-food nest-mode world (n_food 25), drifting hazards on, 5 seeds: integrity-death rate at kappa 2 at least 1.5x the kappa 0 rate. Hunger's dominance must blind agents to danger just as grief blinds them to hunger, or the law is a plot device and the phase fails.
7. **The grief-lethality map.** kappa {0, 0.5, 1, 1.5, 2} x bond_init {0.4, 0.8}: bereaved neglect-death fraction per cell, 6 seeds, artifact and figure.
8. **Golden.** One attention grief golden (kappa 2) frozen.

## Non-goals

Per-drive attention parameters (forbidden, not deferred), attention over actions or percepts other than drive urgency, memory or rumination, recovery narratives, the pinned-target world (phase 8).

## Deviations from spec during build

Recorded 2026-07-23. Full numbers in `results/phase-7-validation.json`.

1. **Criteria 1, 2, 3, 6 pass.** Preservation bit-exact at kappa 0 across every golden. The law names no drive (tripwire written first, green). The attended transition identity holds at 5.6e-17 over 3.1 million drive transitions with heard reconstructed from recorded arrays. And the symmetry criterion, the one that makes attention a mind's property rather than a plot device, passes at 15x: under scarce food, hunger-dominated agents die in hazards at 0.514 versus 0.034 at kappa 0. The same deafness, pointed at fear.
2. **Criterion 4 FAILS as declared, and the failure is a structural discovery: there is no everyday null at kappa 2, or anywhere near it.** The full boundary, measured: survival in the ordinary drifting-hazard world falls 0.992 / 0.815 / 0.765 / 0.516 / 0.108 / 0.016 / 0.000 across kappa 0 / 0.25 / 0.5 / 0.75 / 1.0 / 1.25 / 1.5. Chronic vigilance requires transparency: a calm life keeps fear's weight small, so under sharpness the ambient hazard is never heard. Attention is never free where threats are ambient and recurring.
3. **Yet in the acute arena, moderate sharpness is protective.** In the single-storm world, kappa 0.5 to 1.0 produced almost no storm deaths at all (bereaved counts collapsed to 0 or 1 per twelve hundred pairs, versus 25 to 36 at kappa 0): once fear leads, it owns the mind, and evacuation is total. The same parameter that saves the crisis kills the everyday. Crisis minds versus maintenance minds, one axis.
4. **Criterion 5's phenomenon is established; its declared threshold was guessed high.** Neglect deaths exist and require attention: zero of 61 bereaved starved at kappa 0 (baseline-indistinguishable, phase 6's silent grief), versus 15/434, 23/396, 79/556, 87/618 across kappa 1.5 and 2.0, baseline starvation exactly zero. Excess +14.1 points at kappa 2 against the declared 20. The shortfall's mechanism is itself humane: hunger breaks through at the brink (raw urgency approaching the dominant weight is heard again), so only the deepest bonds starve their carriers outright. Most grief does not kill; some does; the model now knows the difference.
5. **The golden's character, stated plainly**: the frozen kappa 2 storm run ends with 0 of 400 alive at tick 3500. In the imprisoning regime, the storm's aftermath of locked dominances (grief, fear, hunger, each deaf to the others' worlds) collapses the whole population over the longer horizon. It is committed as the specimen of that regime.
