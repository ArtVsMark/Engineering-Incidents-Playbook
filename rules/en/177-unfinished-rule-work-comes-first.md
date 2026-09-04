# Unfinished rule work comes before new work

**Area.** catalogue

**Tier.** 1 — rules and roles

**The rule.** While a project has unfinished rule work, it does not start new
work. Unfinished means three things, and any one is enough: a rule with no
answer or answered `unreviewed`; a rule declared active and backed by
**nothing**; a catalogue contract that moved and whose answers have not been
re-read. The mechanism prints those three numbers as the first thing the project
sees — **before** the list of new rules, not after.

**Portable beyond Claude Code.** yes — the subject is not agent windows but the
discipline of working through a rulebook; a team with no agents at all can own
one.

## The incident

The owner of four connected projects, 3 September: "the grader has not worked
through all the rules and keeps working on other issues, when rules should come
first — and I have to remind every project about this. I do it constantly."

Measurement from the same day's summary: rules declared **active and backed by
nothing** — 47 across three of the four projects. `Claude-Code_Usage-Token` 20,
`ArtVsMark` 15, the catalogue itself 12. This is not "haven't got to it yet":
an answer exists, the status says `active`, and there is no mechanism — the rule
is declared in force and is not in force.

**What was tried first.** Ordering: rules got an adoption tier, and the
consumer's inbox queue started following it. It failed for two reasons at once.
First, the guard looked only at open issues whose title names a rule number —
and the "backed by nothing" debt does not live in issues; the grader has no such
issues at all. Second, and worse: ordering answers "what to take first", while
the incident was about something else — "whether to take anything new while the
old is unfinished". The first guard existed, ran, and guarded nothing.

## Why

Working through rules competes with product work for the same attention, and
always loses, for one reason: product work has a customer and rule work does
not. A rule left without a mechanism breaks nothing today; a task left
unattended breaks something. Hence a stable drift: the work is deferred by the
absence of a decision, not by a decision.

A human reminder does not remove that asymmetry — it hides it. While the owner
keeps repeating, the discipline holds and looks like it works. Stop repeating
for a week and the debt is visible nowhere, because "active but backed by
nothing" is a **green** state in every report. Knowledge in someone's head is
not a mechanism ([002](002-rule-without-mechanism.md)), and the cost here is not
forgetfulness: the person doing the reminding becomes the single point of
failure.

**Asymmetry of cost.** A guard that fires needlessly costs one glance: the
person reads three numbers and moves on. A guard that fails to fire costs months
of accumulation — twenty rules without mechanisms are twenty breakages the
project believes it is protected from.

## In practice

- the three numbers print **always**, not only when non-zero: "no answer 0 ·
  unreviewed 0 · backed by nothing 0" is a state, not emptiness
  ([027](027-empty-state-is-a-state.md));
- a moved contract counts as unfinished work like the rest: by
  [157](157-a-contract-version-bump-is-a-re-read.md) a version change is a reason to
  **re-read the answers**, not merely to adjust the format;
- the guard **names**, it does not forbid: a mechanism cannot stop someone
  else's work and does not pretend it can. It puts the numbers where they cannot
  be missed and says plainly that the list of new rules below is a queue, not
  work;
- closing the task stays with a person: it says "I looked", and a mechanism
  cannot say that;
- revisit the decision if the "backed by nothing" debt stops shrinking while the
  guard works: then the subject is not visibility but the absence of any
  mechanism the project will ever have — and the honest answer is
  "not applicable", not silence.

## Where it applies

**Works** where rules arrive from outside and compete with the project's own
work: a catalogue with several consumers, a shared rulebook across a team, an
external standard adopted for execution.

**Does not work** when the rules and the work are the same thing: a project
whose product *is* the rulebook has no state called "deferring rule work for
tasks". Nor where the only consumer is also the author: the guard shows them
their own debt, which they already see, and becomes decoration.

**Does not work as a prohibition.** A project that deliberately defers is not
stopped by this mechanism — and should not be: deferral has reasons the
catalogue does not know. The rule demands that the deferral be a **decision**
rather than a consequence of invisibility.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#326
