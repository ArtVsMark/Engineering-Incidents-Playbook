# Two honest metrics beat one averaged number

**Area.** metrics

**Tier.** 5 — everything else

**The rule.** If no single truthful number exists, publish two — each with a
note saying what exactly it measures. Averaging them into one means lying twice.

## The incident

Test coverage. Isolation is implemented by three mechanisms, one per operating
system, and on any single machine two of the three are **unreachable in
principle**. A single number came out either understated (other systems' code in
the denominator) or overstated (other systems' code silently excluded from both
numerator and denominator).

The answer was two figures with different thresholds:

- a run on one operating system, other systems' mechanisms excluded from the
  denominator — the lower threshold;
- the union of runs across all systems, no exclusions — the higher threshold.

The project's real coverage is the second. The first exists for the sake of the
local run: a contributor's check on one operating system must not go falsely red
over code that system physically cannot execute.

## Why

A metric is an answer to a question. Two different questions ("what is covered
here and now" and "what is covered at all") have no common answer, and trying to
issue one produces a third number that answers neither.

A side effect of honesty: the lower threshold **must not be raised**. It is
calibrated for one specific case — a contributor's run on one system — and any
increase turns it into a false red for people who did nothing wrong.

A second consequence of the same principle: **a stale date is more honest than a
wrong number**. If the data for some slice did not arrive, the figure is not
published at all, and the reason is written as a separate warning — with
"artefact never arrived" and "artefact is empty" named individually.

## In practice

- every number on display says what it measures and what its threshold is;
- it is stated plainly which number is the real one and which is auxiliary;
- the auxiliary threshold is never raised — a note beside it says why;
- no data, no publication: silence beats an invented value.

## Where it applies

**Works** when part of the measured subject is unavailable at the point of
measurement: multiple platforms, paid integrations, rare hardware.

**Does not work** if the difference between the numbers is smaller than their
margin of error — then two figures only confuse.

**Sign of trouble:** the number is routinely "explained" in conversation instead
of being split.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § why there are two coverage
badges. Related: [005](005-hand-written-numbers-rot.md) — a number typed by
hand.