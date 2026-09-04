# An exclusive claim binds the document, not the section

**Area.** documentation, process

**Tier.** 1 — rules and roles

**The rule.** A claim of the form "X is read **only** from here", "the single
source of Y is Z" binds the **whole document**, not the section it is written
in. So it is written not when it is true on its own plane, but when the document
holds no **other** exclusive claim about the same subject. Two such claims do not
refine each other: each forbids the other, and both stop working — the reader
obeys whichever one they read last. They must be found by enumerating over the
subject, not by reading through.

**Portable beyond Claude Code.** yes — the subject belongs to any normative
document written in more than one pass: an agent rulebook, a contributor guide,
a specification, an on-call runbook.

## The incident

`Stepik-Python-Grader`, a 1245-line `CLAUDE.md`. Two instructions about one
subject — where the state of a finding lives:

> **line 845.** "State lives **only in the issue itself**: the registry in the
> audit document is filled in **once, at archiving** — two sources mean one of
> them is stale."

> **line 1013.** "Closed a finding — write it into the registry **in the same
> pass**. The state of a finding is read **only from there** ('open until the ID
> is in the registry')."

The divergence is exact and along two axes at once: **where** the state lives —
in the issue or in the registry — and **when** the registry is written — at
archiving or on every closure. Both claims are exclusive, about one subject, and
name different holders.

**Both were derived from the same correct principle** — "two sources mean one is
stale". Each is flawless on its own plane: the section about the issue checklist
concluded that the issue is canonical; the section about the audit document
concluded that the registry is.

**Both have machinery.** Line 848 names `check_issue_checklists.py`, line 1017
names `check_audit_registry.py`. Two gates enforce two contradictory
requirements, and each is green on its own plane.

**The cost is counted in the same file, lines 1015–1018:** "one audit drifted by
**152 records** — 57 in the registry against 209 closed". The registry lagged
precisely because a neighbouring section said to fill it once, at archiving.

The distance between the two instructions is **168 lines**.

## Why

The word "only" is a claim about the **whole document**, yet it is written inside
a section where the author is thinking about one plane. Hence the mechanism of
the failure: each pass is locally correct, the contradiction arises **between**
passes, and so no single author sees it. The author of the second section is
answering a different question — "how do we keep the audit document honest?" —
and answering it correctly.

It is exclusivity that turns two correct answers into one wrong one. Without
"only" the two claims are compatible: state lives in the issue, and the registry
mirrors it. With "only" each declares the other an error.

**The asymmetry of price.** A non-exclusive claim, if redundant, adds work. An
exclusive one, if wrong, **devalues the neighbouring mechanism**: a reader
following it breaks what was working. And it breaks silently — both sides are
green, because each gate checks its own plane and knows nothing of the other.

**Why by enumeration, not by reading.** Sections are written at different times
in different passes; the author of the second does not remember the first, and
nobody re-reads a 1245-line document before every edit. So the question is asked
by a machine — not deciding who is right, but showing the pair.

## Practical boundaries

- before writing "only", "the single source", "read solely from here" —
  enumerate **every** exclusive claim in the document about the same subject;
- easy to miss that both claims **may each have their own gate** and both be
  green: this class of divergence is invisible to machinery of that kind;
- easy to miss that the closeness here is **in subject, not in wording**: the
  pair is found through shared subject vocabulary, not through similar phrasing;
- revisit the decision when the subjects really are **different** and merely
  share vocabulary — the state of a *finding* versus the state of an *issue*.
  Then the fix is not the exclusivity but the name of the subject: make it
  precise.

## Where it applies

**Works** for a normative document written in more than one pass: an agent
rulebook, a contributor guide, a specification, an on-call runbook.

**Does not work** for descriptive text: "the file is read only by the showcase
job" is a claim about a fact — it is verified, not obeyed. Nor does it work for a
single-section document: there is no second plane there by construction.

**Sign of violation:** two sentences in one document, each carrying "only" about
the same subject, naming different holders — and both sections correct when read
apart.

## Trace

`ArtVsMark/Stepik-Python-Grader` — `CLAUDE.md`, lines 845–846 and 1013–1014, the
cost counted in the same file at lines 1015–1018; verified against HEAD
`dbbbd47` on 4 September. In the catalogue — `scripts/check_exclusive.py`.

Related: [022](022-one-canonical-document.md) — adjacent and NOT the same: there
a topic spreads across two documents, here the document is one and the planes are
several, which a canonical document does not cure.
[125](125-a-generated-file-is-not-a-store.md) — the same principle "two sources
mean one is stale" from which both contradicting instructions were derived.
[146](146-a-green-gate-does-not-verify-its-premise.md) — why both gates being
green said nothing.
