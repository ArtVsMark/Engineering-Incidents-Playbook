# A project publishes the facts about itself; a neighbour does not compute them

**Area.** contracts, metrics

**Tier.** 1 — rules and roles

**The rule.** A number describing a project's **structure** — how many tests it
has, which versions it builds on, how many checks a change creates — is
published by that project as a machine-readable file, and the consumer reads it.
Computing such a number from outside means keeping a copy of someone else's
definition: where the tests live, what their directory is called, how the matrix
is arranged. The copy holds until the first edit on the other side and then
drifts **silently** — both numbers stay plausible, and nothing tells them apart.

**Portable beyond Claude Code.** yes — the subject belongs to any
publisher/consumer pair: a showcase, a report, a dashboard, an aggregator of
other people's metrics.

## The incident

A profile showcase displayed five of the grader's numbers, and three of them
required knowing its structure: it cloned the repository **in full** for two
counts over `tests/` and parsed the neighbour's `ci.yml` with a regular
expression for the experimental Python versions. The fourth — how many checks a
change creates — was estimated as the median over the last seven merged changes,
and not out of laziness: from outside, the exact answer is not visible.

**Measured at the switch to the publisher's answer:** the median gave 19, the
exact set **16**. So the showcase claimed something measured where it was
estimating, overstating by a fifth. Test modules: 246 against 247 — the clone
was hours behind the other side's main branch.

The first fix was obvious and wrong: count more precisely — refine the sample,
take the mode instead of the median, widen the window. All of that refines an
**estimate**, while the publisher already holds the **answer**: it counts that
very set of checks for its own merge gate.

## Why

The mechanism of failure is not imprecision but **direction**. Computing
someone else's number at home means holding a copy of their definition, and that
copy is protected by nothing: it does not break when it drifts — it quietly
starts answering a different question.

Hence the asymmetry that settles it. A source failure is visible: the file did
not parse, the key is missing, the timestamp is stale; it is fixed in a minute.
A drifted definition is seen by **nobody** — not a gate, not a reader, not the
author — because both answers look plausible.

The shape of the answer follows from the same logic rather than from taste:

- the file lives **off the main branch**: it is rebuilt more often than changes
  land ([160](160-derived-artifacts-live-off-the-branch.md));
- it carries a **format** version, and that version says what it versions
  ([164](164-a-version-says-what-it-versions.md));
- **a missing key means "not measured"**: a zero would read as the answer "no
  checks are created";
- a timestamp is mandatory, and where possible what the number was derived
  from: without them freshness cannot be told from staleness
  ([046](046-name-the-gaps-do-not-level-them.md)).

## In practice

- the publisher is whoever already has the answer: usually the same count the
  project performs for its own gate;
- the consumer reads and does **not** recompute: two implementations of one
  count will drift ([090](090-shared-helpers-move-up-not-sideways.md));
- a project with nothing to measure gets no such file: an empty answer is worse
  than a missing one — it looks like measured absence;
- a source failure is told apart from a clean result explicitly and names its
  subject ([039](039-three-outcomes-not-two.md),
  [158](158-the-third-outcome-names-its-subject.md)).

## Where it applies

**Works** for numbers describing structure: the test set, the matrix, the
checks, the versions, the size of an export.

**Does not work** for numbers a publisher cannot know about itself: how many
consumers read it, how fast its server answers from outside, how many people
reached the second page. There the observer measures, and their number is the
only one. Nor does it work where the publisher is out of reach: a private
repository, another organisation — there an outside estimate is honest, provided
it is named an estimate.

**Sign of violation:** a consumer clones someone else's repository in order to
count something in it.

## Trace

ArtVsMark/Stepik-Python-Grader#1411 — the publisher began publishing facts about
itself; ArtVsMark/ArtVsMark#120 — the consumer stopped computing them

Related: [129](129-a-catalogue-needs-a-consumption-contract.md) — a catalogue
needs a consumption contract; 174 generalises it beyond rules: any facts about
oneself are shipped the same way.
[164](164-a-version-says-what-it-versions.md) — a version says what it versions;
in a facts file that is the format's version.
[160](160-derived-artifacts-live-off-the-branch.md) — a derived artifact
rebuilt more often than changes land lives off the branch.
[046](046-name-the-gaps-do-not-level-them.md) — a frozen indicator is
indistinguishable from an honest one, hence the timestamp.
