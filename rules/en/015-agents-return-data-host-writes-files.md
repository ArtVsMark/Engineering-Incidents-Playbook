# Agents return data — the host writes the files

**Area.** parallel work

**The rule.** Parallel executors hand back a result; they do not write into the
shared tree. Writing belongs to one party.

## The incident

A wave of parallel agents, each with its own task, edited files directly. The
result is predictable in hindsight: overwrites, lost changes, a tree state
nobody could explain.

## Why

Parallel writes to a shared resource without synchronisation are a race. Agents
cannot see each other, and "read, then write" performed by two of them loses one
of the results.

Worse, the failure **does not reproduce**: it depends on who got there first,
and next time it may not happen at all.

Separation removes the problem entirely: executors work in parallel and return a
structured result; the host applies changes sequentially, seeing the whole
picture and resolving overlaps.

A side benefit is that each agent's result becomes **data**: it can be checked,
displayed, stored in a journal. Editing in place leaves no such option.

## Where it applies

**Works** for any parallel processing over shared state: agent waves, workers,
distributed builds.

**Does not work** if executors are genuinely isolated — each in its own copy of
the tree, for instance. Then conflicts are resolved on merge, not on write.

**The price:** the result has to be expressible as data. For code changes that
means diffs or structured findings, not "I fixed it".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md`
