# A gate blocks what the change itself has certainly brought; everything else is a warning

**Area.** gates

**Tier.** 3 — gates and processes

**The rule.** A block is placed only on a violation that is proven and that the
change itself brought in: an edit to that same change removes it. A signal
that fires uselessly in legitimate cases, and a discrepancy that already lived
in the tree before the change, are warnings, not blocks. What the change
brought is measured by its increment: more lines with the subject arrived than
left — not "the file was touched". There is one exception — a violation
dangerous in itself (broken syntax, a failing test, a leaked secret): it
blocks whoever brought it.

## The incident

**First — a false block teaches bypassing** (record 051, the grader). A tool
shows where your work overlaps someone else's: which files a neighbouring
branch edits. Overlap is a useful signal but not a sign of an error: two
changes often legitimately edit different parts of one file, and for the
changelog it is normal. So the tool always exits successfully and warns, and
what to do about an overlap is a person's decision (the grader's
`scripts/check_work_overlap.py` always exits zero).

**Second — a certain violation left to drift gets through** (the mechanisms
project, proposal `a-change-is-judged-by-what-it-adds`). On 25.10.2026
ArtVsMark/Engineering-Pipeline-Mechanisms#1671 raised `actions/setup-python`
from v7.0.0 to v7.1.0 in all 43 pins. The same day
ArtVsMark/Engineering-Pipeline-Mechanisms#1674 added a new line with v7.0.0 —
two versions of one action in one workflow. Only drift held it, with the
argument "fixed by a migration, not by editing the change", and drift would
have named it a day after the merge. The argument holds for a pre-existing
discrepancy and fails for a brought-in one: it was enough to write the line
with the version standing next to it.

**A measurement over history** (mechanisms, 28.10.2026; the figures are taken
from their proposal and are not reproducible in the catalogue's tree), with the same
predicate — every merged change that touched workflows, against its parent: of
337 mechanisms changes 11 were named, all of one kind (`actions/checkout@v4`
next to `v7.0.1`); of 515 changes in the family, two
(ArtVsMark/Glossary-Python#12, ArtVsMark/Stepik-Python-Grader#40). False
positives — zero.

**We had the technique, not the rule.** Three catalogue gates already judge
the increment against the change's base, each for its own reason:
`check_asked_family.py` asks about the family only for a mechanism the change
adds; `check_attribution.py` checks history with `--since`;
`check_narrowing.py` judges the change's range. A fourth,
`check_duplicates.py`, is a neighbouring technique: only rules newer than
`baseline` must answer about neighbours, so the past is declared debt by
number rather than separated by an increment.
Before this record none referred to a common rule: each derived the technique
anew.

## Why

**A block that fires on what the change cannot remove teaches bypassing.** A
legitimate case and someone else's earlier discrepancy look the same to the
author: there is red, and nothing to fix in their own change. Having bypassed
the gate once for a good reason, people bypass it again for a bad one, and the
gate stops protecting anything while its cost remains.

**A warning on a certain, brought-in violation lets the breakage through.**
Drift sees the discrepancy after the change is merged and the author has left.
Someone else fixes it then, and the one who brought it never learns.

**So the line is drawn by two questions at once:** is the violation proven, and
did this change bring it. A block is a "yes" to both. The costs of the errors
differ: a false block stops work, a false warning costs a second of attention,
and a missed brought-in violation costs a migration after the merge.

## In practice

- the increment is more lines with the subject arriving than leaving, against
  the change's parent; "the file was touched" is not an increment;
- raising a version everywhere at once is not an increment of the discrepancy
  but its removal;
- a warning says what to do with it — otherwise people stop reading it;
- one signal is either a block or a warning: "blocks, but can be skipped with
  a flag" degenerates into the flag being on by default;
- a warning matures into a block by a separate decision, once false positives
  stop appearing.

## Where it applies

**Works** for gates on a change: heuristics (overlapping work, suspicious
patterns, metrics with a blurry boundary) — as a warning; a certain violation
the change brought — as a block; an earlier discrepancy of the same subject —
as drift and a warning.

**Does not work** for checking the whole main branch, outside a change: there
is no increment there, and the state is judged — that is the subject of the
main-branch duty ([142](142-a-scheduled-red-needs-an-addressee.md)). **Does
not work** either where a violation is certain and dangerous regardless of who
brought it — broken syntax, a failing test, a leaked secret: that always
blocks.

**Sign of a wrong choice:** the gate is regularly bypassed and the bypass is
considered normal practice; or a change brings in a discrepancy that only
drift sees after the merge.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § Две линии работ
(`scripts/check_work_overlap.py` always exits with zero)

ArtVsMark/Engineering-Pipeline-Mechanisms — scripts/check_action_pins.py

Related: [114](114-migrate-from-the-current-version-not-from-zero.md) — a
migration applies only to what has not passed it; here a gate judges only
what was brought; [133](133-file-overlap-sets-the-boundary.md) — file overlap
between changes, the original example of a warning.
