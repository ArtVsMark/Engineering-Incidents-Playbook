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

## Where it applies

**Works** for any "this test catches the defect" claim: test-first development,
regression tests, proof of a fix in a pull request.

**Does not work** for tests that check the existence of a thing — there
`ImportError` is the expected failure.

**Generalisation:** proving redness is an experiment, and the usual demands on
an experiment apply. Change one variable; make sure the failure happened **for
the reason** under test, not for the first reason available.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § what the gates miss