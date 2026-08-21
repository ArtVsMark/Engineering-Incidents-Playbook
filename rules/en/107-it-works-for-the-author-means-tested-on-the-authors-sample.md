# "It works for the author" means "tested on the author's sample"

**Area.** borrowing

**The rule.** Somebody else's tool was tested on whatever its author had. Beyond
the bounds of their sample it is not broken — it is **untested**, and those are
different diagnoses.

## The incident

The project began with somebody else's tool, adopted for our own task. For a
while it worked, then discrepancies started: it reported an error where there was
none, and hung where it should not.

The analysis produced not "bad code" but **a boundary of applicability**: the tool
was written for its author's part of the course, and on the early topics there
was simply nothing to test it against — everything worked for the author because
tasks of that kind never came up.

Two consequences grew from that. First, adapting it to our needs was not a
grievance against the author but a normal continuation: somebody else's unfinished
edge became the start of our own thing. Second, our own tool has the same
boundary: it is tested on whatever came our way.

## Why

Working is not a property of code but a **relation** between the code and the set
of inputs it was run against. The phrase "it works" without naming that set is
incomplete, and nobody makes it complete: the author cannot see the bounds of
their sample from inside — for them it is the whole world.

Hence the practical point: when carrying somebody else's tool into your own
conditions, the first thing to establish is not quality but **what it was tried
on**. The answer is usually in the project's history, in the tests, in the
examples — and it also predicts where the discrepancies will start.

Second, symmetrically: the same is true of us. Claiming the product works, you
must be able to name the set that was verified — otherwise the next person gets
exactly the experience we got with somebody else's tool.

## In practice

- your own product records **what** it was tested on: which inputs, which
  environments, what volume;
- a discrepancy with somebody else's tool is first explained by the sample
  boundary and only then by an error: accusing it of a defect requires a
  reproduction;
- having taken somebody else's work as a base, you extend the applicability
  boundary with **your own** cases, and they enter the test suite immediately, not
  after the second occurrence;
- the original source is cited: that is both respect and an address for returning
  findings.

## Where it applies

**Works** when borrowing libraries, forks, templates, other people's scripts.

**Does not work** for anything with a formal specification: there a deviation
from it is precisely a defect, not a sample boundary.

**The tell:** "it all works for me" is said without listing what it was tried on.

## Trace

ArtVsMark/Stepik-Python-Grader — `HISTORY.md` § how it started. Related:
[046](046-name-the-gaps-do-not-level-them.md),
[055](055-your-own-expectations-are-a-hypothesis.md).
