# Closing the container is not proof that the work is closed

**The rule.** An epic, a milestone, a sprint close by their own criteria; units of
work close by theirs. Completion is proved by **a count of unclosed units**, not
by the container looking empty.

## The incident

An audit document was moved to the archive when **all eleven** sub-epics of its
main epic had closed. Formally impeccable: the containers are empty, the tasks are
closed, the question looks settled.

A review returned to that audit a week and a half later and found **ten live
defects** listed as fixed — including one that reproduced in an ordinary run.

The cause is simple: closing a sub-epic meant work had passed through it, not that
**every finding** inside had received an outcome. Some findings were neither closed
with a change number nor rejected with a reason — they simply stopped being
mentioned.

The resulting rule: before archiving, check **by counter**. The number of findings
with no change number and no rejection mark must be **zero**.

## Why

A container closes on a signal that is easy to observe: no open children. A unit
of work closes on a signal that is harder to observe: it has an outcome. Between
those two signals fits everything that fell out along the way — reworded, split
into parts, lost in a move.

Second: **archiving closes the question**. Nobody returns to an archive, nobody
re-reads it, nobody plans from it. Getting it wrong at the moment of archiving
means burying live defects so that only a chance review will find them.

Third, generally: every transition to "the work is complete" needs a **countable
criterion**, not an evaluative one. "Everything is done" cannot be verified;
"units without an outcome: zero" is verified by one command and does not depend on
who is looking.

## In practice

- every unit of work has an explicit outcome: closed with a change number, or
  rejected with a reason; a unit that vanished silently counts as open;
- before archiving the counter runs **mandatorily**, not on suspicion;
- **different thresholds need not coincide** and are not confused: unblocking the
  next phase may require closing only the units affecting its subject, while
  archiving requires closing all of them, including those affecting nothing;
- closing a container does not move the document anywhere by itself: the move is a
  separate action with a separate condition.

## Where it applies

**Works** for audits, epics, milestones, checklist-based acceptance.

**Does not work** if the units are uncountable ("improve performance") — then a
countable subject is needed first.

**Sign of a breach:** a review of the closed finds the living.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/claude-handoff.md` § work outside the
tracker (the 2026-07-30 audit: ten live defects after archiving). Related:
[028](028-checklist-not-a-list-of-findings.md),
[108](108-a-living-document-keeps-a-fixed-window.md),
[116](116-the-collector-script-is-a-source-of-loss.md).
