# Measure what is left of the quota instead of guessing — and look first

**Area.** quotas, diagnostics

**Tier.** 2 — the pipeline and CI

**The rule.** Diagnosis starts with facts about the quota, not with hypotheses
about causes. Asking for the remainder is usually free.

## The incident

The limit was hit **four times in one day**, and each time the investigation
started from scratch: theories about which command was "too heavy", hunting for
the guilty code, optimising the wrong thing.

The answer sat in a single call the whole time:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" https://api.github.com/rate_limit
```

Three counters separately: remainder and reset time for each. And the **reset
time shows when the window began** — which indirectly says who spent it.

The call itself costs nothing against the limit.

## Why

A hypothesis about spending is built on a mental model of what is expensive. That
model is usually wrong: in the case investigated, the expensive part was the
**transport**, not the amount of work — 300 units per operation against one.

Measuring answers the question in a second and does not require knowing in
advance where to look.

The second argument is the **asymmetry of cost**: asking for state is free, an
hour of guessing costs an hour. At that ratio, "look first" always wins.

## Where it applies

**Works** for any rate-limited resource whose state can be queried: API limits,
disk quotas, build minutes.

**Does not work** if the remainder is not exposed as a number — then it has to
be inferred from spending, which is a separate problem.

**Careful:** the attempt counter can keep growing **after** exhaustion. A
rejected request is still charged, so you cannot "use up the remainder", and the
number of attempts says nothing about the number of successes.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § diagnosis first