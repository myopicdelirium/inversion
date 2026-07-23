# Incident: apparent trajectory nondeterminism

Date: 2026-07-24. Status: **CLOSED: operator error, fully explained, no nondeterminism ever existed.**

## What was observed

Across phases 14 and 15, the two sight-on goldens (phase 13 threshold, phase 14 care) appeared to flip between bit-exact match and one consistent alternative trajectory: within-process consistent, across-process bimodal, seemingly machine-global and time-varying, surviving bytecode purges and source diffs, while a clean-room clone always matched. Successive wrong explanations were adopted and then retracted in this file's history: stale bytecode (real as import hygiene, irrelevant to dynamics), then concurrent repository mutation by a parallel session (withdrawn; the operator confirmed single-writer and none was needed).

## The actual cause

The verifier's own scripts. The goldens were frozen and tested with directly constructed configs carrying the default bond_init 0.5. The ad hoc verification loops rebuilt those configs through a convenience chain (partner, then mire) that silently carried bond_init 0.8 from an unrelated definition. Two different configs, two different deterministic trajectories. Every observation maps exactly onto which construction style each script used. Decisive proof, one process, side by side: the direct construction matches the golden, the chained one mismatches, and `direct == chain` is False.

The engine was bit-deterministic throughout. No golden was ever violated. Clarification kept for the record: the frozen phase 13 and 14 specimens are the bond_init 0.5 variants of their regimes; the grid claims in those specs rest on the grid artifacts (which used 0.8); both are internally consistent.

## The systemic fix, in force

Hand reconstruction of golden configs is abolished. Every golden file stores its complete config; `tests/test_golden.py` replays `Config(**stored)` and verifies the stored hash before running. A config can no longer be approximately remembered, only exactly replayed. Cache purging before verification is retained as hygiene. The one-writer-per-repository convention remains sensible practice but was not implicated.

## The lesson, stated plainly

Fourteen phases of infrastructure meant the impossible was correctly rejected at every step: the engine never once looked nondeterministic under a controlled test. The failure was that verification scripts were rewritten from memory instead of replayed from a record, exactly the error class the golden system exists to prevent, one layer up. The fix applies the project's own principle to its own tooling.
