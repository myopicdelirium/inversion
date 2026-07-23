# Phase 10: The whisper floor

Status: **implemented 2026-07-23 under delegated judgment** ("I trust your judgement. Move forward."). The zero-trap decision: soften without deleting. Spec before mechanism.

## Purpose

Phase 9 found the attention law's absolute fixed point: a drive with weight exactly zero is unhearable forever. That regime is real and stays reproducible at floor 0, but as the only option it is an idealization cliff that dominated every attention map. The floor makes it the boundary of an axis: `heard = u * max(w / max w, attention_floor) ** kappa`, floor declared, default 0 (bit-inert, every golden preserved), one scalar for all drives.

## Pre-registered predictions (floor 0.05 throughout)

* **F1, fear becomes acquirable.** Everyday world at kappa 1: survival recovers from 0.108 (floor 0) to at least 0.5.
* **F2, peacetime collapse is cured.** Place arena, bond 1.0, kappa 1.5: agents alive at storm onset recover from 0-1 of 200 to at least 150.
* **F3, the origin case survives the fix.** Partner-storm grief cell (kappa 2, bond 0.8): bereaved neglect-death rate stays at or above 3% with baseline near zero. If the floor erases the phenomenon, the fix deleted the finding and that gets reported, not hidden.
* **F4, the axis becomes smooth**: the everyday kappa boundary at floor 0.05, remeasured, no longer collapses to extinction by kappa 1.5 (survival above 0.3 there).

## Acceptance criteria

1. Preservation at floor 0: every golden trajectory bit-identical (config hashes refreshed, the routine).
2. F1 through F4 judged as written; failures reported as findings.
3. Artifact `results/phase-10-floor.json` with all cells; the names-no-drive tripwire still green (the floor is scalar).
4. One golden freezing a floor-on regime.

## Non-goals

Per-drive floors (forbidden), floor values other than {0, 0.05} beyond the F4 boundary sweep, any change to prospection (phase 11).

## Deviations from spec during build

Recorded 2026-07-23. Full numbers in `results/phase-10-floor.json`.

1. **F1, F2, F4 hold as pre-registered.** Fear is acquirable (everyday kappa 1 survival 0.108 to 0.587), the peacetime collapse is cured (alive at onset 153-190 of 200 versus 0-1), and the kappa axis is smooth at floor 0.05 (0.992 / 0.924 / 0.587 / 0.447 / 0.000 across kappa 0 / 0.5 / 1 / 1.5 / 2).
2. **F3 FAILS as declared at floor 0.05, and the failure exposed two findings.** First, a new phenomenon: hypervigilance starvation. At kappa 2 with the floor, storm survivors can now acquire fear, fear then dominates, and the non-bereaved baseline starves at 12.5%, swamping any grief-specific signal (excess -2.9 points). Also observed at kappa 1 and 1.5 with floor 0.05: grief-specific excess is zero everywhere. The floor at 0.05 abolishes the origin case entirely: a mind whose hunger keeps even a 5% whisper always hears it in time.
3. **The boundary, mapped along the declared axis**: grief-specific excess is +14.0 points at floor 0.005 and +14.6 at 0.01 (baselines exactly zero), +5.8 at 0.02 (hypervigilance appearing at 8.1%), and gone at 0.05. Starving in mourning does not require the absolute zero-trap, but it requires a whisper at or below about one percent relative hearing. The floor is a genuine psychological axis: how faint a suppressed need's voice can be before devotion can starve you. The faint-whisper golden (floor 0.01, kappa 2, 245 of 400 alive) freezes the origin case in its post-trap form.
4. Phase 7's and phase 9's floor-0 results remain exactly reproducible; nothing was deleted, the trap became a boundary.
5. **Replication (pre-declared, fresh seeds 11-16, results/phase-10-replication.json), and a withdrawal.** R1 and R2 hold (everyday kappa 1 survival 0.629; peacetime-cure alive-at-onset 143-189). R3 FAILS: at floor 0.01 the bereaved neglect rate replicates (0.141 vs 0.146) but the baseline starvation rate is bistable across seed sets (0/187 original, 23/135 fresh), so grief-specific excess flips from +14.6 points to -2.9. The deviation-3 boundary claim (grief-specific below floor 0.01, hypervigilance above 0.02) is therefore WITHDRAWN pending high-seed measurement: it was drawn from 6-seed cells over a quantity with run-level clustering. What survives both seed sets: the floor-0 origin case (twice replicated, baselines exactly zero both times); bereaved neglect rates persisting under any floor measured (8.5-14.6%); and baseline hypervigilance starvation as a real but run-bistable phenomenon whose dependence on the floor is unresolved.
