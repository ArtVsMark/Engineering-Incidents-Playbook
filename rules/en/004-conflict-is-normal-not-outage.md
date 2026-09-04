# A conflict is normal pipeline traffic, not an outage

**Area.** pipeline, automation

**Tier.** 2 — the pipeline and CI

**The rule.** Machinery that meets a predictable obstacle must skip the item,
mark it, and carry on. Failing outright is a defect in the machinery.

## The incident

The workflow that advances the head of the merge queue failed three times in a
row and held the queue for **fourteen hours**:

```
03:29  failure
21:08  failure
17:11  failure   ← first failure
16:23  success   (the queue was empty)
```

Each time on the branch-update step. The head of the queue had gone `dirty`: a
conflict with the main branch. The update call returned an error, and the whole
run collapsed.

Behind it stood **four healthy pull requests** — all green, all merely behind.
Not one moved. Two had auto-merge enabled: they were not merging precisely
because they were behind, and nobody was left to bring them forward.

## Why

A conflict arises whenever two changes touch the same file. That is the normal
course of work, not an infrastructure failure.

Machinery that halts on it stops being a safety net and becomes the **single
point of failure**: one awkward branch blocks everyone.

The second layer of the mistake is silence. When the failure was patched with a
plain "do not fail", the conflicting pull request began to be passed over
**without any trace at all**: it was skipped forever, and the only way to learn
that was to look. A skip must leave a label or a comment.

## Where it applies

**Works** for any automation walking a set of items: merge queues, batch
processors, scheduled sweeps.

The generalisation: **a failure on one item must not end the walk over the
rest** — log it, mark it, move on. The run finishes successfully if the set was
processed, even when part of it was skipped. A red run here means "the
machinery is broken", not "somebody has a conflict".

**Does not work** when items are coupled: if skipping one makes processing the
next meaningless, stopping is correct. Example — a red main branch: while it is
broken, updating the other branches serves no purpose.

## Trace

ArtVsMark/Stepik-Python-Grader#1313