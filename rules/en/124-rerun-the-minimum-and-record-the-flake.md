# Re-run the minimum — but green on the second try is a finding, not a fix

**The rule.** When one check fails, re-run **that one**, not the whole suite.
But a re-run is **diagnosis**: if it passes the second time, that result must be
recorded as instability, or the test suite quietly loses its credibility.

## The incident

The full check matrix is three operating systems by two language versions, plus
isolation, static analysis, supply chain and end-to-end scenarios. Re-running
everything over one failed cell costs tens of minutes and occupies the executor
queue everybody else uses.

And the failures that call for a re-run are **not hypothetical** here:

- the file-system guard produced **14 false accusations in a row** — the culprit
  was a neighbouring tool running on the same machine, while the blame landed on
  the tests;
- one test flickered steadily on one platform, with the cause of failure hidden —
  which is precisely why it became its own task;
- spawning a process on a slow machine ran into the launch deadline, and **three
  different tests** went red for that single reason.

Each of the three passed on the second attempt. And each was a **real defect** —
just not in the code it pointed at.

## Why

The saving here is real and worth taking: re-running only the failed jobs keeps
the results of the ones that passed instead of recomputing them. But that saving
has a price, and it is not paid immediately.

**A re-run fixes nothing.** It changes the outcome without changing the cause.
Green on the second try means exactly one thing: the result of the check
**depends on more than the code**. That is a fact about the system, and it is
worth more than the run itself.

Hence the central discipline: **green after a re-run gets recorded**. Without a
record each individual flake looks like chance, while together they build a test
suite nobody believes — and then red stops being read at all.

Second: re-running **blind** turns a real defect into "it flickered". Log first,
button second. If the log shows a meaningful failure, there is nothing to re-run
— it needs fixing.

## When a partial re-run is legitimate

- **the commit has not changed.** Otherwise some results describe one state and
  some another, and together they describe nothing. Changed the code — run it all
  again;
- **the failed job is independent of the ones that passed.** If a closing step
  consumes its result — coverage assembly, publication, an aggregate — that
  closing step must be re-run as well, or it will combine fresh output with
  stale;
- **the readiness gate reads the latest result per unique name**, not the first
  it finds and not the sum of records. After a re-run a check has two runs with
  different outcomes, and a naive counter will see the old one;
- **the number of attempts is bounded.** Two re-runs is the limit; a third means
  this is not a flicker but a defect, and the log needs reading rather than the
  button pressing.

## In practice

- re-run the minimal set: only the failed jobs;
- read the log before re-running — at least the failure line;
- if it passed on the second try, raise a record: what flickered, on which
  platform, in which run. An unstable test is either fixed or explicitly marked,
  but never left nameless;
- instability is measured: the share of runs that needed a re-run is a real
  quantity, and it must not grow.

## Where it applies

**Works** where checks are independent and the platform can re-run a subset.

**Does not work** if jobs share state or the result depends on ordering — there a
partial re-run manufactures a consistency that does not exist.

**Sign of abuse:** "just re-run it, it fails sometimes" has become a normal
answer, and nobody remembers what exactly fails.

## Trace

ArtVsMark/Stepik-Python-Grader#1171, #924, #1344; rule
[103](103-a-side-effect-guard-blames-the-wrong-suspect.md) — 14 false
accusations. Related: [009](009-count-unique-not-total.md) — count unique names;
[052](052-only-the-head-of-the-queue-moves.md) — check against the current
state.
