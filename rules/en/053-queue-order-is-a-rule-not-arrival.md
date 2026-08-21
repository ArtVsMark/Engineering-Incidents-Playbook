# Queue order is set by a rule, not by who went green first

**Area.** pipeline

**The rule.** The merge queue is ordered by **importance**, not by who turned
green earliest. What fixes a shared breakage goes first; while the shared branch
is red, nothing else moves at all.

## The incident

A queue ordered by readiness looks fair and produces two failures at once.

**First: the fix sits at the back.** A change that repairs a broken shared
branch joins the queue on equal terms — behind everyone who went green earlier.
But while the shared branch is red, every check in the queue runs on a knowingly
broken base: the results mean nothing, and the executors are busy.

**Second: the owner's priority has no way to express itself.** Somebody says
"this one first" — the machinery does not know that and carries on by readiness.
The words were said, the order did not change, and the divergence is discovered
when the important thing has already gone through third.

Hence an order in which importance is expressed by a **label** rather than in
conversation: what fixes a red shared branch → what is marked blocking → changes
touching a shared file → the rest by readiness. Plus a separate stop label:
while it is on, there is no auto-merge no matter how green things are.

## Why

A queue is machinery, and machinery reads **markers**, not intentions. Anything
living only in someone's head or in correspondence does not exist for it. So
priority must either be expressed as a marker the queue can read, or admitted
not to exist.

A red shared branch is a special case, and it is not "one more high priority"
but a **freeze**. The difference is practical: high priority moves one item
forward, a freeze stops everyone. While the base is broken, a green check does
not mean the thing works — it means the broken thing did not get worse.

Third: expressed priority has a price and that price must be visible. A "first"
label on everything restores ordering by readiness with an extra step.

## In practice

- the priority marker is **a label on the change**, and applying it is
  mandatory: a queue that reads labels will silently fall back to readiness order
  when they are absent;
- a red shared branch is checked **before** choosing the head, not after: it is a
  condition of entry to the queue, not one of the sorts;
- the stop label outranks any priority: it means "the owner merges this by
  hand";
- what fixes a shared breakage usually **cannot be derived** from queue state —
  the machinery does not know what repairs the redness. Then the queue says so
  on a separate line and leaves the decision to a human: lying by sorting is
  worse than admitting a gap;
- the order is printed on request together with the reason for each position —
  otherwise you can only argue with the queue in words.

## Where it applies

**Works** for pipelines where merges land one at a time and external importance
exists: deadlines, a release, a breakage.

**Does not work** where all changes are equivalent: sorting adds rules and
changes nothing.

**Sign of trouble:** priority is communicated by voice and the queue does not
reflect it.

## Trace

ArtVsMark/Stepik-Python-Grader#1325, #1326, #1329.
Related: [052](052-only-the-head-of-the-queue-moves.md),
[004](004-conflict-is-normal-not-outage.md),
[002](002-rule-without-mechanism.md).
