# A rejected finding is recorded together with its reason

**Area.** audit

**The rule.** A finding deleted in silence will come back with the next review.
Rejection is as much a decision as a fix, and it needs a trace.

## The incident

An audit produced hundreds of findings. Some were dismissed as false positives
or as immaterial — and simply struck from the document.

The next audit found **the very same** places and raised them again. The
analysis went round a second time: the same discussions, the same arguments, the
same decision.

The cause is simple: the arguments for "this is not a defect" were never saved.
To a new reviewer the place looked untouched.

## The fix

Every finding has an explicit state, and there are **three** of them, not two:

- open;
- closed — with the number of the change;
- **rejected — with a reason**.

The third state is recorded in the same document, mandatorily. A rejected
finding is not deleted but marked: struck through, in a separate column, with a
flag — what matters is that it stays visible.

## Why

A rejection carries **knowledge**: why this looks like a defect and is not. That
is exactly what the next reviewer needs — and exactly what deletion destroys.

There is an accounting effect too: if rejected items disappear, the "closed N of
M" counter lies and progress looks better than it is.

A separate trap when automating: rejected items must be excluded from the review
queue **by an explicit marker**, not by "not being in the closed list".
Otherwise they resurface every cycle and the walk never converges.

## Where it applies

**Works** for audits, security reviews, static analysis, incident write-ups.

**Does not work** where the review is one-off and will never be repeated.

**Generalisation:** this is a special case of "the decision matters more than
the outcome". Recording "why not" saves as much time as recording "how yes".

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § a complex issue keeps a checklist
