# Calibrating against an external signal requires a complete input

**Area.** metrics, quotas

**Tier.** 2 — the pipeline and CI

**The rule.** If your scale is built from the moment an external indicator
flips, the input must cover **everything** that indicator reacts to. A sum over
the visible part is not the sum.

## The incident

The task: work out how much of a limit remains when the limit is published
nowhere as a number. All that is exposed is a three-step traffic light plus
actual spending per session. The plan was elegant: add up spending across all
sessions and remember the total at the moment the light changes — that total is
the scale.

A check against a live account exposed the hole. The source sees three kinds of
session but reports spending for only one: sessions started on the owner's
machine have no spending field in the listing, and some of them never appear in
the registry at all.

Meanwhile the limit is **shared across the account** — the light reacts to all
spending, including the invisible part. So the flip arrives at a total lower
than the real one, and the scale is understated by exactly the invisible share.

## Why

The error looks like a bias and is not one. The invisible share is not constant:
it depends on how much work happened where the counter cannot reach. So it is
**noise, not an offset**, and accumulating measurements does not cure it —
averaging works against random error, not against varying incompleteness.

Hence a practical conclusion that was not obvious before the check: **the
remainder is measurable, the scale is not**. The state indicator arrives
correctly and is visible everywhere; what breaks is translating that state into
a number.

The general form: calibration binds an **external event** to an **internal
counter**. The event is always complete — it is about the whole system. The
counter is complete exactly as far as its input is. The difference between them
goes entirely into the error of the scale, and it is invisible in the data
itself.

## In practice

- before building a scale, answer in writing: **what the indicator reacts to**
  and **what reaches the counter** — the discrepancy is the future error;
- the completeness of the input is part of the output, not a footnote: the
  measurement reports what share was collected and what is invisible entirely;
- while completeness is unknown, the scale is labelled an estimate, not
  "refined as data accumulates";
- sources covering different parts do not replace one another — they are added,
  and overlapping records are deduplicated by identifier: double counting
  distorts the scale exactly as much as omission.

## Where it applies

**Works** for inferring any hidden threshold from an observable flip: quotas,
throttling, external API limits, alert thresholds.

**Does not work** if the indicator reacts to exactly what you count — then the
calibration is honest.

**Sign of trouble:** the scale is built confidently, and the question "what did
not make it into the total" has no answer.

## Trace

ArtVsMark/Claude-Code_Usage-Token#13.