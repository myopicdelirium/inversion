# Phase 13: Full sight

Status: **implemented 2026-07-24 under standing delegation**. The declared follow-ups of phase 12, combined into the definitive experiment.

## Purpose

Phase 12's flag could only fire for the already-wounded (seeable price capped at horizon times burn) and its persistent deaths were trap-underestimation (the grip absent from the agents' physics). This phase removes both limits: the grip becomes part of the agent's declared physics behind a config switch, and horizons extend so a whole life fits inside the seeable price. The question, in its final form: with the trap seen, the burn seen, and a life-sized price computable, does any agent still choose toward the trapped beloved at excess mortality? Either answer bounds the architecture. No direction is desired.

## Model addition (Amendment 4 extension, one switch)

* `prospect_sees_grip` (bool, default false, bit-inert: every golden preserved; the switch is itself an axis: what an agent knows about the world is part of the psychology space).
* When true and a storm is active, the farsighted rollout prices destinations with the grip, under declared radial approximations: a target inside the storm is reached by an outside leg at normal speed plus an inside leg of length (radius minus the target's center distance) at gripped speed; the inside leg and any held remainder are priced at the danger at the target (an overestimate of the leg, so full sight errs toward seeing too much price, the conservative direction); arrivals beyond the horizon buy nothing. Applied to both food targets and bond targets: the grip is world physics, so a full-sight agent prices it everywhere.
* **Up-front clear-eyed**, the new sub-metric: a phase 12 flag fired while integrity is at least 0.8: a near-whole life priced and chosen. The phase 12 flag itself is unchanged.

## The grid (mire arena as phase 12; bond 1.0 throughout, the deepest ledger; controls at bond 0)

`tau_safety` {12, 48} x `kappa` {0, 0.75 at floor 0.05} x `prospect_horizon` {60, 120} x `prospect_sees_grip` {false, true}: 16 search cells plus 16 controls, 12 seeds each, then the full grid replicated on fresh seeds 31-42: 768 runs.

## Pre-registered

* **G1, the question, no desired direction**: with sight full and the price life-sized, either at least one cell shows the phase 12 cell criteria met with at least one up-front clear-eyed death among its dead entrants (the wager exists), or no cell does (the architecture cannot produce the up-front wager over this grid; bounded and reported).
* **G2, falsifiable direction**: sees_grip true reduces trap-underestimation: among pull-group dead entrants, the share whose entry decisions were priced survivable falls relative to sees_grip false at the same coordinates.
* **G3, inertness**: sees_grip false and horizon unchanged reproduce every golden bit for bit (config hashes refreshed for the one new field, trajectory hashes verified, the routine).
* **Replication before packaging**, per the standing default.

## Non-goals

Per-agent knowledge as a trait (a later axis), grip-aware pricing of flee or wander paths (fleeing exits, wandering is undirected; declared), changes to the phase 12 flag, forensics of the remaining phase 12 individuals (available separately on request).

## Deviations from spec during build

Recorded 2026-07-24. Full grids in `results/phase-13-search.json` (seeds 1-12) and `phase-13-replication.json` (fresh seeds 31-42), 768 runs, plus one instrumentation note: after the first search pass showed deaths without entries, cause-of-death fields were added and both grids rerun in full; the first pass's numbers are reproduced identically in the rerun (deterministic), so no verdict ever rested on the uninstrumented pass.

1. **G1 answered, and replicated: no wager cells, no up-front clear-eyed deaths, anywhere.** Zero of 16 cells on either seed set, and zero individual up-front flags (a whole life priced and chosen) in 768 runs, including horizon 120 with the grip seen, where the seeable price comfortably exceeds a full life. Combined with phase 12: this architecture, as searched, does not make the up-front wager. Its clear-eyed deaths remain endgame perseverance only.
2. **G2 holds on both seed sets**: full sight collapses entry deaths. With sees_grip on, entered shares of pull-group deaths fall to 0.00 in eleven of sixteen cells (max 0.33) versus 0.20 to 1.00 with sight off. The trap-underestimation deaths of phases 8 and 12 were exactly what they were named: mispricings, gone when the price is seen.
3. **The replacement death, established as a mode, suggestive as an excess.** With sight on, pull-group deaths become essentially 100% starvation on both seed sets (starved shares 1.00 in nearly every sees-on cell): agents with trapped partners will not enter (the price is seen) and will not leave (the pull), and they starve at the threshold. The honest caveat, found by the instrumentation: controls also starve more under full sight, because food lying in the storm's shadow is priced prohibitively too, an ambient seen-famine. The pull group's pooled excess over that background is +3 points (original) and +8 (replication), cell-noisy. The threshold vigil is real as a death mode; as an attributable excess it is suggestive and would need a matched-famine, higher-power design, declared as the follow-up if wanted.
4. **G3 held**: the switch is bit-inert off; all eleven golden trajectories verified unchanged; config hashes refreshed for the one new field, the routine.
5. The threshold-vigil golden freezes the regime (sees on, tau_safety 48, h 60, seed 42, 273 of 400 alive).


## Addendum, pre-registered 2026-07-29 before running: the severed twin

Phase 13 established the threshold vigil as a death mode and left its
excess suggestive (+3 and +8 points, cell-noisy) because full sight
creates an ambient seen-famine that starves controls too. The matched
design this called for now exists as a tool, proven by the phase 21
amputation: the counterfactual twin. Two runs per seed, bit-identical
to the cut tick because severing consumes no draws; in the twin, the
instrument sets the vigil-keepers' bond to zero and their partner
pointer to absent at the cut, leaving position, energy, memory, and
the seen-famine untouched. The same agent, with and without its love,
in the same famine. Declared before running:

* **Arena**: the threshold-vigil regime exactly as frozen in
  tests/golden/phase13_threshold.json (config replayed from the
  golden, the embedded-config discipline), 3500 ticks, onset 2000.
* **Cohort**: at tick 2300, alive agents whose living partner is
  inside the storm while they stand outside within 15 units of the
  rim. V1, power floor: at least 150 pooled across seeds 1-24, else
  the design says so and stops.
* **V2, the attributable excess, the question phase 13 left open**:
  kept-arm starvation among the cohort exceeds severed-arm
  starvation by at least 5 points, pooled, both seed stages (1-24
  declared, 31-54 replication). Refutation clause at full volume: if
  severing the bond does not save the vigil-keepers, the threshold
  vigil was ambient famine wearing a bond's face, and the phase 13
  mode is revised accordingly.
* **V3, reported without bar**: the severed twins' post-cut death
  rate beside the never-pulled background, for the record.
* The severing is an instrument edit in the validation script, the
  flatten-trick pattern; no core code path changes, no RNG is
  consumed, and the twin's prefix is bit-identical by construction.

### Severed-twin run 1, recorded 2026-07-29: V1 failed, the design stops and says so

Artifacts: `results/phase-13-twin.json`, `phase-13-twin-replication.json`.
V1 found 4 pooled vigil-keepers on the declared seeds and 0 on fresh
seeds against the 150 floor; V2 and V3 are void at that n. The
diagnosis, from the arena's own arithmetic: the mire burns 0.01 per
tick, so partners trapped at onset are dead by roughly tick 2100, and
a cohort defined by a LIVING partner inside at tick 2300 is a
contradiction. The threshold vigil phase 13 observed is largely kept
over the dead: the pull begins at capture and persists through the
partner's death as grief (separation is total either way). The cut
tick was mine to choose and I chose it wrong; recorded, not hidden.

### Re-registration, 2026-07-29, before the corrected run: cut at 2050

Same twins, same bars, one corrected coordinate: the cohort is taken
at tick 2050, phase 13's own snapshot convention, while trapped
partners still live. V1 at least 150 pooled (seeds 1-24), V2 kept
minus severed starvation at least 5 points both stages, V3 reported.
The severing at 2050 now cuts a live bond mid-vigil, which is the
cleaner experiment anyway: the twin loses its beloved to amnesia at
the exact moment the original stands watch.

### Run 2 recorded and the power re-registration, 2026-07-29

Run 2 (cut 2050): V1 failed again, 17 and 16 pooled against the 150
floor, and the cause is the one-body finding recurring: pairs are
caught together, so a living partner inside with its mate outside is
structurally rare, about 0.7 per seed. At that n, V2's sign flip
(+17.6 then -12.5 points) is noise and void. Third registration,
changing only power, never bars or design: seeds 1-240 declared,
241-480 replication, same cut 2050, same cohort, same V1 floor of
150, same V2 bar of 5 points. Expected yield sits near 170 per
stage; if the floor fails a third time, the verdict is that the
vigil's attributable excess is unmeasurable at any honest power in
this arena family, and phase 13's suggestive +3/+8 stays suggestive
permanently.

### Severed-twin verdicts, recorded 2026-07-29: the vigil's deaths belong to the famine, not the bond

Artifacts: `results/phase-13-twin.json` (seeds 1-240),
`phase-13-twin-replication.json` (seeds 241-480). Judged exactly as
declared:

* **V1 PASSED at the third registration's power**: 214 and 232
  pooled vigil-keepers against the unmoved 150 floor.
* **V2 FAILED both stages, and the refutation clause fires as
  written**: kept-arm starvation 0.491 against severed 0.477 (+1.4
  points), then 0.444 against 0.474 (-3.0), straddling zero against
  a 5-point bar. The same agent, at the same rim, in the same seen
  famine, with its love surgically removed at tick 2050, dies at the
  same rate. V3 matches on all-cause.
* **The phase 13 revision, at the promised volume**: the threshold
  vigil is real as a behavior and misattributed as a death. The bond
  explains WHERE the watcher stands, because the pull positioned it
  at the rim before the cut. But once there, removing the bond does
  not free it: the severed twins stayed and starved at the same
  rate, because under full sight every path near the storm is priced
  through shadowed food, and the rim is a trap made of prices rather
  than of love. Phase 13's replacement-death mode is hereby revised:
  the deaths at the threshold belong to the seen famine; the bond's
  attributable share, from the vigil onward, is statistically zero
  (+1.4 and -3.0 points). Love positions; prices execute.
* The suggestive +3 and +8 of the original grids are thereby
  explained rather than confirmed: they were the bond's positioning
  effect feeding agents into the famine's reach, not a mortality the
  bond exacts at the rim. Three registrations, two honest power
  failures, one clean answer through the counterfactual-twin
  instrument.