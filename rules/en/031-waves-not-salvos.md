# Parallel executors launch in waves of fixed size

**Area.** parallel work

**Tier.** 2 — the pipeline and CI

**The rule.** Not in a salvo. A wave, a debrief, the next wave. A large salvo
manufactures its own failure, and the bigger it is, the more expensive the loss.

## The incident

Four attempts at launching many agents at once:

```
40 agents at once → API overload (503/529 → Connection closed):
                    13 of 32 lost
29 agents at once → session limit plus a cascade of 403 Failed to authenticate:
                    20 of 29 lost — 1.34M tokens for 9 results
24 agents at once → stopped by hand before the first result
 5 agents, but a whole role each → Connection closed ON DELIVERY of the answer:
                    5 of 5 lost, twice (884k and 503k tokens for nothing)
```

The scheme that works: **five agents → debrief → the next five.**

## Why

Three independent failure mechanisms, and all of them scale with the size of the
salvo.

**Overload on the receiving side.** Simultaneous requests hit throughput limits
and get refused.

**Session limit.** The shared budget runs out mid-salvo, and the work collapses
all at once — not one by one but in a cascade.

**Loss on delivery.** The last example matters most: five agents, but each given
too large a zone. The connection broke **at the moment of returning the answer**
— the work was done, the result never arrived. Twice, half a million tokens
each, for nothing.

So wave size is a ceiling, not a guarantee. A wave of five dies whole if each
executor was given too much.

## A separate invocation per wave, not one script with barriers

The difference shows when you stop: a script with barriers takes the unstarted
waves with it. Separate invocations give you a **checkpoint and a decision
point** between waves.

## Where it applies

**Works** for any batched parallel launch: agents, workers, mass API calls,
migrations.

**Does not work** where the receiving side is built for salvos and there are no
limits.

**The number is found by measurement**, not by guessing: ours is five, yours
will differ. The sign of the right size is that the wave completes, not that it
"usually completes".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § the main rule