# Incident: intermittent per-process trajectory divergence

Date: 2026-07-24. Status: **REOPENED. Leading hypothesis: concurrent repository mutation by parallel sessions.** The earlier stale-bytecode finding explains at most one burst; the full observation set does not reduce to it.

## Observations, complete

1. During phase 14's preservation check, the phase 13 threshold golden (partner mode, sight on, 400 agents, 3250 ticks, seed 42) reported a combined-hash mismatch once, inside a 13-check loop process. Three immediate single-run processes matched, all nine per-array hashes matched, and the full test suite then passed, twice.
2. During phase 15's preservation check, the same golden mismatched again in a loop process, then mismatched four more times within one subsequent interpreter (isolated run, run after warm-up runs, and two repeats: consistent within that process). Three fresh subprocesses immediately after all matched, including one with the identical working tree.
3. The working-tree diff at the time was provably inert for the affected mode (a guarded init block for a different mode, membership-equivalent condition rewrites, one added config field), and reverting it did not correlate with the flips.
4. Characterization since: `scripts/determinism_canary.py` (24 fresh processes x 3 conditions, short config) and 12 fresh processes of the exact failing configuration: 84 of 84 identical hashes. Within the mismatching bursts, results were self-consistent per process; across processes, bimodal.

## What it is not

Not the recorded arrays' rounding (per-array hashes matched during burst 1's aftermath); not explained by any code change (burst 2's flips spanned identical trees); not reproduced under pinned numpy SIMD dispatch or default dispatch in 72 canary runs.

## Standing mitigations, effective immediately

1. **Two-process rule**: no golden verdict (mismatch or match) is acted on from a single process. Any mismatch must reproduce in a second fresh subprocess before being treated as a dynamics change; refresh rituals verify trajectories in two independent processes.
2. The canary stays in `scripts/` and is run when any anomaly appears, and periodically before major phases.
3. Interpretation guard: distribution-level results (pooled grids, replicated on fresh seeds) are robust to a rare flaky process; bit-level claims on this machine carry this incident as a caveat until the cause is found.

## Root cause, established by clean-room bisection

A fresh clone with the byte-equivalent edits matched every golden in every process, while the main worktree mismatched consistently; purging `__pycache__` in the main worktree restored bit-exact matches immediately (3/3 processes), with the source trees differing only in comments. Python validates cached bytecode by (mtime-in-seconds, size); the session's rapid edit-run-revert cycles (including git checkouts that rewrite files) produced collisions where a stale compiled module from an intermediate edit state silently loaded as current. This explains every observation: per-process self-consistency (one stale pyc per process), cross-process bimodality (which cache entry a process found), the correlation with edit bursts, and the immunity of the clean room. No engine nondeterminism existed; the dynamics were always deterministic per loaded code.

## Hardened mitigations, superseding the above

1. **Cache purge before verification**: every golden refresh or verification ritual begins by deleting `__pycache__` under the project (never the venv), making stale-bytecode masquerade impossible. The two-process rule alone is insufficient, since both processes can read the same stale cache.
2. The canary stays for anomaly triage; a clean-room clone is the escalation of record.
3. All thirteen goldens re-verified bit-exact after the purge; no golden was ever actually violated by the dynamics.


## Reopening, same day

After the bytecode resolution, the flips continued under conditions that rule that cause out: caches purged, sources verified identical, fresh single-run processes flipping from four-of-four GOLDEN to MISMATCH and back within minutes, machine-globally, with both states internally consistent. Order-dependence hypotheses failed reproduction (isolated runs mismatched during one window; predecessor-run probes all matched in another). The final observation set is consistent with exactly one simple cause: the repository's source files changing under the verifier between runs and changing back.

Supporting facts: three claude-code sessions were running concurrently on this machine at observation time; a parallel session has previously committed directly to this repository (the phase 3 spec, commit 7f67213); golden-file mtimes exist that this session cannot account for. Not conclusive, but every alternative requires new physics and this requires only a second writer.

## Disposition

1. All phase 15 verification is HALTED pending single-writer confirmation from the operator. No golden verdict from the affected window (either direction) is trusted.
2. This session's in-flight work is snapshotted on branch `phase-15-wip` to fix a forensic reference point.
3. Standing rule proposed for the constitution once confirmed: one writer per repository at a time; parallel sessions coordinate through commits and branches, never through a shared working tree.
4. The stale-bytecode mitigation (cache purge before verification) remains in force regardless; it is correct hygiene even if it was not the whole story.
