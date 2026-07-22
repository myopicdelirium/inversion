"""Action valuation and selection.

The Phase 1 mechanism lands here once specs/phase-1.md is approved:

  - a closed-form table of expected urgency reduction per (drive, action)
  - V(a) = sum over drives of weight * expected reduction
  - argmax with frozen index tie-breaking; action order is part of the
    model definition
  - myopic: no lookahead, no anticipation of drive dynamics

This file reads drive state and never writes it (CLAUDE.md chokepoint
rule; enforced by tests/test_invariants.py).
"""

ACTION_NAMES = ("seek_food", "flee", "rest", "wander")
