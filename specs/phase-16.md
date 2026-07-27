# Phase 16: the rumor of danger

Pre-registered 2026-07-27, spec and tripwires before mechanisms, per the
constitution. This phase gives the agent a social sense: honest displays,
earned credence, and testimony. It is the first stone of the social
system and the capability the transmission phases build on.

## The mechanism, declared

* **Displays are honest because they are not writable.** An agent's
  display is its safety urgency from the previous tick, read directly
  from the drive state. There is no display array, no suppression path,
  no posture. A tripwire enforces that no such array ever exists.
* **Credence is one number per (listener, signaler) pair**, initialized
  at cred_init 0.5, moved only at the close of verification windows by
  the integrated form of the one law: c += (1 - exp(-W/tau_cred)) *
  (score - c). tau_cred 24, verify window W 30. No spread this phase;
  spreads arrive with the affiliation phase.
* **An alarm** is a neighbor within r_social whose display crosses
  alarm_threshold 0.6. It opens one window per listening pair. The
  window scores 1 if the listener's own unmediated local danger reaches
  verify_level 0.1 at any tick before the window closes, else 0.
  Scoring is egocentric: verified means the danger reached me.
* **Testimony** enters the safety urgency as evidence: u_safety becomes
  the max of local danger and testimony strength times the loudest
  discounted rumor, max over neighbors of display times exp(-d/r_social)
  times max(credence, cred_floor). It competes in the same bounded
  attention field under the unchanged law. drives.py remains the only
  writer of drive state; social.py computes a percept and is the only
  writer of credence.
* **Inertness**: r_social 0.0 is the default and the social organ is
  absent: no state allocated, no arithmetic run, every existing golden
  bit-identical. Adding the axes changes every config hash, so this
  phase performs the golden-refresh ritual: rerun every stored golden
  under its stored config plus new defaults, assert the behavioral
  sha256 unchanged, rewrite the embedded config and hash.

## Registrations, before running

* **R1, the law made exact, kill switch**: under k consecutive false
  windows credence equals cred_init * (1-g)^k with g = 1-exp(-W/tau_cred),
  machine-exact, and under mixed scores it converges toward the
  empirical score rate. Any deviation stops the phase as an instrument
  or law violation. This is the memo's fitted-tau discipline applied at
  build time.
* **R2, the cry-wolf ledger**: in the social arena (defaults plus
  r_social 8, testimony 1.0, kappa 0, n_hazard 9, hazard_drift 0.02,
  5000 ticks), across (listener, signaler) pairs with at least 8
  closed windows, the median absolute gap between final credence and
  that pair's empirical alarm accuracy is at most 0.10, with at least
  50 qualifying pairs pooled or the verdict is underpowered. Seeds
  1-24 declared, fresh seeds 31-54 replication. The claim in words:
  reputations converge to truth rates, warning fatigue is bookkeeping,
  not mood. Amendment before any declared-seed outcome: the first
  registration said drifting hazards as shipped over 3000 ticks; the
  design check on unused seed 99 found scares too brief for repeat
  windows (max 3 per pair, zero qualifying), so the arena was made
  slow and dense (9 hazards, drift 0.02, 5000 ticks: 40 qualifying at
  seed 99). Hazards that linger create the repeated encounters a
  reputation needs. Peek recorded: seed 99 only.
* **R3, the social cure, falsifiable direction**: in the boiling-frog
  inversion cell of phase 5 (nest mode, bond_init 0.6, storm_ramp 200,
  damage mode, storm on nest 0 at onset 2000, 200 agents, 5 nests),
  with r_social 8: nest-0 cohort window mortality at testimony 1.0 is
  at least 25 percent relatively below testimony 0.0, same seeds,
  seeds 1-24 declared, 31-54 replication. The mechanism on trial: the
  rumor runs ahead of the wave, neighbors deeper in the gradient
  display the future to those farther out. If it fails, the finding is
  that rumor cannot outrun the cook when every voice whispers from
  inside the same pot, and it is reported exactly so.
* **Exploratory, no bar**: pariah census in the R2 arena at cred_floor
  0 versus 0.01, reported for the affiliation phase to build on.

## Honesty notes

The verification window is [open, close): peril at the open tick
counts, peril at the closing tick does not. Co-occurring peril
therefore verifies: neighbors in shared danger vouch for each other by
geography, and tightening to strictly-predictive scoring would be a
declared change, not a patch. Displays lag one tick by construction. Scoring is egocentric, so a
correct warning about danger that turns aside scores 0; accuracy here
means accuracy about the listener's own future, which is the only
ledger a listener can keep. The R3 cohort is nest-0 agents alive at
onset, matching phase 5 accounting.

## Deviations

* **Redirection, 2026-07-27, before any declared-seed outcome ran.**
  The R2 and R3 protocols were designed to chase phenomena imported
  from an older system rather than to deepen the agent, and the
  project's standing priority is richness of the individual first,
  experiments after. The mechanism stands: credence is interiority, a
  private earned opinion of every neighbor, and it ships with its
  tripwires, its R1 kill-switch test, and its inertness proof. The R2
  and R3 registrations are DEFERRED, not run, not judged; they remain
  on file with their bars intact for whenever the experiment queue
  reopens, and nothing here may be cited as a finding. Phase 16
  closes as a capability delta only.
