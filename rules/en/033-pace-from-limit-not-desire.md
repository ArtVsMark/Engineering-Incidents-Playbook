# The pace of long work is derived from the limit, not from eagerness

**Area.** quotas, pace

**The rule.** The interval between launches follows arithmetically from the
budget. Otherwise the work hits the wall mid-wave — and loses the whole wave.

## The incident

Multi-wave work failed not from difficulty but from the **session limit** — and
it always failed at the worst moment: mid-wave. Agents received "You've hit your
session limit" and their work was lost entirely.

In a single run this happened twice: two agents in one wave and four in another.

## The arithmetic that settled it

Counting turned out to be easy:

- a wave of five executors costs roughly **550 thousand tokens** — about
  **9–10%** of the five-hour window;
- so the window fits **eight or nine waves**, allowing for debriefs and
  write-ups;
- hence a working cycle of **40 minutes start to start**: the wave runs about
  twenty minutes, the rest is a pause.

Three options compared:

```
30 minutes → 10 waves, ~95% of the limit → hits the wall mid-wave
40 minutes →  7–8 waves, ~85%            → the optimum: margin without idling
60 minutes →  5 waves,  ~47%             → half the window burns, twice the time
```

## Why

The urge to run back to back is understandable: a pause feels like wasted time.
But the cost of hitting the wall is asymmetric: stopping loses **the entire
current wave**, not the last step.

A pause costs minutes. A lost wave costs a wave — plus the time to work out what
exactly was lost.

Second: the interval must be computed **from measured spending**, not assigned
from a feeling. "An hour is probably enough" would have doubled the elapsed time
at half the utilisation.

## Where it applies

**Works** for any long work under a quota: agent waves, batch jobs, mass API
calls.

**Does not work** without measurement: to divide a budget you must know the cost
of a unit of work. The first run is always reconnaissance.

**Recompute** when wave size or budget changes — the numbers do not transfer
between projects.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § pace
