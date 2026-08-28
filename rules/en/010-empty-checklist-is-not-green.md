# An empty list of checks means "never started", not "all clear"

**Area.** CI

**The rule.** The condition "nothing red and nothing pending" is true of the
empty set. Verify that the checks were created at all.

## The incident

Immediately after a push, the readiness gate reported the pull request could be
merged: nothing red, nothing pending.

There were no checks at all — GitHub had not created them yet. "Everything
green" held over emptiness.

A related case from the same place: when a branch conflicts with the main line,
the build runs against a merge commit, and that commit cannot exist — so **no
check runs are created at all**. From outside it looks like "the build broke",
when the build never started.

## Why

The classic quantifier mistake: "all elements satisfy the condition" is true for
the empty set. Checking for the absence of bad things does not substitute for
checking the presence of good ones.

In the interface it looks convincing: no ticks, no crosses, therefore fine.

## Where it applies

**Works** anywhere a decision is made from a set of results: builds, linters,
vulnerability scanners, test suites.

The generalisation: **check the size of the set before checking its
properties.** "Zero problems found" and "the scanner never ran" produce the same
report.

The same class covers gates on empty input: a script that found nothing must
distinguish "nothing to check" from "everything checked and clean".

**Does not work** where an empty set is legitimate and means success — for
example, a check for "no uncommitted changes".

## Trace

ArtVsMark/Stepik-Python-Grader#1232