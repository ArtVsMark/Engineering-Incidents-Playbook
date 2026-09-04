# Retention is counted from completion, not from enqueueing

**Area.** code, resources

**Tier.** 4 — code and tests

**The rule.** A record's lifetime is measured from **the moment it became
terminal**. Counting from enqueueing sweeps the result away faster the longer the
work took.

## The incident

Run records are kept for a limited time — otherwise the registry grows without
bound. The natural "count from enqueueing" produces an unpleasant skew: the
longer the work ran, the less time is left for its result.

In the limit, work that takes as long as the retention period is **swept away
immediately after finishing**: the user waited longest of anyone and never saw
the result. Exactly on the longest and most valuable runs.

The fix: on entering any terminal status the record stamps its completion time,
and the sweeper measures from that.

A second limitation surfaced later: **one retention period is not enough**. A
loop of requests grows the registry without refusal, because the sweeper only
cleans completed entries and each result lives its own fifteen minutes. A hard
cap on the number of records was needed — and it is applied **after** insertion:
before insertion it would hold one fewer than declared, and the just-added record
is not terminal so it cannot evict itself.

## Why

Retention answers "how long the result must remain available after it appeared".
Counting from enqueueing folds the duration of the work itself into that period —
a quantity unrelated to the availability of the result and, on top of that,
unpredictable.

Second: **two limiters are needed and they catch different things**. Retention
bounds age, the record cap bounds volume. A burst evades the first (the records
are young), a long-running job evades the second (there are few records). Either
one alone leaves a hole, and the hole is found not by an attacker but by an
ordinary request loop.

## In practice

- the timestamp is set **on transition** into the terminal state, not on read;
- the record cap is applied after insertion, otherwise it holds one record fewer
  than declared;
- only completed entries are eligible for eviction: the sweeper does not touch
  active work;
- both limiters are stated in the documentation as numbers — "roughly a quarter
  of an hour" cannot be verified.

## Where it applies

**Works** for background job registries, result caches, run journals.

**Does not work** if execution time is negligible compared with the retention
period — then the difference between the two reference points is invisible.

**Sign of trouble:** the result of a long operation disappears sooner than the
result of a short one.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/runs.py`,
ArtVsMark/Stepik-Python-Grader#408, ArtVsMark/Stepik-Python-Grader#811.