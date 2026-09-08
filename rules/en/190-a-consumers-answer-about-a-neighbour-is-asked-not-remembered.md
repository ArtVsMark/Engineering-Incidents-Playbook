# A neighbour's answer shape is asked for, not remembered: only its absence is recorded

**Area.** contracts, metrics

**Tier.** 3 — gates and processes

**The rule.** A showcase displaying neighbouring projects' numbers does not keep
the SHAPE of their answer — where the metric lives, under what name, whether it
is published at all. It queries sources in a declared order and shows the first
one found; what stays recorded is only ABSENCE — the reason a neighbour has no
such metric. A mismatch between what is recorded and the live source is a
finding, not a build failure: otherwise every neighbour gains the right to stop
your pipeline, by an edit on their side, and a correct one at that.

**Portable beyond Claude Code.** yes — the subject exists for any summary built
from other people's sources: a metrics dashboard, a status aggregator, a
dependency showcase.

## The incident

A profile showcase kept the shape of its neighbours' answers in `projects.json`:
`{"endpoint": "coverage"}` versus `{"none": "reason"}`. That is a copy of
someone else's definition — the very thing the showcase itself had forbidden
when it wrote the facts contract for those neighbours.

Over three days in September the copy diverged TWICE, and both times took
everything down:

- on 4 September the glossary moved `badges/coverage.json` from a badge to a
  coverage-completeness report — the build died with a bare `KeyError` on the
  `message` field;
- by the 5th it had separated the two properly: the badge returned to its place,
  completeness moved into `facts.json`.

Both edits on THAT side were correct. On ours the showcase did not rebuild at all
on 5, 6 and 7 September, and then the freshness watchdog went red, honestly
reporting that the numbers were from the 4th. A rebuild of thirty numbers, the
image publication and the watchdog all stopped — because of one badge belonging
to one project.

Measured after the rewrite: the same scenario, reproduced with a forgery, now
shows the live value 96.8% together with a finding "the recorded answer is
stale"; the daily build finishes the rest, the change check goes red.

## Why

A neighbour's answer shape is their definition, and keeping it locally means
keeping a copy that diverges silently. A neighbour is free to move their number:
it is their tree and their decision, and they owe no warning. Meanwhile the copy
looks correct right up to the first divergence.

Hence order instead of memory: query the sources in turn and take the first that
answers. What is worth recording is absence — the neighbour declares that
themselves, and it is their answer, not a copy of their definition.

The asymmetry of cost settles the second half. One neighbour's wrong badge does
not make the other thirty numbers wrong and does not prevent recomputing them. If
it fails the build, any neighbour gains the power to stop your pipeline — not
through malice but through an ordinary edit. So a mismatch reddens the change
check, where its author fixes it, while the scheduled rebuild carries on with a
warning.

## In practice

- sources are listed as an order, not as one address: named identifier → badge
  for the metric → field in the facts contract → "no such subject";
- what gets recorded is ABSENCE with a reason, not a location;
- a mismatch accumulates as a finding; the build computes the rest;
- the freshness watchdog looks at the rebuild date, and its red is about your
  build, not their edit.

## Where it applies

**Works** for summaries over other people's published numbers, where there is
more than one source and they change independently.

**Does not work** where there is a single source and it is yours: your own
metrics are read directly, and an order of sources only adds branches. Nor does
it apply where a neighbour is bound to you by a contract on location — there a
mismatch is their violation, and red is legitimate.

**Sign of violation:** your own file holds a field naming WHERE a neighbour's
number lives.

## Trace

ArtVsMark/ArtVsMark — `scripts/build_metrics.py::live_value`: the order of
sources (named identifier → badge for the metric → facts contract field → "no
such subject"), findings about neighbours accumulate instead of failing

ArtVsMark/Engineering-Incidents-Playbook — `.rules/consumers.json` stores the
address of an answer, not its shape; `scripts/aggregate_bindings.py` turns an
unreachable answer into a finding and finishes counting the rest

Related: [174](174-facts-about-a-project-are-published-by-it.md) — facts are
published by the project itself, the same thought from the other side: do not
keep someone else's definition; [049](049-derive-state-from-live-artifacts.md) —
state comes from a live artefact, and a neighbour's answer shape is state too;
[004](004-conflict-is-normal-not-outage.md) — a consumer's divergence is a state
of the summary, not an outage of the run.
