# "The test goes red without the fix" is proved by a partial revert, not a full one

**Area.** tests

**Tier.** 4 — code and tests

**The rule.** Remove only the behaviour and keep the new names. Otherwise you
have proved something other than what you think.

## The incident

To confirm that a new test really caught the defect, the whole source directory
was reverted and the suite was run. The tests went red — and the proof was
accepted.

Investigation showed they were failing on `ImportError`. That proved only that
**the test references the new code**, not that it exercises the behaviour.

A test of that quality stays green through any error inside the function, as
long as the function exists.

## Why

A full revert changes **two things at once**: both the behaviour and its name
disappear. The test fails at the first obstacle — the import — and never reaches
the behaviour check.

The correct experiment changes exactly one variable: names in place, behaviour
removed (`return None`, an empty body, the old branch of the logic). Red under
those conditions means precisely what you need.

## Practical limits

This arrived as a proposal from the mechanisms project and was merged in here
rather than given a second number: the subject is the same — verifying a gate by
rollback — and splitting it would put the red outcome and the green one in
different records (022).

**A GREEN ROLLBACK IS A FINDING ABOUT THE CHECK, NOT LUCK.** You removed the
behaviour, kept the names, ran the suite — and it is green. That is not "it
worked out", it is an answer, and it means one of two things, both of which
require work.

**FIRST: THE ROLLBACK NEVER APPLIED, AND THIS IS CHECKED FIRST.** A string
replacement silently finds no match — the formatter rewrote the condition across
several lines, a name changed, the indentation differs. The suite stays green and
the fix stays untouched: the experiment did not fail, it did not happen. Until
this is ruled out, the second explanation cannot be considered — you would start
repairing a check that may be sound.

**SECOND: THE CHECK IS WEAKER THAN YOU THOUGHT.** It holds something other than
what it promises — comparing files instead of functions, names instead of
behaviour. That is
[146](146-a-green-gate-does-not-verify-its-premise.md) in its pure form.

**"I RAN THE ROLLBACK" WITHOUT A RESULT SAID OUT LOUD MEANS ONLY THAT THE COMMAND
WAS RUN.** The result is named with a number or a word — what went red and where
— before the mechanism is declared confirmed. The measurement over our own corpus
on 2026-09-17 is unpleasant and therefore recorded: the phrase "verified by
rollback" occurs ONCE across all 160 changelog fragments, and that one quotes
another project. The rule has been in force from the earliest days, is held by a
document (`CONTRIBUTING.md` § When a defect counts as fixed), and leaves almost
no trace of its own work in the tree.

**WHAT THIS DOES NOT MAKE MECHANICAL.** Telling behaviour from names inside a
rollback still means reading the meaning of an edit, and there is no gate here and
none is being built
([182](182-an-unmechanisable-answer-is-split-in-two.md)): the machine gets the
form — that a line about the rollback's result exists at all next to declaring the
mechanism confirmed; the human gets whether the result is named correctly.

## Where it applies

**Works** for any "this test catches the defect" claim: test-first development,
regression tests, proof of a fix in a pull request.

**Does not work** for tests that check the existence of a thing — there
`ImportError` is the expected failure.

**Generalisation:** proving redness is an experiment, and the usual demands on
an experiment apply. Change one variable; make sure the failure happened **for
the reason** under test, not for the first reason available.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § Что гейты не ловят