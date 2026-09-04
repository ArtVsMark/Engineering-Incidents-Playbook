# A required field is checked for completeness, not for non-emptiness

**Area.** gates, tracker

**Tier.** 3 — gates and processes

**The rule.** When a required field's subject is a **set** (issues, areas,
platforms, touched modules), the gate checks it for completeness, not for
non-emptiness. One entry where five are due lies worse than an empty field:
emptiness is visible, half-filled looks filled.

## The incident

Linking a change to its issue is mandatory and gated
([064](064-labels-are-machine-input-not-decoration.md)): closing the issue on
merge and inheriting queue priority both hang off that line. The gate requires
**at least one** link, or an explicit exemption.

A combined change arrived. Six changelog entries in the diff named **five**
issues: renaming sessions, recording rules into the shared catalogue, role
coverage, the index generator, the attribution gate. The body carried **one**
link.

The gate went green — the field is not empty. On merge one issue closed and four
stayed open: done, with their work already in the shared history. The only way to
find out was by reading the diff, and a week later, in a tracker review, it looks
like "the work was never done".

The fifth issue, meanwhile, was closed **by a third**: it had grown after being
filed, and closing it would have been an outright mistake. Incompleteness is not
always a defect — that is part of the rule, not a footnote to it.

## Why

**"Non-empty" and "complete" are different predicates, and only the first
usually gets written.** It is cheaper: is there at least one link line in the
body. The second needs a notion of what the set **should** be — and so it gets
postponed, even though the source for it is usually already lying next to it.

**Absence is noticeable, incompleteness is not.** An empty field trips both human
and machine. A half-filled one passes both checks: the gate sees non-empty, the
reviewer sees a familiar line and does not count the subjects. The harm is
deferred — the discrepancy surfaces where it can no longer be managed: in the
tracker, in the queue, in a report.

**The author is not at fault; the form is.** A combined change grows commit by
commit: the first issue is declared, the second and third arrive with the next
commit, and by then nobody returns to the body. A rule that has to be remembered
is not a mechanism ([002](002-rule-without-mechanism.md)).

## The mechanism: the expected set comes from the change itself

Completeness cannot be checked without knowing what is expected. The good news is
that it is almost always already derivable — the same move as
[049](049-derive-state-from-live-artifacts.md): state is computed from live
artefacts rather than kept somewhere it has to be remembered.

In the incident the issue numbers sat inside the **changelog entries**: the format
requires a number in the text of every entry. The gate had both sets — one from
the diff, one from the body — and the check reduced to a set difference. No
heuristics, no extra API calls.

The general form: look for an **independent trace inside the same change** —
changelog entries, touched directories, test names, migration files. No such
trace means the rule is not mechanisable and should be named as such
([057](057-unmechanizable-rules-are-named-explicitly.md)) rather than mimed as a
check.

## In practice

- **warn, do not block**
  ([051](051-warn-on-likely-block-on-certain.md)): incompleteness is sometimes
  legitimate — a partial closure, a number that entered the text for another
  reason. What is certain here is the set difference, not the intent;
- **the message names both sides**: what was found in the change and what was
  declared in the field. "The field is incomplete" without a list makes the
  author search all over again;
- **partiality gets its own written form**: a line saying "part of issue #N —
  this slice" clears the warning and stays in history. That is a filled field,
  not an omission — the same device as the explicit exemption in
  [064](064-labels-are-machine-input-not-decoration.md);
- **both error types are held by tests**
  ([097](097-a-checker-has-two-error-types.md)): it does not stay silent on an
  incomplete field, and does not shout on a complete or exempted one;
- **count unique values** ([009](009-count-unique-not-total.md)): two entries
  about one issue are one subject, not two.

## Where it applies

**Works** for any required field whose subject is a set and which has an
independent trace: links from a change to its issues, a list of touched areas, a
platform matrix in a report, a list of versions being migrated.

**Does not work** when the expected set exists only in the author's head: there a
completeness check degenerates into noise, and it is more honest to call the rule
unmechanisable.

**Sign you need it:** issues that are "done but open" surface in a tracker review
rather than at the gate. A second sign — the field always holds exactly one
entry, however much the change carries.

## Trace

ArtVsMark/Stepik-Python-Grader#1350 (the link-completeness gate), precedent — PR
ArtVsMark/Stepik-Python-Grader#1345 (five issues in the changelog entries, one
link line in the body); ArtVsMark/Stepik-Python-Grader#1329 — the link-mandatory
gate, which lets this through by design. See also:
[064](064-labels-are-machine-input-not-decoration.md) — the field's
mandatoriness, which this record extends to completeness;
[049](049-derive-state-from-live-artifacts.md) — where the expectation comes
from; [039](039-three-outcomes-not-two.md) — there the third outcome is "did not
run", here it is "filled in part";
[116](116-the-collector-script-is-a-source-of-loss.md) — reconciling counts as a
mandatory step; [046](046-name-the-gaps-do-not-level-them.md) — a gap is named
rather than levelled.