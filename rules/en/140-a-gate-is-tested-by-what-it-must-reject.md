# A gate is tested by what it must reject

**Area.** gates, tests

**The rule.** A gate has a subject it is **obliged to refuse** and a subject it
is **obliged to pass**; both are put through it on purpose. Until such a run
exists, "the gate will not let it through" is a promise — and it is usually
written where people will read it and believe it: in the rulebook.

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

## The second incident: a set of refusals only tests half the gate

The rule's first edition asked only for a subject the gate must refuse. A
profile showcase did exactly that — and was caught by it.

Its verdict-liveness gate got a self-test written strictly to 140: forged
subjects are run on purpose, and a refusal is what is expected. Then the
self-test itself was checked by mutating the gate:

| mutation | self-test |
|---|---|
| the parser finds nothing, the gate is always green | **failed**, as it should |
| path parsing eats the leading dot | **passed** |

The second mutation is not invented: it was the check's actual first draft.
Path parsing started at a letter, so `.github/workflows/pr-check.yml` was read
as `github/workflows/pr-check.yml`, and the gate refused **eighteen live links
out of eighteen**.

The set could not see it. It consisted of subjects the gate must **refuse**,
and all of them were refused correctly. The defect lived in the other half: the
gate was also refusing what it was obliged to pass.

**The first edition's reasoning leaned on
[097](097-a-checker-has-two-error-types.md) and took only one of its two errors
— the invisible one.** The logic ran: a false pass never announces itself,
while a false refusal is seen at once, "someone will come and complain." In a
pipeline without a human, the second half of that sentence does not exist. A
false refusal looks like ordinary red on a correct change, and there is nobody
to come and complain. The session sees red, edits the record to fit the check —
and a gate that scolds correct work starts being routed around
([051](051-warn-on-likely-block-on-certain.md)). So a false refusal is not
cheaper, it is expensive differently: it does not break the release, it
destroys trust in the gate, and that is noticed later than a false pass.

The second half is checked just as cheaply — by mutation: break the gate toward
a false refusal and confirm the set fails.

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

- for every gate, a subject it is **obliged to refuse** and a subject it is
  **obliged to pass**, and a run of both in the pipeline;
- the healthy subject is taken **from the border**: a short name instead of a
  full path, a template instead of a literal, a neighbouring spelling. That is
  where false refusals live, not in the middle of what is allowed;
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

**A second sign, by the same measure:** a set in which every case expects a
refusal tests the gate by halves — a gate that is always red passes such a set
in full.

**Sign of a violation:** the rulebook contains the phrase "the gate will not let
X through", and there is not a single run with X.

## Trace

ArtVsMark/claude-code-playbook#54 — the measurement that exposed the gap between
the rulebook and the attribution gate. ArtVsMark/claude-code-playbook#72 — the
second incident: a set of refusals only let a false refusal through on eighteen
live links. The mechanism is `scripts/check_gates.py` and `tests/`: every set is
two-sided, and how many gates each of the two mechanisms covers is printed by
`scripts/check_charter.py`.

See also: [097](097-a-checker-has-two-error-types.md) — a checker has two error
types and the second is invisible;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a guard that finds no
subject must fail; [139](139-a-mechanism-is-confirmed-by-a-run.md) — a mechanism
is confirmed by a run; [002](002-rule-without-mechanism.md) — a requirement
without a mechanism.
