# One executor's zone must be small

**Area.** parallel work

**The rule.** Split a role across two or three executors and give each plan no
more than three items. A large zone dies whole.

## The incident

The wave was the right size — five executors. But each was given a **whole
role**.

The result: `Connection closed` **on delivery of the answer**. The work was
done, the result never arrived. Five of five, twice in a row — 884 and 503
thousand tokens for nothing.

So limiting wave size did not save us: the failure moved from the level of "how
many were launched" to the level of "how much one was given".

## Why

The larger the zone, the larger the final answer — and the higher the chance it
does not arrive. The failure lands at **the most expensive moment**: the work is
already done, already paid for, and is lost entirely.

Second effect: a large zone is hard to verify. A result of "I went through the
module" can be neither confirmed nor decomposed; a result of "three specific
points" is checked point by point.

Third: splitting gives **restart granularity**. One of three fell over — repeat
a third, not everything.

## In practice

- split a role across **two or three** executors rather than handing it to one;
- an executor's plan holds **no more than three** items;
- prohibitions and environment quirks go **into the task text**, they are never
  implied: the executor cannot see what the host knows.

## Where it applies

**Works** for parallel executors with a cap on answer size.

**Does not work** if the task is indivisible: then the only way out is to shrink
not the zone but the demands on the answer (a structured result instead of
prose).

**The sign of too large a zone:** answers get lost on delivery or arrive
truncated.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § splitting a role