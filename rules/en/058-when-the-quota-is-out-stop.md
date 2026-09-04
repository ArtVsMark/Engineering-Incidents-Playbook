# When the quota is exhausted, stop — do not retry

**Area.** quotas

**Tier.** 2 — the pipeline and CI

**The rule.** Past zero the counter keeps growing: a retry does not "try again",
it pushes the reset further away. And worse than the spending are the half-done
states left behind by rejected calls.

## The incident

The counter read **10,724 against a limit of 5000**. That is not "ten thousand
operations performed": it is 5000 successes plus 5724 rejections. Past the limit
the work does not go through — it is rejected, and the counter grows anyway,
because it counts **attempts, not successes**.

The practical consequence mattered more than the arithmetic. An agent on an
exhausted quota does not "work with complaints" — it does not work at all, and
it leaves stumps behind: the branch is pushed but no pull request is open; the
pull request exists but has no labels; the issue is closed but the comment never
went out.

Every such stump then has to be found and finished by hand — and found exactly
when nobody remembers what was left.

## Why

A quota behaves not like a tap but like a penalty: exceeding it extends the
punishment. Automatic retry, written for network glitches, works against you
here — it assumes "let us try, perhaps it works now", while every attempt
lengthens the wait.

Second, less obviously: **an exhausted quota is worse than idleness**. Idleness
leaves the system in a consistent state; working on an exhausted quota leaves it
inconsistent, and the cost of cleaning up exceeds any gain from "maybe it will
go through".

Third: **the quota is shared**. Spending by several parallel sessions adds up,
and polling intervals must be multiplied by their number. A session economising
honestly on its own will still hit the wall if two others are working alongside.

## In practice

- a rejection due to exhaustion is **not a reason to retry**: such errors are
  excluded from the retry policy separately from network ones;
- before stopping, finish the chains **already started** rather than beginning
  new ones: a stump costs more than something never launched;
- diagnose first, hypothesise second: the remainder and the reset time are read
  with one command, and the reset time shows when the window began — that is,
  who spent it;
- spending is counted across all participants, not for yourself alone.

## Where it applies

**Works** for any sliding-window quota with an attempt counter: APIs, external
services, session limits.

**Does not work** for overload rejections where retry with backoff is the
intended mechanism: there a pause genuinely helps.

**Sign of a breach:** the spending counter exceeds the limit.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § when the quota is
out, § `used` counts attempts. Related:
[017](017-measure-quota-do-not-guess.md).