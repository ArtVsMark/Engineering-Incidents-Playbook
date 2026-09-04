# A project's history keeps turning points, not the course of work

**Area.** documentation

**Tier.** 1 — rules and roles

**The rule.** What goes into the history is a decision that **turned the
direction**: the shape of the work changed, a flaw was found in the mechanism
itself, an outside signal redirected the plan, a stated plan was rolled back.
The entry must name the **rejected alternative** and what the turn became — as a
link to an artefact. Without an alternative it is not a decision but the course
of work, and its place is the changelog.

**Portable beyond Claude Code.** yes — the subject belongs to any project whose
history is of use to somebody, and has nothing to do with agent sessions.

## The incident

The history document **had no criterion for "when to write"**, and it collected
whatever came to mind: a change in the shape of records stood next to an
ordinary rule addition. A reader could not tell a turn from the course of work,
and the author decided anew on every pass — silently and differently each time.

The second case arrived from outside and confirmed the device: the grader keeps
its history as eleven releases, and its opening line promises not a list but
"why the decisions were made the way they were".

**The third case is this same rule being executed, and it is about taking a
device by halves.** From the neighbour we took the conclusion "history is
decisions" and invented our own form for it: a separate "## Turning point"
genre standing beside the row of releases. A week later the price was measured:
three releases, one release section, and the decisions of the other two lying
as separate entries tied to no release at all. The owner put it plainly: "this
is prose, not a history". A device is carried over whole or not at all — half a
device gives you your own genre with someone else's justification
([162](162-a-gap-asks-the-neighbours-first.md)). Neighbouring documents there
are separated explicitly — the changelog answers "what changed", an archive
holds old entries, the version policy is a third file. Two histories took shape
independently and arrived at the same place.

## Why

History and changelog answer different questions, and mixing them eats both. A
changelog answers "what changed" — it is complete by construction and read
selectively. A history answers "why it was decided this way" — it is useful
exactly to the degree everything else has been thrown out of it.

The selection criterion has to be **written down**, or it is replaced by the
author's memory: on a good day a trifle gets in, on a bad one a turn does not.
The sign that the criterion is broken is checkable by eye: the entry does not
let you see **which alternative was rejected**. If there was none, there was no
decision either.

The link to an artefact at the end is the same demand a rule's "Trace" makes: a
turn without it stays a story, and a story cannot be checked.

## In practice

- **the unit of history is a release**, not a stand-alone turning-point entry:
  the turn is told inside the release that carried it, otherwise releases and
  turns live as two rows and drift apart;
- four parts: context · what shipped (as links to artefacts) · decisions,
  including the rejected alternative · outcome;
- an unclosed release sits under its own heading and gets its number and date
  from the release itself, never by hand: renaming by hand is the same
  "don't forget" agreement on which the metrics row broke;
- a turn that changed the PROJECT's direction rather than its work is added
  **briefly to the opening narrative** — a paragraph, not a section: work
  changed goes into its release's decisions, intent changed goes to the front,
  where the history is read whole and first;
- an ordinary addition, a fixed link, a rebuild of derived files is **not** a
  turn — that is a changelog fragment;
- a living document has a limit expressed as a number: what falls outside the
  window moves to the archive **verbatim** rather than being shortened
  ([108](108-a-living-document-keeps-a-fixed-window.md));
- neighbouring documents are named in the header, or the reader looks for the
  changelog inside the history.

## Where it applies

**Works** for a project whose history is of use to somebody: a tool with users,
a catalogue, a library with external consumers.

**Does not work** for a project with no second reader: a history for oneself is
a diary, and demanding rejected alternatives in it demands ceremony. Nor for a
release changelog: there completeness matters more than selection, and a
turning-point criterion would throw out half of what is needed.

**Sign of violation:** an entry with no visible rejected alternative — either
there was none, or it is the course of work that landed in the wrong document.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#148

Related: [042](042-decision-records-its-alternatives.md) — how **one** decision
is written: context, alternatives, consequences; 161 answers the previous
question, which decisions enter the history at all;
[024](024-no-worklog-in-active-docs.md) — no worklog in a live document, the
other side of the same boundary; [030](030-changelog-from-fragments.md) — where
what is not a turn goes; [108](108-a-living-document-keeps-a-fixed-window.md) —
the limit of a living document and the verbatim move to the archive.
