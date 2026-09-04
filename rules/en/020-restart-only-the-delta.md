# After a failure, restart the delta, not the whole wave

**Area.** parallel work

**Tier.** 2 — the pipeline and CI

**The rule.** Work out what is already done and repeat only what is missing. A
full restart pays twice for one result.

## The incident

A wave of parallel agents kept hitting the limit. The natural reaction — run the
wave again — meant work already completed was done a second time, hit the limit
again, and was lost again.

The analysis showed two things. First, **an agent cut off on its attempt limit
had not lost its work** — the result was in the journal and needed collecting,
not discarding. Second, only the tasks with no result should be repeated.

## Why

A full restart assumes "the wave fell over, so nothing got done". That is
usually false: some of the executors finished.

The difference is arithmetic. A wave of ten tasks with eight completed: a full
restart costs ten units, the delta costs two. With repeated failures the gap
grows, and a full restart may **never converge** — every attempt hits the same
limit at the same place.

The condition for applying this is that **the result must be stored separately
from the process**. If it exists only inside the executor that died, there is
nothing to compute the delta from. Hence the link to "executors return data": a
stored result is what makes restarting cheap.

## Where it applies

**Works** for batch processing, agent waves, migrations, mass builds.

**Does not work** if the tasks are coupled and a partial result is useless —
then starting over is cheaper.

**Requires:** a journal of what is already done. Without one the rule is a wish.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § restart the delta