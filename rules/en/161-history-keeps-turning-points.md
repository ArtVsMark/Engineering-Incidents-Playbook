# A project's history keeps turning points, not the course of work

**Area.** documentation

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
"why the decisions were made the way they were". Neighbouring documents there
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

- four parts: what started it · what else was considered and why rejected ·
  what was chosen · what it became (as a link);
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

ArtVsMark/claude-code-playbook#148

Related: [042](042-decision-records-its-alternatives.md) — how **one** decision
is written: context, alternatives, consequences; 161 answers the previous
question, which decisions enter the history at all;
[024](024-no-worklog-in-active-docs.md) — no worklog in a live document, the
other side of the same boundary; [030](030-changelog-from-fragments.md) — where
what is not a turn goes; [108](108-a-living-document-keeps-a-fixed-window.md) —
the limit of a living document and the verbatim move to the archive.
