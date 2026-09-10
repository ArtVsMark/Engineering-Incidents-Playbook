# "Pre-release" is a claim about somebody else's calendar: it goes stale on its own

**Area.** CI, observation

**Tier.** 2 — the pipeline and CI

**The rule.** A marker meaning "this version is not released yet" is a claim
about **somebody else's calendar**: it stops being true because of an event in
another project, not because of an edit in yours. Such markers are checked
against a **live source** — the same one the tool takes the subject from — never
against memory or a calendar table of your own. The check is a **warning**, not a
rejection.

**Portable beyond Claude Code.** yes — the subject is a marker whose truth
depends on somebody else's event. The same holds for "beta", "deprecated since
version N", "supported until <date>", compatibility flags and dates in docs.

## The incident

A test matrix carried Python 3.14 behind an `experimental: true` flag (that is,
`continue-on-error`) from the time the version was pre-release — and **the flag
outlived its release**.

Measured on 9 September against the runner's manifest, the very one the runner
takes its interpreter from: **`3.14.7 stable=True`** — the seventh patch — while
`3.15.0-rc.2 stable=False`. For a whole release cycle, failures on a fully
supported version **did not block a merge**, and no run ever went red: the flag
did exactly what it said, and the version stopped being pre-release without a
single edit in the tree.

The price was measured the same day: change **#1522** reached the main branch
with one failing cell — 3.14 — and the reason stayed unknown, because the failure
summary looks at a job's conclusion and `continue-on-error` keeps it green.
**Both halves of the mechanism fell silent at once:** the failure neither stopped
the merge nor got explained.

A human found the mismatch, out loud, from memory of the calendar. None of the
project's fourteen gates had such a subject. And it was not only the matrix that
had gone stale: the same marker sat in prose across four documents, in the
package classifiers, and in three test docstrings.

## Why

**A marker about somebody else's state has no event that would make you re-read
it.** An ordinary note goes stale from an edit next to it: you change the code
and see the comment. Here there is nothing to change — a foreign release happens
without you, and not a line moves in your tree that day. The only chance to
notice is to remember.

**A tolerance flag hides its own staleness.** `continue-on-error` makes a failure
invisible **by design**, and in doing so removes the very signal that would have
revealed the staleness: the longer the flag stands needlessly, the less likely
anyone recalls it.

**A copy of somebody else's calendar diverges as silently as memory does.** The
temptation is to keep a "version → release date" table and check against it. That
is the same defect in new clothes: the table is also a claim about a foreign
thing, and it is updated by the same person who did not remember the flag.

**Why a warning rather than a rejection.** The event happened without you, and
the fix touches the list of required checks and branch protection — that is, it
does not fit into one change. Red that cannot be cleared by your own work trains
people to read red as background
([051](051-warn-on-likely-block-on-certain.md)), and then it fails to work where
the red is yours.

## In practice

- the source is **the same one** the tool takes the subject from: the runner's
  manifest, the package index, the image registry. A different source is a second
  claim about the same thing ([022](022-one-canonical-document.md));
- what is checked is the **flag's staleness, not its presence**: demanding a
  marker for every version would forbid the matrix from containing released ones;
- the subject is looked for **beyond the matrix**: the same marker lives in
  prose, in package classifiers, in docstrings — the count of places is named as
  a number;
- the source **could not be read** is a third outcome, not "clean"
  ([039](039-three-outcomes-not-two.md)): somebody else's unavailability does not
  make your marker true;
- a flag found redundant is **removed together with an analysis of what it hid**:
  a real failure nobody ever saw may be sitting underneath.

## Where it applies

**Works** for any marker whose truth depends on a foreign event: a pre-release
version, a beta channel, "deprecated since N", a support deadline.

**Does not work** for markers about **your own** state: "this test is flaky for
us", "this step is temporary until our migration". There the event is yours and
there is someone to notice it — a different rule's subject.

**Does not work** where no machine-readable foreign source exists at all: there
is then nothing to check against, and the honest answer is to say so rather than
start a calendar table of your own.

**Sign of violation:** the tree carries a tolerance flag for a version, and the
answer to "when will it stop being needed" is "when we remember".

## Trace

ArtVsMark/Stepik-Python-Grader#1529
ArtVsMark/Stepik-Python-Grader — `scripts/check_experimental_python.py`

Related: [049](049-derive-state-from-live-artifacts.md) — state is derived from
a live artefact; here the artefact is somebody else's, and that is the whole
difference; [192](192-changing-the-actor-invalidates-the-measurement.md) — a
measurement is invalidated by a change of actor, and here by a foreign release:
both are claims that stopped being true without an edit of yours;
[051](051-warn-on-likely-block-on-certain.md) — block on the certain, warn on the
likely; hence a warning rather than a rejection.
