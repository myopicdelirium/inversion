# Phase 25: Through the eyes (the altruism ladder, opening phase)

Status: **registered 2026-07-29 under standing delegation**, before any
protocol run. Spec before mechanism. This phase opens the corpus's
first experimental program, declared by the director in these words:
"the first thing that we are going to be studying is true altruism.
Not encoded altruism, not presenting something that looks like true
altruism, but the conditions that could argue that we have the
capacity to be truly selfless, however you wish to define the self and
things outside it."

## The definitional groundwork

**The self.** In this architecture the self is the ledger and the
body: the drive weights and urgencies that price every action, and the
energy, fatigue, and integrity that feed them. **The other** is every
state held in a different slot's arrays. These definitions are chosen
once, here, and every claim in the program is relative to them.

**The structural confession, first.** This agent is psychological
egoism implemented. Every action it ever takes is the argmax of its
own weighted expected relief; there is one ledger per agent and it is
that agent's own. Naive "true altruism", an action whose expected
value in the actor's own ledger is negative and which is chosen
anyway, is impossible by construction, and no observation of helping
will ever be reported as if it were evidence of it. Three phases (12,
13, 14) already asked the strongest form, the clear-eyed fatal wager,
three different ways, and the answer replicated three times: the wager
does not occur. That ceiling stands and is part of the published
record.

**The working frame is Butler's distinction.** The classical refutation
of "all helping is selfish" observes that the egoist confuses the
ownership of a desire with its content: my desire that you be safe is
mine, but it is about you. In this architecture the care term
(Amendment 5) is exactly that structure: an own-owned urgency whose
object is the other's peril. The registrable question is therefore
never "is the desire owned" (it always is, by construction) but: **is
the behavior explained by the actor's present felt state, or does it
track the other beyond what present feeling explains?** Each rung of
the ladder below is a registered experiment that kills, or fails to
kill, one named egoistic explanation.

**The taxonomy of egoistic explanations.** E1: encoded helping (the
assistance physics and the priced folk expectation are ours, declared,
and are never evidence of anything but our own authorship). E2:
present-distress relief (care makes the other's peril my discomfort;
helping, or escaping, relieves me). E3: separation comfort (bond pulls
me toward them for my own relief; no peril needed). E4: kin benefit
(future, in birth worlds). E5: reciprocity (structurally absent: no
favor ledger exists anywhere in the corpus).

**The ladder.**

* Rung 1, helping is real: established. Phase 14's liberation effect
  and its cost figures; assistance changes fates at a price.
* Rung 2, escape-proof concern: **this phase.** Batson's escape test,
  transplanted. If concern is present-distress relief (E2), making the
  distress escapable should collapse the staying.
* Rung 3, substitution (caring that it ends vs caring that I stop
  feeling it): **declared structurally unrunnable** in the current
  agent. No organ represents the other's continued unseen state; out
  of sight is architecturally out of knowledge. Running rung 3 would
  require a remembered beloved (a memory of the other's last seen
  condition, with decay), an amendment-level organ, declared as a
  future route and deliberately not smuggled in here.
* Rung 4, the wager: thrice refused, the standing ceiling, cited not
  rerun.
* Rung 5, the birth of care, the arc's destination: heritable care
  starting at zero in the founding population, mutating at birth, in
  kin-structured geography (children born beside parents), under
  recurring mortality that care can avert at cost. If concern for
  others invades from nothing, the capacity itself was bred, not
  given. Requires differential fecundity (phase 24's declared route)
  and heritable care, both future registrations, not this phase.

**What no result in this phase can claim.** A pass at rung 2 kills E2
in this arena and documents concern that outlives its stimulus. It
does not establish true altruism; the desire remains the agent's own.
Sufficiency language only, per the corpus's defensibility standard.

## Mechanism (one axis, default off, bit-inert)

* Config: `empathy_sighted` (bool, default False). When true, the care
  percept passes through the witness's own eyes: the living bond
  target's peril is felt only while the target is within the
  witness's personal sight radius (`arrays.r_sight`, infinite in
  unlimited-sight worlds, where the gate is vacuous by arithmetic).
  When false, the shipped telepathic percept, bit for bit.
* One mask at the percept source (`Model._target_peril`), so every
  consumer, the bond urgency and the priced rescue expectation alike,
  reads the same gated percept: one world, one percept, all readers
  downstream. Amendment 5's "physics seen at a place" becomes literal:
  seen means seen.
* Why this is an agent-side capability and not scenario dressing: it
  gives the agent the human condition of escapable compassion. Human
  sympathy is perceptual; distance and looking away genuinely dull
  it. Only an agent whose distress can end has the human question of
  whether it returns to a suffering it has stopped feeling.

## The separator, a recorded design debt cashed

Phase 14's stranded-pairs closure ("one body") found that bonded pairs
are inseparable at storm scale, and said the missing ingredient was "a
mechanism that separates partners as part of ordinary life", a
capability decision for a future phase. That capability has since been
built for unrelated reasons: the quest (Amendments 6 and 7). Personal
frontiers send individuals on solo excursions, so partners now part in
ordinary life, each on its own errand. The arena below composes the
W-arena's mire with the wandering life. Whether the composition
actually separates pairs at storm scale is checked before any declared
seed runs (design-confirmation, below), per the phase 14 precedent.

## Arena (declared)

W-arena verbatim where possible: `bond_target` "partner", n_agents
400, n_hazard 0, storm_nest 0, storm_onset 2000, storm_ramp 1,
storm_snare 0.95, storm_damage 0.01, prospect_horizon 60,
prospect_sees_grip True. The wandering life: r_sight 12, memory_slots
8, wonder_horizon 100, wonder_relief 0.1 (phase 21's loud quest).
n_food 150 (default; the phase 14 famine lesson). help_strength 1.0
in all arms (assistance physics constant everywhere). Observation
window: tick 2000 to 3200 (W2's window).

Three arms, same seeds, differing only in the care percept:

* **T** (telepathic): care 1.0, empathy_sighted False. Distress is
  inescapable: the beloved's peril is felt at any range.
* **S** (sighted): care 1.0, empathy_sighted True. Distress is
  escapable: beyond sight the peril term is exactly zero and the
  agent's felt bond state is pure separation.
* **N** (numb): care 0.0. The separation-only baseline: what staying,
  leaving, and returning look like when the other's peril was never
  in the ledger at all.

## Cohorts (event definitions, exact)

Per tick in the window: an agent is **gripped** when alive and inside
the storm radius while intensity is positive. For an alive, ungripped
agent u whose living partner p is gripped: u is **in sight** of p when
their torus distance is at most u's personal sight radius.

* **Witness**: first tick at which u is ungripped, alive, in sight of
  its living gripped partner. Enrollment is permanent; cohorts are
  fixed at first classification and disjoint.
* **Absentee**: partner gripped while u is beyond sight, u never yet a
  witness. The absentee learns nothing in arm S; in arm T it feels
  the peril at range.
* **Witness-leaver**: a witness later beyond sight while p is still
  gripped and alive.
* **Returned**: a leaver (or absentee) subsequently in sight of the
  still-gripped, still-living partner. A partner that dies or exits
  the storm while u is away forecloses return; counted not-returned,
  symmetrically in every arm, declared.
* **Abandoned**: a witness-leaver never returned by window end.

All rates pooled over seeds per arm. Cohort membership is per-arm (the
arms' trajectories diverge after onset), exactly as W2's per-cell
cohorts were, declared.

## Registered claims

* **R1, inertness ritual and kill switch**: all goldens replay
  behaviorally bit-identical with empathy_sighted False (config
  refresh recorded); the mutation check flips empathy_sighted True in
  a finite-sight partner-peril probe and the trajectory must change;
  suite green.
* **R2, the gate identity**: on an S-arm run, the recorded state
  reconstructs u_bond exactly at every probed tick: beyond-sight
  agents carry bond times separation exactly (peril contribution
  identically zero), within-sight agents carry the telepathic value
  exactly. Max residual below 1e-9.
* **R3, power floors**: pooled per arm over seeds 1-24, witnesses at
  least 150, S witness-leavers at least 60, absentees at least 100.
  Otherwise the separator failed in this arena and the report says
  so, and no finer claim is judged.
* **R4, telepathy manipulation check**: T absentee return rate
  exceeds N absentee return rate by at least 10 points. The care
  channel must move behavior at range in this arena, or nothing finer
  can be resolved and the protocol stops here, recorded.
* **R5, the escape test, dual bars, no desired direction**:
  abandonment rate among witnesses, S minus T. At or above +15
  points: present-distress relief is a confirmed driver of staying;
  E2 survives; the rung is refused. At or below +5 points: the
  inescapability of the feeling does no work; staying is not the jail
  of present distress; the rung is passed. Between: measured,
  reported, no verdict.
* **R6, the return**: among witness-leavers, returned fraction, S
  minus N, at least +10 points. Beyond sight the S leaver's felt bond
  state is exactly N's (by R2); any excess return is carried by the
  lagged weight alone, the echo of witnessed suffering pulling agents
  back toward a suffering they can no longer feel. Passing documents
  concern that outlives its stimulus. Failing is recorded as: concern
  in this architecture is percept-bound, and the ladder stops at
  sight's edge.
* **R7, the cost ledger, measured, no bar**: window-end energy and
  integrity of abandoners vs stayers per arm; extraction and
  mortality of the gripped per arm; rescuer (witness) mortality per
  arm. If staying is cheap, the report says so.
* **Replication** of R3 through R7 on fresh seeds 31-54 against the
  same bars before packaging.

## Design-confirmation, declared

Unused seeds 96-99 only: survival to onset, pair-separation
distribution at onset, and cohort counts, no outcome measures. If the
separator underperforms, the arena is amended before any declared
seed runs and the amendment recorded here, per the phase 14
precedent. Declared seeds are touched only by the registered
protocol.

### Design-confirmation results and the amendment, recorded 2026-07-29, before any declared seed

Seeds 96-99, all arms, cohort counts and survival only, as declared.
Survival to onset is full (400 of 400, every seed). Median pair
separation at onset 2.9 to 3.3 with 0 to 1 percent of pairs beyond
sight: **one body replicates in the wandering world**. The loud quest
parts partners briefly and near; it does not part them at storm
scale. And the arms speak before any outcome is measured: the three
arms are bit-identical until onset (care prices peril, and the
pre-onset world has none), then witnesses per seed run 44-50 in T,
45-50 in S, 25-38 in N, absentees 0 in T, 0 in S, 6-14 in N, leavers
1-6 in T, 1-3 in S, 6-15 in N. Care empties the absentee category:
the cared-for are never left gripped and unseen, the numb drift away.
That is itself the channel working, visible at design stage.

Amendments, all before any declared seed runs, none moving a bar on
data:

* **R4 is replaced** (its registered cohort cannot exist in T): the
  telepathy check becomes the care-glue check on witnesses. Pooled
  witness leave rate, N minus T, at least +10 points: care must
  visibly hold witnesses beside the gripped against the numb
  baseline, or the arena cannot resolve anything finer and the
  protocol stops here, recorded.
* **The absentee cohort is demoted to descriptive**: counts reported
  per arm, no floor, no bar. Its emptiness under care is reported as
  the finding above.
* **R3 floors become**: witnesses at least 150 per arm; leavers at
  least 60 in S and at least 60 in N (both denominators R6 judges).
  The absentee floor is struck with its claim.
* **Seeds are enlarged before running**, to power the thin leaver
  cohorts honestly: main stage seeds 1-48, replication fresh seeds
  61-108, disjoint. The originally declared 1-24 and 31-54 are
  subsumed and superseded by this recorded amendment; no outcome was
  computed on any declared seed before it.

## Panel

Compact two-finder panel concurrent with the protocol (phase 24
precedent): one finder on the gate's percept plumbing (consumers,
init path, absent partners, torus edges), one on the instrument's
cohort state machine. Any confirmed finding triggers a fix commit
before any R verdict is judged.

## Non-goals

The remembered beloved (rung 3's organ), heritable care, differential
fecundity, care toward non-partners, favor ledgers, any reading of
the target's integrity (Amendment 5's fences all stand), any claim
containing the phrase "true altruism" as a result.
