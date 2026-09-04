# File overlap sets the boundary of a change, not the number of tasks

**Area.** pipeline, planning

**Tier.** 2 — the pipeline and CI

**The rule.** The boundary of one change is set by **file overlap**, not by the
number of tasks. Tasks editing the same file travel together; tasks that do not
overlap travel apart. "One task, one change" is a formal criterion, and it fails
exactly where the file is shared.

## The incident

One change carried **five tasks** at once: the name of a working session,
recording rules into the shared catalogue, role coverage, the index generator,
and the authorship check. By the habitual criterion this is a gross violation:
five tasks, so five changes.

Except that all five edited **the same project charter**. Split across five
branches they would have collided on it — not "possibly" but certainly, because
each appends its own section to one file.

The cost of a conflict in this pipeline has already been measured, and it is not
merely a manual merge: **a conflicted change gets no checks at all** — the run
happens on a merge commit that does not exist while there is a conflict, and an
empty list of checks reads as "the pipeline broke"
([010](010-empty-checklist-is-not-green.md)). Plus the queue: five changes
instead of one means five full runs and five queue turns where one was enough.

The converse was measured on the same project: of the last sixteen merges,
**fourteen carried exactly one task**. The norm holds, and what breaks it is not
laziness but the shared file.

## Why

**Splitting does not restore revertability when the edits share a file.** The
main argument for small changes is "one thing broke, revert one thing". But
reverting an edit in a shared file drags the neighbouring lines anyway: five
changes into one file revert as badly as one combined change. The very argument
for splitting does not apply here — while its costs remain.

**A conflict is cheaper to prevent than to resolve.** In itself it is normal
traffic ([004](004-conflict-is-normal-not-outage.md)), but it costs checks, a
queue turn and the branch owner's attention. If two tasks will certainly meet on
one file, meeting them **inside one branch** is the cheap way: one person, one
merge, the full context of both.

**A formal criterion does not set the unit.** The same conclusion as in
[098](098-the-unit-of-splitting-follows-usage.md), only the subject here is a
change rather than data. The unit is set by how it moves through the pipeline:
file overlap, the order of checks, the cost of a run.

## The boundary with "one topic"

Rule [132](132-one-change-carries-one-topic.md) demands one topic; this one
allows five tasks in a single change. There is no contradiction, because the
criteria are of different orders.

**The ceiling on tasks is soft, the ceiling on zones is hard.** Five edits to one
charter are one topic with five occasions. Five edits to five subsystems "because
it was convenient" are five topics, and they travel apart even if the task is
formally one.

Check in this order: zones first (132), then file overlap within a zone (133).
Different layers — split. One file — travel together.

**A third way, when the topics differ but the file is shared:** stack the
branches, one on top of another. Then each has its own topic and there is no
conflict, because they edit the shared file in turn rather than in parallel.

## In practice

- **the criterion is checkable: the files overlap**. "While I was at it" is
  convenience, not overlap; such a task leaves in its own change;
- **a combined change declares ALL of its tasks**, or the tracker lies
  ([128](128-a-required-field-is-checked-for-completeness.md));
- **the risk is named in the description**: a combined change reverts as a whole,
  and that is stated where the tasks are listed;
- **the shared file first, the rest after**: if the tasks meet only in part of the
  work, the shared file goes as one change and the independent parts as their own.

## Where it applies

**Works** wherever branches live in parallel and a conflict costs checks — that
is, in any pipeline with required checks on merge.

**Does not work** for short branches merged the same day: the chance of meeting
is small and splitting costs nothing.

**Sign you need it:** changes keep sitting in conflict over the same shared file
— a charter, a journal, a registry — each waiting its turn to be resolved.

## Trace

ArtVsMark/Stepik-Python-Grader#1345 (five tasks, one charter),
ArtVsMark/Stepik-Python-Grader#1350 (the completeness gate); measurement: 14 of
the last 16 merges carried exactly one task. See also:
[132](132-one-change-carries-one-topic.md) — the criterion checked first,
[098](098-the-unit-of-splitting-follows-usage.md),
[004](004-conflict-is-normal-not-outage.md),
[010](010-empty-checklist-is-not-green.md),
[030](030-changelog-from-fragments.md).