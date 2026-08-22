# A gate is tested by what it must reject

**Area.** gates, tests

**The rule.** A gate has a subject it is **obliged to refuse**, and that subject
is put through it on purpose. Until such a run exists, "the gate will not let it
through" is a promise — and it is usually written where people will read it and
believe it: in the rulebook.

## The incident

A catalogue's rulebook said, in plain text, under critical prohibitions:

> ❌ Do NOT commit without attribution trailers — **the gate will not let it
> through**

I built a repository with two commits carrying no trailers at all and ran the
gate:

```
attribution is fine: 1 commits, without attribution 1
exit code: 0
```

**It let them through.** The gate goes red on a name outside the agreed list and
on a session trail without co-authorship — a commit with no signature at all it
counts and passes. The sentence in the rulebook described not the mechanism but
the intention of whoever wrote it.

Neither side could reveal this by reading. The rulebook reads as a requirement,
the script reads as a list check, and only the third thing — running a subject
that must be refused — shows they are about different things.

## Why

**A gate errs in two directions, and the second one is invisible.** A false
refusal is seen at once: somebody comes and complains. A false "passed" never
comes — it looks like a healthy run, and the longer the gate stands the more it
is trusted ([097](097-a-checker-has-two-error-types.md)).

**Only a refused subject tests the check.** A green run on good input confirms
that the gate starts, and nothing more. A gate that always returns zero passes
that test perfectly.

**A claim about a gate outlives the gate.** The script gets edited, the condition
narrowed, the step moved — and the line in the rulebook stays. It is the more
dangerous of the two: the script at least runs, while nobody executes a sentence.

## In practice

- for every gate, a subject it is **obliged to refuse**, and a run of that
  subject in the pipeline;
- the subject is forged on purpose rather than awaited from real life: waiting
  for a genuine violation means testing the gate at the moment it has already
  failed;
- the rulebook's wording follows the run, not the intent: what was refused is
  what gets written;
- the third outcome is a subject too: a check that "did not run" must be
  distinguishable from one that passed ([039](039-three-outcomes-not-two.md));
- if there is nothing to refuse, there is no gate — there is a counter, and
  calling it a gate does harm.

## Where it applies

**Works** for checks that refuse: pipeline gates, validators, linters,
publication guards.

**Does not work** for metrics and reports: they have no subject of refusal, they
print a number, and they are verified differently — against a known answer.

**Sign of a violation:** the rulebook contains the phrase "the gate will not let
X through", and there is not a single run with X.

## Trace

ArtVsMark/claude-code-playbook#54 — the measurement that exposed the gap between
the rulebook and the attribution gate. The mechanism is
`scripts/check_gates.py`: the gate is run against a forged subject, and a refusal
is what is expected.

See also: [097](097-a-checker-has-two-error-types.md) — a checker has two error
types and the second is invisible;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a guard that finds no
subject must fail; [139](139-a-mechanism-is-confirmed-by-a-run.md) — a mechanism
is confirmed by a run; [002](002-rule-without-mechanism.md) — a requirement
without a mechanism.
