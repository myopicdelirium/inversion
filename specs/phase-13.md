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
