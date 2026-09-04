# The guard sees the raw value: formatting comes after it

**Area.** gates, metrics

**Tier.** 3 — gates and processes

**The rule.** The "did the source answer" guard is placed on the **raw** value.
Never show the guard a formatted value: formatting destroys the very mark by
which the guard recognises emptiness, and turns a dead source into a plausible
number.

## The incident

A profile showcase rebuilds its numbers from live sources and deliberately fails
when a source stays silent: "the metric did not come in — I rewrite nothing".
That is its central mechanism; the whole thing was built for it.

The tile value was assembled like this:

```python
plate = [(f"{tests // 1000}000+", "tests"), (coverage, "coverage (all OS)"), ...]
...
empty = [key for key, value in {...}.items()
         if not str(value).strip() or (str(value) == "0" and key != "gfi")]
```

Formatting stands **before** the guard. A run:

```
source answered 4321 -> tile "4000+ tests" -> guard PASSES
source answered    0 -> tile "0000+ tests" -> guard PASSES
source answered  999 -> tile "0000+ tests" -> guard PASSES
```

Zero — the one thing the guard looks for — never reaches it: it is no longer
`"0"` but `"0000+"`. The neighbouring metrics, which the guard sees raw, halt the
build correctly on zero. The protection works for everything except the metric
that was formatted in front of it.

The cost: "0000+ tests" would appear on the showcase, the run would report
success, and the number would live until somebody noticed it by eye — exactly the
outcome the whole build exists to prevent.

## Why

**The guard is a predicate over a value, and formatting changes the type of the
value.** `0` → `"0000+"`, `0.0` → `"0.0%"`, `None` → `"—"`, an empty list →
`"none"`. After any of these, emptiness is expressed in something other than what
is being checked.

**The bug is invisible on reading, because both lines are correct separately:**
the format is right, the guard is right. Only the order is wrong — and order, in
code, looks like the order in which variables were declared, which is to say like
nothing at all.

**A second trap lies in what the guard assumes.** Written against strings, it
usually looks for `""` and `"0"` — the shape produced by the **absence** of
formatting. It silently assumes nobody worked on the value first, and that
assumption is written down nowhere.

## In practice

- the raw value reaches the guard, and formatting is applied to what has already
  been checked;
- if one list of checked values mixes raw keys with display strings, that is the
  sign of the bug, not variety;
- "the source stayed silent" is a third outcome, not a success
  ([039](039-three-outcomes-not-two.md));
- parsing your own string back in order to check it is not a solution but a
  confirmation that the raw value should have been carried through
  ([122](122-ship-the-raw-value-next-to-the-formatted-one.md)).

## Where it applies

**Works** for any publication of something measured: showcases, reports, badges,
dashboards, metric exports — anywhere there is a "source stayed silent → do not
publish" step.

**Does not work** for shape checks — length, pattern, allowed characters: their
subject is precisely the formatted value, and the raw one does not fit them.

**Sign of a violation:** in the list of checked values, some keys are raw and
others are already display strings.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#40 — the analysis and the run; the metrics build
of the profile showcase, ArtVsMark/ArtVsMark.

See also: [075](075-a-guard-that-finds-nothing-must-fail.md) — a gate that finds
no subject must fail: here it is the subject it fails to find;
[122](122-ship-the-raw-value-next-to-the-formatted-one.md) — ship the raw value
next to the formatted one; [039](039-three-outcomes-not-two.md) — "the source
did not answer" is a third outcome.