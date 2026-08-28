# A decision is not edited after the fact — a new one supersedes it

**Area.** decisions

**The rule.** Changing a decision means a **new** record that marks the old one
superseded. The old one is not edited.

## The incident

The temptation is obvious: the decision is out of date, so it is easier to open
the old file and rewrite a couple of paragraphs. That way there is one document
and it is always "current".

The price shows up later. Code written under the old decision starts to look
like a mistake: the record says one thing, the code another, and whoever reads
them together cannot tell which one lagged. The history of the fork disappears:
why one option was chosen first and another later, and what exactly changed in
the conditions — nowhere.

## Why

A decision record is a **dated fact**, not a description of the current state.
The fact "in July we decided this for these reasons" does not stop being a fact
because September decided otherwise. Editing after the fact erases not obsolete
knowledge but **the reason for the transition** — the one thing the record
exists for.

Hence the chain of statuses: proposed → accepted or rejected → superseded by
record number such-and-such. The link runs both ways: the old one says what
replaced it, the new one says what it replaces and what changed.

The same principle separates a decision record from a specification. A
specification describes "how it is now" and is edited freely. A record describes
"why back then" and is never edited — except for its status.

## In practice

- in the old record **only the status line** changes, plus the link to the
  record that replaced it;
- the new record opens with **what changed in the conditions** — otherwise it is
  not a new decision but a change of mood;
- rejected records are not deleted: a refusal is a decision too;
- decisions are stored separately from descriptions of the current state, so
  that the two editing regimes do not get confused.

## Where it applies

**Works** for decision logs, minutes, dated reports.

**Does not work** for descriptions of current state — their whole duty is to be
rewritten.

**Sign of a breach:** the history of a decision file contains commits titled
"brought up to date".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/adr/README.md` § conventions.
Related: [024](024-no-worklog-in-active-docs.md),
[030](030-changelog-from-fragments.md) — what gets edited and what gets
appended.