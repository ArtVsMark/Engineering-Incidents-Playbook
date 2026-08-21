# A checking tool has two errors, and each is held by its own test

**The rule.** A false "passed" and a false "failed" are different defects with
different consequences. A regression test is written for **both** sides
separately; covering one creates the illusion of covering both.

## The incident

A checking tool errs in two ways, and they are asymmetric.

**A false "passed"** — the incorrect was accepted. The worst defect: a person
believes the work is finished, the external system does not accept it, and trust
in the tool is gone. A case from practice: the standard line-splitting function
treated **eight further control characters** as newlines, and output containing a
vertical tab was judged equal to an expectation of two lines.

**A false "failed"** — the correct was rejected. A person edits working code and
loses time, and finding a non-existent error is impossible by definition.

Both sides are held by **different** regressions: the first by corrupting output
with a control character, the second by noise in the low digits and by changing
the line-ending characters. Neither of those tests would have caught the other
side's defect.

## Why

The errors live in different places and are not caught by one set of checks. A
false "passed" is a comparison that is **too broad**: something that should
differ was judged identical. A false "failed" is **too narrow**: something that
should match was judged different.

Any edit to the comparison rule moves the boundary and almost always cures one
side at the other's expense. That is why tests are needed on both: otherwise a
"we made it stricter" fix slips through unnoticed until somebody complains.

The cost, however, is asymmetric, and that affects priority. A false "failed" is
noticed at once and complained about. A false "passed" is **noticed by nobody** —
by construction: the result matched what was wanted, so nobody verifies it. It
is discovered from outside, and already as a loss of trust.

## In practice

- each side has its own cases in the suite, named so that it is visible which
  side they hold;
- any edit to the comparison rule triggers a check of both sides, not only the
  one it was made for;
- the cases come from **corrupting the real thing**, not from imagination:
  corrupt a correct answer in a known way and verify that it is noticed;
- a false "passed" is investigated first when complaint counts are equal: there
  will be no complaints about it at all.

## Where it applies

**Works** for any classifier or validator: solution checking, spam filtering,
diagnostics, recognition.

**Does not work** if error is possible in one direction only — then the second
regression is empty.

**Sign of trouble:** every comparison test checks that the correct is accepted.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/corpus.md` § why it exists when there
are tests (the `vertical_tab`, `float_noise`, `crlf_newlines` mutations).
Related: [055](055-your-own-expectations-are-a-hypothesis.md).
