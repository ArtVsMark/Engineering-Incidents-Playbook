# An outside audit is done by somebody who did not write this code

**The rule.** A second pass by **your own** tool reproduces the same blind spots.
An outside view means a different executor with a different history, not another
attempt.

## The incident

External audits of the project are done by a **different system** — not the one
the code is written with. The owner's phrasing is direct: somebody who did not
write this code sees in it what the author cannot.

Practice confirmed that twice. The remark about collapsed blocks on the front page
came from an external review four times in a row, and three times it was put down
to the reviewing tool's quirks — until it became obvious that when four readers
see the same thing, the problem is not the readers.

The reverse case happened too: an external report contained findings whose premise
proved wrong on checking. So an outside view does not replace verification; it
adds a **different** set of errors — and that is precisely why it is useful: the
intersection of two different sets is closer to the truth than doubling one.

## Why

A blind spot is a property not of diligence but of **history**. Whoever wrote the
code knows what was meant and reads what is written through that knowledge. A
second pass by the same executor reproduces the same understanding: they re-read
not the text but their memory of it.

Hence the criterion of "outsideness": what matters is not "a different person" but
**a different source of knowledge about the subject**. A colleague who took part
in the discussion is not outside. Nor is a tool operating on the same history.

Second: an external report arrives with **its own** errors, and that is not a flaw
but the condition of its usefulness. Its findings are checked for premise like any
others; the value is that it errs **in a different direction**.

## In practice

- outside means anybody without the history of this decision: a different tool, a
  person outside the project, a third-party review;
- a recurring remark from outside is a signal, not noise: three or four identical
  observations from different sources outweigh an internal explanation;
- findings from an external report undergo the same premise check as your own;
- analysing an external report is a separate audit task, not an appendix to it.

## Where it applies

**Works** for audits, reviews, usability checks, documentation assessment.

**Does not work** where deep context is required: an external executor without
access to the decision history will produce a lot of noise about deliberate
trade-offs.

**Sign of a missed blind spot:** the same remark arrives from outside not for the
first time, and internally there is a ready explanation for it.

## Trace

ArtVsMark/Stepik-Python-Grader — `HISTORY.md` § how it started; the 2026-08-10
audit (a separate phase for analysing an external report). Related:
[044](044-check-the-premise-before-fixing.md),
[086](086-the-finder-does-not-grade-the-finding.md).
