# Your own reference answer is also a hypothesis

**The rule.** An expectation written by your own hand proves nothing. Until an
external source confirms it, a discrepancy means "one of the two is wrong", not
"the product is broken".

## The incident

There is a catalogue of deliberate corruptions of a solution — timeout, syntax
error, extra line, truncated last line, trailing space, wrong case, CRLF, noise
in floating-point values. Each corruption is checked against **an expectation
written by a human**: this corruption must be caught in this way.

The very first run over real material showed that the discrepancy was an error
**in the corruption itself**, not in the checking system. In other words, a red
result had for months meant not a product defect but a defect in our idea of the
correct answer.

From that came a data source nobody had planned: **the corruptions are submitted
to the external platform too**. It says whether a corrupted solution is accepted
or not — and there is nothing left to guess.

## Why

A reference written by the product's author inherits the author's
misconceptions whole. It checks not "is this correct" but "is this what I
thought" — and that thought is beyond doubt precisely because it is your own.

References for **edge cases** are especially treacherous: that is exactly where
the mental model diverges from reality, and exactly where nobody looks — an edge
case is rare by definition and has no counter-check.

An external source breaks the circle: it took part in writing neither the product
nor the reference. Any independent arbiter will do — the target platform, a
reference implementation, a specification with examples, another team.

One more symptom of the same circle: **compare not only the outcome but the
diagnosis**. A matching verdict with a mismatching failing-case number means the
match was accidental — and that is only caught by comparing both parts.

## In practice

- every reference states what confirms it: an external source, a specification,
  or nothing — the third is acceptable but must be named;
- a discrepancy is analysed symmetrically: first "did the reference get it
  wrong", then "is the product broken";
- compare the intermediate diagnosis as well as the final answer — otherwise an
  accidental match looks like confirmation;
- a reference corrected against an external source is marked as such —
  otherwise, a month later, nobody knows where the number came from again.

## Where it applies

**Works** where an independent arbiter exists: a platform, a standard, a
reference implementation, a live user.

**Does not work** if there is no arbiter at all — then the reference is honestly
labelled an assumption rather than passed off as truth.

**Sign of trouble:** a test has been red for a long time and is being
"explained" rather than fixed.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/course-walkthrough.md` § broken
answers come from the catalogue, § compare the diagnosis as well as the verdict.
