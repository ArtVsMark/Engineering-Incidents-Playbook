# Warn about the likely, block only the certain

**The rule.** A signal that fires on legitimate cases must be a warning and must
**not block**. Only what is proven blocks.

## The incident

A tool shows where your work overlaps with somebody else's: which files a
neighbouring branch is editing. Overlap is a useful signal but **not evidence of
an error**: two changes often legitimately edit different parts of one file, and
for a changelog that is simply normal.

So the tool always exits successfully and blocks nothing. It warns: look, these
files are being touched by somebody else too. What to do about it is a human
decision: if the overlap is substantive, agree on merge order, or the second one
will be resolving conflicts by hand.

## Why

A prohibition that fires on a legitimate case teaches people to **route around
it**. Having bypassed a gate once for a good reason, they bypass it a second
time for a poor one — and now the gate protects nothing while still costing what
it costs.

Second: prohibition and warning have different costs of error. A false
prohibition stops work — expensive and noticed at once. A false warning costs a
second of attention. So the boundary runs along certainty: **a certain breach
blocks, a likely one warns**.

Third: a warning can be introduced early, before the rule is precisely
formulated. A prohibition needs precision, otherwise it catches the wrong
things.

## In practice

- a warning **must** say what to do about it — otherwise people stop reading it;
- do not mix the two: one signal is either a block or a warning; "blocks, but a
  flag skips it" degenerates into the flag being always on;
- a warning matures into a prohibition when false positives stop appearing, and
  that is a separate decision, not a quiet edit;
- a warning also needs a measurable criterion — "by eye" works badly even in
  soft mode.

## Where it applies

**Works** for heuristics: overlapping work, suspicious patterns, quality metrics
with a fuzzy boundary.

**Does not work** where the breach is certain (broken syntax, a failing test) —
soft mode there merely lets breakage through.

**Sign of the wrong choice:** the gate is bypassed routinely, and bypassing is
considered normal practice.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § two lines of work
(`scripts/check_work_overlap.py` always exits zero).
