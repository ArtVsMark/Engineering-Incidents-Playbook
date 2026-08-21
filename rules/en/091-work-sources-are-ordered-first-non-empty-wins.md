# Work sources are ordered: the first non-empty one is the plan

**The rule.** The list of places to look for what to do is defined by an order.
You go top to bottom; the first non-empty source is the plan. Statuses live
**only** in the tracker and are not duplicated into files.

## The incident

While there was no order, the question "what do I work on" was settled afresh
every time, and the answer depended on which document was opened first.

Duplicated statuses turned out worse. A section of the project's rulebook listed
open tasks — and **spent years listing two long-closed ones as open**. The
handover document carried **seven closed tasks** as current. Both lists looked
authoritative: neat, numbered, in the right place.

The order that removed this:

1. **the tracker** — the only source of statuses;
2. **findings from unclosed audits**, if the directory is non-empty — what
   exactly is wrong and where;
3. **the work queue**, if it is non-empty — order and dependencies for one layer
   of tasks;
4. **the changelog** — what is already done, so as not to reinvent it.

## Why

A duplicated status list does not merely go stale — it goes **stale invisibly**.
A task is closed in the tracker with one gesture, and the line in the document
remains: nobody deletes it, because deletion is part of nobody's ritual. Six
months later the document lies confidently, and it lies to the newcomer, who has
no experience of distrusting it.

The order of sources solves a different problem — it **removes the choice**.
While "where to look" is decided each time, the most visible document wins rather
than the most current. The rule "first non-empty" turns a question into a check.

The key condition: for every source in the list **emptiness is a legitimate
state**, and it is declared explicitly. Otherwise an empty directory reads as
"broken" and the order breaks at the first step.

## In practice

- statuses are copied nowhere: not into the rulebook, not into the handover
  document, not into a report — links only;
- every source states **what exactly** it provides: findings, order, history —
  otherwise they start overlapping;
- an empty source is normal, and that is said plainly, with a date;
- the order is fixed and shared: two different orders amount to no order at all.

## Where it applies

**Works** when there is more than one source of work and they differ in nature.

**Does not work** with a single tracker — there the order degenerates.

**Sign of trouble:** a document lists tasks and some of them have long been
closed.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § open work (closed #97/#151 listed
as open; seven closed tasks in the handover). Related:
[049](049-derive-state-from-live-artifacts.md),
[027](027-empty-state-is-a-state.md).
