# An optional channel neither delays nor breaks the main work

**Area.** architecture

**The rule.** An addition to the main function fails **quietly and at once**: any
of its errors is swallowed, there are no retries, and its time is bounded. A
retry here does more harm than the failure.

## The incident

Explaining an error through an external model is a pleasant addition to checking
a solution, but it is not the check itself. Hence a contract written before the
implementation: **the check never fails because of the addition**. A time limit
is set, and any channel error — network, timeout, service refusal, malformed
response — simply means the hint is skipped, with no exception surfacing.

A separate decision records that **there are no retries, deliberately**. The
usual reflex — "the network blinked, let us try again" — works against you here:
the hint is best-effort, and a second attempt does not improve the result, it
**delays the thing the user actually came for**.

## Why

An optional channel has a different utility function. The main work is valuable
for its result; the addition is valuable because it **sometimes** appears. Hence
a direct consequence: its absence is a normal outcome, not an error, and must be
handled as normal.

Retrying is especially treacherous because it looks like care. In fact it turns a
rare invisible degradation (sometimes there is no hint) into a frequent visible
one (everything got slower) — that is, it moves the cost from the secondary onto
the primary.

Here also runs the boundary with the rule about loud failure. **A guarantee fails
loudly, an addition fails quietly.** The difference is not in the nature of the
component but in what was promised: requested isolation that is missing is a
failure; a hint that did not happen is silence. They are easy to confuse, and
both errors are expensive: a silent guarantee deceives, a shouting addition gets
in the way.

## In practice

- the channel has its own time limit, clearly smaller than the main work's;
- the catch around channel errors is broad and **deliberately deaf** — but only
  around the channel itself, not around a piece of the main logic;
- there are no retries; if they are needed, the channel has stopped being
  optional, and that is a separate decision;
- a missing result appears in the output as an absence, not as blankness: "it did
  not work" beats an empty space;
- the channel is switched on explicitly and switched off by one toggle —
  otherwise it cannot be excluded during diagnosis.

## Where it applies

**Works** for hints, data enrichment, telemetry, previews, recommendations.

**Does not work** for anything promised as part of the result: there the failure
must be visible.

**Sign of a breach:** the main operation became slower after the addition was
introduced.

## Trace

ArtVsMark/Stepik-Python-Grader — `SECURITY.md` § AI hints, ADR-0003. Related:
[045](045-no-silent-fallback.md) — the opposite case,
[058](058-when-the-quota-is-out-stop.md).
