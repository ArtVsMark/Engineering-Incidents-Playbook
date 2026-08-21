# Automatic intervention fires only when all conditions hold

**The rule.** If a false positive damages somebody else's work, write the
criterion as a conjunction: intervene only when **every** condition is met. Any
unmet condition means "do not touch".

## The incident

The task looked simple: notice abandoned work and repair it. The naive scheme
"check is red → fix it" breaks on the second of three states, and there are
exactly three:

| What is visible | What it means | What to do |
|---|---|---|
| session running, branch updating | work in progress | **do not touch** |
| session waiting for a human's permission | a person is needed | **call the owner** |
| no live session owns the branch, no change for over an hour | abandoned | repair |

The second state is the trap: the work is done, the session is alive, but it is
stopped at a permission prompt. A repairer will climb into the same branch and
**trample somebody else's work** — silently, because from outside it looks like
an ordinary edit.

So "abandoned" is defined by a list of four conditions, all mandatory: no live
session owns the branch; the last change is older than an hour; the pull request
is open and not a draft; there has been no activity within the same hour.

## Why

The costs of error are asymmetric. Missing abandoned work loses time until the
next walk. Intervening in live work destroys what was done, and the loss is
discovered late, because it looks like the normal course of work.

Under that asymmetry the criterion must be **conservative**: a conjunction errs
towards inaction, a disjunction towards intervention. Choosing between them is
not style but a direct consequence of which error costs more.

Second: there are almost always more than two states. "Working / broken" is a
simplification with no room for "waiting for a human", and that is exactly the
state requiring a third, fundamentally different response: neither fix nor
ignore, but **summon**.

Third: the criterion must be a list, not an impression. "Looks abandoned" cannot
be reproduced, discussed or verified — a list is checked item by item and can be
argued with substantively.

## In practice

- enumerate the states **before** writing the automation, and give each its own
  response;
- the conjunction's conditions are phrased observably: age, presence, activity —
  things read by a query, not judged;
- every condition has its own reason: a condition without one is the first to
  drop out during an edit;
- doubt is resolved towards inaction and is **logged**: "did not intervene
  because condition 2 was not met" — otherwise silence from the automation is
  indistinguishable from its breakage.

## Where it applies

**Works** for automation that edits other people's work: repairs, cleanup,
resource reclamation, auto-closing.

**Does not work** for reversible actions with a low cost of error — there a
disjunction is faster and cheaper.

**Sign of the wrong choice:** after the automation was switched on, complaints
of "my work disappeared" appeared.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/dispatcher.md` § three states of a
session, § signs of ownerlessness are a list, not a hunch. Related:
[007](007-blocked-window-looks-alive.md),
[012](012-do-not-push-to-someone-elses-branch.md).
