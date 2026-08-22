# One change carries one topic: a combined one is honest but unreviewable

**Area.** process, pipeline

**The rule.** One change, one topic. A combined change can be made **honest** by
declaring every task it closes, but it cannot be made **reviewable**: it cannot
be reviewed, reverted or bisected topic by topic. Honesty and reviewability are
different properties, and the first does not substitute for the second.

## The incident

A profile storefront shipped four topics in one change: the rule-catalogue answer
file (verdicts on every record), a commit-attribution fix, the pipeline (change
checks, merging, auto-merge) and the project journal. Five commits, four
different layers, six hundred lines.

The checks passed and it was merged. The damage showed not at the merge but right
after.

**Reverting piecewise became impossible.** Half an hour later the pipeline part
turned out to break attribution — and it could no longer be reverted without
dragging the catalogue verdicts and the journal along with it.

**Review degenerated.** The description had to be written in four sections, each
with its own "why"; the reader must hold four contexts at once, and readers skim.

**The link to tasks became approximate.** The body said "part of task N" — true,
but not the whole truth: the pipeline and the attribution had nothing to do with
that task at all, they grew along the way.

The next change that evening began repeating the shape — three topics — and was
split only because the owner noticed and said so.

## How this differs from completeness of links

Rule [128](128-a-required-field-is-checked-for-completeness.md) grew from a very
similar incident — a combined change closed one task out of five — and fixes it
with a completeness gate: declare every task, not the first one to hand.

That makes a combined change **honest**: the tracker stops lying. But it stays
unreviewable. Completeness of the link field says nothing about whether one of
five topics can be reverted — and usually it cannot.

So 128 is a necessary condition, not a sufficient one.

## Why

**Reviewability is a property of the boundary, not of the description.** However
much you explain in the body, reverting works over commits, not paragraphs. If
topics are mixed inside one branch, the tool does not know where one ends and the
next begins.

**A second "why" doubles the cost of reading rather than adding to it.** The
reader holds the whole context; two independent "why"s do not read as two short
ones — they read worse than one long one, because there is no connection between
them to lean on.

**An agent executor has none of the fatigue that stops a person.** A human,
having finished a topic, is tired and stops. A session, having finished a topic,
sees another one next to it and takes it — "while I am here". The rule bears on
it harder than on a person precisely because the natural limiter is absent.

## In practice

- **the unit is the topic, not the task**: one topic may close two tasks, and one
  task may need three changes in a row; count topics;
- **the sign of a combined change is observable**: the diffs land in different
  layers, or the description grows an "and also", or the change has more than one
  "why";
- **the exception is named**: no split where the intermediate state does not work
  — a rename together with its consequences, a migration together with the reader
  of the new format. Then the topic is one, merely wide;
- **the mechanism warns rather than refuses**
  ([051](051-warn-on-likely-block-on-certain.md)): a count of touched zones does
  not prove combination, and a false refusal on a genuinely wide topic costs more
  than a miss;
- **file overlap outranks the topic**: tasks editing the same file travel
  together even when there are formally two topics —
  [133](133-file-overlap-sets-the-boundary.md).

## Where it applies

**Works** wherever a change goes through review and might need reverting.

**Does not work** for a change with no working intermediate state: a wide topic
is one topic, not a combined one.

**Sign of a violation:** the description has to be written in sections, each with
its own "why".

## Trace

ArtVsMark/ArtVsMark#19 — a combined change across four topics and its
consequences; #20 and #21 — the same work after being split;
ArtVsMark/Stepik-Python-Grader#1350 — the incident behind 128. See also:
[128](128-a-required-field-is-checked-for-completeness.md) — the necessary
condition, [133](133-file-overlap-sets-the-boundary.md) — the boundary that
outranks the topic, [098](098-the-unit-of-splitting-follows-usage.md).
