# Findings and the order of work live in different documents

**The rule.** "What is wrong and where" and "what comes before what and why" are
two different questions and two different documents. One large audit produces
both, and they must not be mixed.

## The incident

The natural instinct is to keep one document: findings, with notes alongside on
what to do first. It sprawls predictably.

A finding lives a long time: it has a location in the code, a state and an
addressee. An order lives briefly: it holds until the first merge, after which
half the dependencies lose meaning. In a shared document the long-lived and the
short-lived mix, and updating it means updating all of it — that is, not
updating it.

The separation is simple. **Findings** — what is wrong, with an exact location
and an explicit state for each: open, closed with the number of the change,
rejected with a reason. **The queue** — order and dependencies: what hard-blocks
what, where the sequence is soft, where a precondition is already satisfied.

And the key point: the queue is written **only when the order is not obvious** —
there are hard blockers, a "do these together or the fix is unprovable", a shared
file. A flat list of independent tasks needs no queue and lives in the tracker.

## Why

The documents have different **lifetimes and different modes of editing**. A
finding is edited pointwise, one line at a time, and survives many changes. An
order is revised wholesale after every merge. A shared document inherits the
worst of both: edited wholesale, surviving little.

Second: what is valuable in the queue is exactly what is **absent** from the
tasks — the justification of the order. What breaks under a different sequence,
where the escape hatch is. Retelling the task body does not belong there: it is a
duplicate that will start diverging.

Third: a mixed document cannot be closed. Findings run out, the order is
exhausted, but from the shared document it is unclear what exactly finished.

## In practice

- the queue holds only the justification of order and the dependencies, without
  retelling tasks and without acceptance criteria;
- dependencies are marked distinguishably: a hard blocker and a soft sequence are
  not the same thing;
- no queue is created for a flat list: the absence of a queue is a normal state;
- a finding's state lives in **one** place; the register in the report is filled
  once, at archiving — two sources mean one of them is stale.

## Where it applies

**Works** after large audits and reviews that produce a coupled layer of tasks.

**Does not work** for small reviews: there the order is obvious and the document
is overhead.

**Sign of mixing:** the document can neither be closed nor updated partially.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § open work (an audit and a queue
are different things), `docs/agent/claude-handoff.md`. Related:
[028](028-checklist-not-a-list-of-findings.md),
[021](021-split-docs-by-reader.md).
