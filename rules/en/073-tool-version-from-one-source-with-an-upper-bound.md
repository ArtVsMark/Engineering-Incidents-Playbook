# A tool's version comes from one source and has an upper bound

**Area.** tooling

**The rule.** The version of a linter, formatter or builder is set in **one**
place, and it has an upper bound. Otherwise the local check and the shared build
diverge, and the local one stops meaning anything.

## The incident

The linter's version was set by two parties: the pre-commit hook configuration
and the dependency specifier. Synchronisation was manual — and it diverged
exactly as a comment in the config itself had warned: the environment and the
build got one version while the hook kept reformatting code by the previous
one's rules.

The consequence mattered more than the divergence: a local "check passed"
**stopped saying anything** about whether the shared build would be green. The
tool that all of this exists for lost its purpose — it no longer predicted the
outcome.

The second half of the same problem was the missing **upper bound**. Without it
the shared build installs the newest version on the day it ships while the
contributor still has yesterday's: the same divergence, only spread over time and
therefore even less visible.

Third: the **actually installed** version is checked too. A stale local install
produces a false "all clean" before anything has diverged at all.

## Why

A checking tool is valuable precisely because its verdict is **transferable**.
As soon as two parties have different versions the verdict becomes a local
opinion, while trust in it persists by inertia — and that is the worst state:
the check exists, the confidence exists, the guarantee does not.

An upper bound looks like cowardice but protects against an asymmetric risk: a
new linter version brings new rules, meaning **redness on unchanged code**, and
it arrives not when expected but on a random day, in the middle of somebody
else's task.

## In practice

- there is one source for the version; the second way of setting it is
  **explicitly forbidden**, because it will return disguised as convenience;
- the specifier has an upper bound, and raising it is a change of its own, not a
  side effect;
- not only the declared version is checked but the **installed** one;
- the check avoids heavy dependencies: three facts do not justify pulling in a
  parser — but then it says why the parsing is simplified and what it relies on.

## Where it applies

**Works** for tools whose verdict is compared across machines: linters,
formatters, generators, builders.

**Does not work** for runtime libraries — there an upper bound blocks security
fixes.

**Sign of trouble:** "it is all clean locally for me" has stopped predicting the
build result.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_ruff_pin.py`,
ArtVsMark/Stepik-Python-Grader#791. Related:
[035](035-version-is-never-edited-by-hand.md).