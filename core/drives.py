"""The drive system: instant urgencies, lagged weights, one uniform law.

THIS IS THE ONLY FILE THAT MAY MUTATE DRIVE STATE (weights, urgencies,
time constants are read-only even here). See CLAUDE.md, Prime Invariant
and Amendment 1.

The Phase 1 mechanism lands here once specs/phase-1.md is approved:

  - urgencies computed instantly from body state each tick, as
    continuous functions, never branches
  - weights chase urgencies through the uniform lag:
    w += (dt / tau) * (u - w), every drive, no exceptions, forever
  - taus are read from Config and written never
"""

DRIVE_NAMES = ("energy", "safety", "rest")
