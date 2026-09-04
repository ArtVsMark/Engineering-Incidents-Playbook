# Generated output is checked by properties and by sampling, not against a reference answer

**Area.** AI, quality

**Tier.** 4 — code and tests

**The rule.** A non-deterministic component has no "correct answer" to compare
against. Acceptance runs on properties that must always hold, plus a sample that
somebody actually reads.

## The incident

The temptation is obvious: record one good answer from the model and check for a
match. Such a test goes red when the model version changes, when the temperature
changes, when the word order changes — that is, almost always, and it is quickly
disabled. After that there is no check at all, while the confidence remains.

The opposite mistake cost more and happened to us. Counting successful
completions as sufficient evidence of quality does not work: five executors that
reported "done" produced coherent rubbish — a retelling of what was already
written, filler, wrong facts. The mechanical check was green throughout.

Another measurement has the same nature: adversarial re-checking of findings left
**16 confirmed out of 83 claimed**. Generated output looks convincing exactly in
proportion to how well it is written — which has nothing to do with whether it is
correct.

## Why

Deterministic code is checked by equality: the same input gives the same output.
A generator lacks that property by construction, so equality checks not its
quality but its immutability — a quantity nobody cares about.

What must be checked is what **must hold for any answer**:

- **form** — structure, fields, length, absence of forbidden markup;
- **grounding** — everything substantive is present in the input; invention
  beyond it is a defect regardless of elegance;
- **boundaries** — the answer contains nothing it is forbidden to emit;
- **sampling** — part of the output is read by a human or a separate checker and
  compared with the task point by point.

The key: properties check **every** answer and are cheap; a sample checks
**meaning** and is expensive. Both are needed — properties will not notice
coherent rubbish, and a sample will not cover the volume.

## In practice

- form is checked strictly, content softly: a test for an exact match with the
  answer text is never written;
- the sample is at least one result per executor in the first run, and it is read
  in full rather than skimmed;
- grounding is checked mechanically where possible: a claim absent from the input
  is a finding;
- the answer is marked as generated wherever a human will see it: unmarked, it
  acquires an authority it does not have;
- a change of model or prompt is a reason to run the sample again, not "well, it
  used to work".

## Where it applies

**Works** for language models, generators of code and text, heuristics with an
element of randomness.

**Does not work** if the output is deterministic for fixed input — there equality
is the correct check.

**Sign of error:** the only check on the generator is that it did not crash.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0003, `core/ai_grounding.py`; the
2026-08-10 audit (16 confirmed `high` out of 83). Related:
[060](060-debrief-every-wave-quality-first.md),
[055](055-your-own-expectations-are-a-hypothesis.md).