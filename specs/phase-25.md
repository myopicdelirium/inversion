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

### Panel results, the voided first run, and the second amendment, recorded 2026-07-29

Two finders, zero stalls, both reported in full before any verdict
was judged. The gate finder confirmed the mechanism clean in all four
registered classes (sole producer, all consumers gated, torus and
edge semantics exact, bit-inertness verified by a cross-commit
module-swap probe on three care worlds the goldens do not cover),
with one confirmed minor that scopes two of this spec's sentences:
under prospect_sees_grip the phase 13 grip percept is ungated, so a
sighted agent still prices the storm's depth at its partner's
location through the SAFETY channel at unlimited range. That percept
is identical across all three arms and independent of care and of
the gate, so no bar or arm comparison is touched, but "seen means
seen" and "the absentee learns nothing in arm S" hold for the CARE
channel only, and are so scoped. Telepathic navigation (distance and
direction to the partner) is likewise ungated: that is the shipped
bond percept, and it is what makes return possible at all.

The instrument finder confirmed four majors, all mine, all fixed
before any verdict was judged, and **both protocol stages already
run are VOID by instrument defect** (their artifacts were
overwritten by the corrected instrument's reruns; the voided numbers
survive in git history at commit f0fdd76 and are not quoted here so
no eye falls on unjudgeable rates):

* Dead witnesses were latched as leavers and abandoners: a witness
  that died at its post beside the gripped beloved became a
  "deserter" when the partner later drifted from the corpse.
  Construct inversion, arm-asymmetric (care arms hold witnesses
  where the dying is), poisoning R4 and R5. Fixed: every transition
  now requires a living u.
* The registered foreclosure censor was never implemented: a partner
  extracted while u was away and re-gripped later could yield a
  counted "return" the registration forecloses. Fixed: the censor
  latches per the registered sentence, and foreclosed counts are
  reported.
* The R2 probe was a tautology: it reconstructed the expected
  urgency THROUGH the gate under test, and the finder proved a
  deliberately broken gate still passed it. Fixed: the
  reconstruction is now independent (production physics, the gate
  rebuilt from raw arrays, never Model._target_peril).
* The first amendment's replication range 61-108 contained the four
  design-confirmation seeds 96-99, whose cohort counts were peeked.
  My registration error. **Second amendment, before any judged
  verdict: the replication range becomes fresh seeds 109-156**,
  disjoint from every seed any eye has touched.

Minors, fixed in the same pass: a witness gripped inside the storm
can no longer be marked a leaver (entering the storm is not
desertion); R5 through R7 are computed but marked unjudged whenever
R3 or R4 fails (the registration's "no finer claim is judged", now
enforced in the artifact itself); the artifact manifest now hashes
the arena config it actually ran plus per-arm hashes; the cost
ledger's means are over living agents only; the design-mode wording
no longer overclaims; the onset separation stat reads cfg.r_sight.
Declared limitation, recorded not fixed: post-step sampling cannot
see a one-tick storm transit (about one per four cells, undercounts
only, arm-symmetric).

## Results, recorded 2026-07-29: the rung is passed, and the echo is real

Artifacts: `results/phase-25-escape.json` (seeds 1-48),
`phase-25-escape-replication.json` (fresh seeds 109-156), measured by
the panel-corrected instrument, judged after the panel per the
registered sequencing. Every claim replicated.

* **R1 PASSED**: 25 goldens behaviorally bit-identical before the
  config refresh; the kill switch kills where it must bite and is
  vacuous under an infinite eye; suite green at 99.
* **R2 PASSED, both stages**: max residual exactly 0.0 against the
  independent reconstruction (production physics, the gate rebuilt
  from raw arrays, never the function under test).
* **R3 PASSED, both stages**: witnesses 2296/2208/1529 (T/S/N), then
  2211/2331/1557, floors 150; leavers 111/108/530, then 101/111/577,
  floors 60 in S and N.
* **R4 PASSED, both stages, the care-glue check**: witness leave
  rate N 34.7 vs T 4.8 percent (+29.8 points, bar +10); replication
  N 37.1 vs T 4.6 (+32.5). Care holds witnesses beside the gripped
  at seven times the numb baseline's grip. The descriptive absentee
  counts say the same thing from the other side: 3/7/407, then
  3/5/472 (T/S/N): care all but empties the category of the beloved
  gripped unseen.
* **R5 PASSED, both stages: the rung is passed at Batson's own
  test.** Abandonment among witnesses, S minus T: +0.6 points in
  both stages (S 1.1 vs T 0.6; S 1.3 vs T 0.8 percent), against a
  pass bar of +5 and a refuse bar of +15. Agents whose compassion
  genuinely switches off when they walk beyond sight (the escape is
  real and relieving, R2) do not walk away more than agents whose
  compassion follows them everywhere. In this arena, staying is not
  the jail of present distress: E2, the aversive-arousal account of
  helping, is dead here. Numb abandonment runs 15.2 and 16.5
  percent: an order of magnitude above either care arm.
* **R6 PASSED, both stages: the return.** Leaver return, S minus N:
  +20.6 points (76.9 vs 56.2 percent) and +16.6 (72.1 vs 55.5), bar
  +10. Beyond sight the S leaver's felt state is exactly the numb
  leaver's (R2's identity: pure separation), yet it turns around for
  the gripped beloved far more often. The excess is carried by the
  lagged weight alone: the echo of witnessed suffering, the one
  law's own memory trace. No rule prices it, no rule says remember;
  the lag is the fidelity. The full ordering is T 88.3/83.2 above S
  76.9/72.1 above N 56.2/55.5: telepathy above echo above
  separation, exactly the informational gradient the arms built.
* **R7, the cost ledger, measured**: witnesses die at 44 to 51
  percent in every arm (the mire's edge is a killing floor), and the
  care arms pay MORE: witness mortality T 48.4/47.1 and S 50.6/48.2
  vs N 44.3/46.3 percent. What the payment buys: gripped extraction
  T 47.0/47.3 and S 44.6/46.4 vs N 38.2/36.6 percent; gripped
  mortality T 51.0/51.3 and S 54.3/52.2 vs N 59.5/60.5. Care
  transfers survival from the witness to the gripped. Helping is
  costly here, and the cost is paid overwhelmingly by those who
  stay.
* **The instrument lesson, recorded beside phase 24's**: the voided
  first run had R6 FAILING with an inverted sign, entirely by
  instrument defect: corpses counted as deserters and foreclosed
  episodes counted as returns. A false refutation of the phase's
  most delicate claim was one unread panel report away from the
  record. The dead cannot desert; the instrument must know it.

**What is claimed, and what is not.** Sufficiency language only: in
this arena, with this agent, escapable compassion produces no extra
abandonment (rung 2 passed, E2 killed), and concern demonstrably
outlives its stimulus through the lag law's echo (the return). Not
claimed: true altruism, selflessness, or any motive beyond the
agent's own ledger; the desire remains owned, its object remains the
other, which is Butler's point and the most this architecture can
say. Rung 3 stays declared unrunnable (no organ holds the unseen
other), rung 4 stays thrice-refused, and rung 5, the birth of care,
is the arc's registered destination.

## Non-goals

The remembered beloved (rung 3's organ), heritable care, differential
fecundity, care toward non-partners, favor ledgers, any reading of
the target's integrity (Amendment 5's fences all stand), any claim
containing the phrase "true altruism" as a result.
