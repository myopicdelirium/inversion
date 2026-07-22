# Build brief

Read `CLAUDE.md` first. It is binding. This brief is orientation, not law.

## The mechanism in one paragraph

Agents have drives. Each drive has an urgency (computed instantly from body state and percepts) and a weight (the agent's current valuation of that drive). Weights chase urgencies through a first-order lag with a per-drive time constant. Action selection is myopic argmax over action values, which are weight-weighted expected urgency reductions. That is the entire kernel. Preference inversion, when it eventually appears, is a timing failure: a commitment drive has accumulated weight over a long horizon, a lethal threat arrives, survival urgency spikes instantly, but the survival weight cannot relax back to dominance before the decision is forced. The agent dies mid-reversion. Death is a failure to re-prioritize in time, never a valuation of death.

## Why the ordering of phases matters

The inertia law ships in Phase 1, with base drives only, before any commitment machinery exists. The lag is measured and validated as an artifact then. When sacrifice appears in later phases, the mechanism provably predates the phenomenon: nobody can claim it was added to produce the result, because it was there when agents could only eat, rest, and flee.

## Phase plan (provisional; each phase gets its own spec before code)

1. **Homeostat kernel.** Base drives (energy, safety, rest), uniform lagged update law, myopic argmax, deterministic harness, manifest writer. Validation artifact: empirically fitted lag time constant matches the declared parameter.
2. **Commitment as an ordinary drive.** The same drive class with slow accumulation dynamics (attachment to a target: place, agent, activity). No new mechanism. Validation: commitment accumulates and decays on its declared timescales; no behavioural change in environments without commitment targets (golden runs from Phase 1 still pass).
3. **Collision environments.** Environments where threat onset speed is controllable, so the timing collision becomes reachable. Validation: the null test: telegraphed threats produce collapsing sacrifice rates at fixed commitment; sudden threats do not.
4. **Sweep machinery.** Batch runner over (accumulation rate, reversion time constant, threat onset speed, ...); manifests per run; results aggregation.
5. **The phase diagram.** Population-scale sweeps (10k+ agents, thousands of runs). The map of where inversion lives and where it does not is the product.

## Current status

Phase 1 complete: homeostat implemented, calibrated, and validated. All acceptance criteria met; artifacts committed under results/; golden run under tests/golden/. Next: Phase 2 spec (commitment as an ordinary drive).
