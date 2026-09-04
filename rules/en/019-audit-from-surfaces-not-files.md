# An audit is planned from the product's surfaces, not from its files

**Area.** audit

**Tier.** 3 — gates and processes

**The rule.** Walking the files gives you code coverage and misses everything
that is not in the code. Start from the list of things the user meets.

## The incident

The first audits went directory by directory: walk the modules, find defects.
The result was hundreds of findings and a firm sense of completeness.

Meanwhile whole surfaces were **never** examined: browser scenarios, behaviour
under missing permissions, the wording of messages, the installation path for a
newcomer. None of them existed in any file as a separate entity, so a file walk
never met them.

A later dedicated slice found dozens of findings "visible only to the eye".

## Why

A file is a unit of storage, not a unit of experience. Users do not encounter a
module; they encounter installation, first launch, an error, recovery after a
failure.

Walking files optimises **code coverage**, while the question is about surface
coverage. These are different sets, and the second is larger: it contains what
the code does not — the missing handler, the page that was never written, the
scenario that is impossible.

A practical technique: list the surfaces in advance (installation, launch,
error, data, documentation, recovery), then ask for each "who checks it and in
which environment". An empty cell is a blind spot, and it is visible at once.

## Where it applies

**Works** for any review: code audit, release readiness, post-incident analysis.

**Does not work** for narrow tasks: if the review concerns one module, there is
one surface.

**The price:** the list of surfaces has to be written and it is subjective. But
an empty cell in a table is more honest than a hundred per cent coverage by
files.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § plan from surfaces