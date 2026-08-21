# A gate that cannot find its subject must fail

**Area.** gates

**The rule.** A check that looks up an object by name **fails with an explicit
error** when the object is absent, instead of going green on empty input.

## The incident

The pipeline invariant check looks up a job by name and inspects the order of
steps inside it. The natural implementation — "found the job, checked it" —
returns green in two entirely different cases: when everything is correct, and
when the job **does not exist at all**.

The second case arrives through a harmless action: the job was renamed. The check
keeps running, reports success and verifies nothing — while looking like a
working defence.

So it is built differently: subject not found means failing with an explicit
error. A rename does not pass in silence.

## Why

A gate has two different states of success, and they are constantly confused: "I
checked and found no breaches" and "there was nothing to check". The second is
not success but **the absence of a check**, and equating them means losing the
defence at the least visible moment: not during a breakage but during a rename, a
move, a refactor.

The most dangerous part is that the degradation is **irreversible in time**: the
gate stays green for years, nobody re-verifies a defence that already works, and
the loss is discovered together with the incident it was supposed to prevent.

Hence a general requirement for gates: **empty input is an input error**. Zero
files found, zero matches, a missing section — all of these are reasons to fail
and to name what was not found.

## In practice

- "subject not found" gets its own code and its own message, not merged with
  "breach found";
- if zero matches is legitimate, that state is declared explicitly and justified,
  not implied;
- the gate has its own test for empty input — otherwise nothing verifies the
  rule;
- the same applies to expectations of count: "there must be exactly this many
  checks" is stronger than "checks exist";
- a setting implemented by an **optional plugin** silently has no effect without
  it: the plugin's presence is checked separately, or the declared restriction
  goes mute and nobody finds out.

## Where it applies

**Works** for any check that looks up its subject by name, path or pattern.

**Does not work** for aggregators where an empty result is a normal answer; there
emptiness should be printed, not raised.

**Sign of trouble:** the gate has never gone red since it was written.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_workflow_guardrails.py`.
Related: [010](010-empty-checklist-is-not-green.md),
[027](027-empty-state-is-a-state.md), [039](039-three-outcomes-not-two.md).
