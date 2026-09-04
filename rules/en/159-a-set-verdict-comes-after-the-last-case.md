# A set's verdict comes after the last case, not in the middle of the walk

**Area.** tests, gates

**Tier.** 3 — gates and processes

**The rule.** A set that collects findings into a list reads that list **after
the last case**. An early return turns everything that follows into printing:
the cases run, findings are appended to a list nobody reads again, and the run
answers "passed". From the outside such a set is indistinguishable from a
working one.

**Portable beyond Claude Code.** yes — the subject belongs to any walk with an
accumulator, not to agent sessions.

## The incident

On 31 August, in the showcase build's self-check
`scripts/build_metrics.py::selftest`, `if broken: return 1` turned out to sit
right after the banner checks, with **three more groups of cases** behind it: a
call without the grader clone, a comparison of the answer against the rule
catalogue, and a source failure.

All three printed their lines and appended findings to `broken`, which nobody
read after the early return. Measured with a planted failure in the last group:
the self-check answered with code `0` and the line "self-check passed".

The early return was not carelessness — it looks like thrift: "we found a
break, no point running the rest". And it stays true exactly until the first
group appended **after** it.

## Why

A set grows at the end where new cases are appended — that is, right past the
verdict. So the defect does not appear when the code is written: it appears for
whoever adds the next group, and is invisible to them and to the reviewer,
because a diff shows only what was added.

The silence is two-sided and quiet both ways. The run prints the same lines a
working one does — nobody sums them. And
[140](140-a-gate-is-tested-by-what-it-must-reject.md) promises "a gate is proven
by what it must reject", but it is proven only up to the verdict: forgeries
standing further along prove nothing.

## In practice

- the verdict over an accumulator is taken once, at the end of the walk;
- an early return is legitimate for the "did not run" outcome — it stops the
  work rather than concluding it: there is nothing left to walk;
- a new group of cases is appended **before** the verdict, and that is where
  people slip: the end of the file and the end of the walk stopped coinciding.

## Where it applies

**Works** for any walk that accumulates a result: a forgery set, a self-check, a
sweep over artefacts, findings collected by an audit.

**Does not work** where the walk must stop on substance: the first failure makes
the remaining cases meaningless — the input they are built from did not parse,
say. That is not a verdict but the third outcome
([039](039-three-outcomes-not-two.md)).

**Sign of violation:** between the `return` over the accumulator and the end of
the function there are lines appending to that same accumulator.

## Trace

ArtVsMark/ArtVsMark#95

Related: [136](136-a-verdict-comes-after-enumerating-every-subject.md) — the
same bias in an answer about somebody else's rule: there the verdict is taken on
the first subject, here on the first group of cases; different subject, one
mechanism; [140](140-a-gate-is-tested-by-what-it-must-reject.md) — its promise
is what an early return undermines;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a check that never reached
its subject must say so rather than going green.
