# Ship the raw value next to the formatted one

**Area.** contracts, data

**Tier.** 1 — rules and roles

**The rule.** Formatting is a lossy operation. When you emit a quantity for
display, emit the original number beside it: parsing the string back is
reconstructing what you destroyed yourself.

## The incident

The response with measurement results carried metrics as strings with
automatically chosen units — convenient for a table: "144.812 ms", "1.2 s",
"870 µs".

The comparison chart needs **raw** values: it scales axes and computes
proportions. Parsing the string back would have meant guessing the unit from the
suffix, restoring the order of magnitude, and living with the rounding the
formatting had already applied.

So the same metrics are emitted **twice**: as strings for display and as numbers
in seconds for computation. The neighbouring mode, whose consumer computes from
the start, emits numbers from the beginning.

## Why

Formatting fuses three things into one string: the value, the unit and the
rounding. The inverse operation requires separating them — and it is **not
equivalent**: the rounding is not undone, and suffix parsing breaks on the first
new unit or a different locale (decimal comma, non-breaking space, a different
thousands separator).

Hence the practical point: the string is for the **human**, the number is for the
**machine**, and trying to serve both with one quantity serves both badly.
Emitting both is cheaper than any parsing: a few bytes in the response against a
separate parser with its own edge cases and its own tests.

Second: parsing your own output is a sign that the data took the **wrong route**.
It appears when a consumer was not anticipated, and it almost always means the
original value already exists nearby, just out of reach.

## In practice

- the raw value is in **one, named** unit (seconds, bytes), not in whichever unit
  the formatter happened to choose;
- the field name states the unit: then it need not be guessed;
- the formatted field is marked as display-only, so nobody builds calculations on
  it;
- if there are many raw values and only one display, duplicate only those that are
  actually computed with — not "all of them just in case";
- the same rule applies to dates, sizes, money and percentages.

## Where it applies

**Works** for interface responses, reports, exports, journals read by both humans
and programs.

**Does not work** for purely human output (text in a terminal) where no machine
consumer exists by design — but then there is usually a machine-readable output
mode alongside.

**Sign of a breach:** the code contains parsing of a string produced by the same
product.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/api.md` (comparison-mode metrics:
strings for the table and `*_s` numbers for the chart). Related:
[113](113-a-contract-states-how-it-may-change.md),
[118](118-keep-the-source-next-to-the-derived.md).