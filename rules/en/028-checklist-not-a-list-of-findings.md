# A complex task keeps a checklist, not a narrative

**Area.** tracker

**The rule.** From three items upwards, use tick boxes rather than prose.
Otherwise the state of the task has to be computed by reading.

## The incident

Tasks with a dozen findings were described as a list in the body: "we found
this, that, the fifth thing, the tenth". As work progressed some were fixed and
some rejected — and the body was edited in prose.

Working out what remained required reading the whole thing and comparing it with
the edit history. The tracker's progress counter meanwhile showed zero: as far
as it was concerned there was one task and it was open.

## The fix

A checklist. The box is ticked **in the same pass as the closing change**, and
it names the outcome: the number of the change, or the reason for rejection.

- [x] Finding A — fixed in #123
- [x] ~~Finding B~~ — rejected: false positive on generated code
- [ ] Finding C

A rejected item is **struck through but kept** — otherwise the counter lies (see
the rule on rejected findings).

From about thirty items upwards, group by file or by zone. A flat list of a
hundred boxes is as unreadable as prose.

## Why

A checklist makes state **readable by machine and by eye**: the tracker itself
shows "7 of 12" without reading the contents.

Second: the box is ticked at the moment of closing, not "later during the
review". Prose requires rewriting — and therefore does not get rewritten.

The condition: **state lives only in the task**. Duplicating progress into a
document gives two sources, one of which will go stale.

## Where it applies

**Works** for tasks with several independent items: audit findings, migration
lists, acceptance checklists.

**Does not work** for single-subject tasks — there a checklist is overhead.

**For an epic with child tasks** boxes are unnecessary: the tracker counts
progress itself.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § complex issues
