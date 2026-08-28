# A skip without a reason is indistinguishable from a forgotten test

**Area.** tests

**The rule.** Every skip must carry a reason, and the number of skips must be
visible by name. A suite of thousands of tests gives confidence exactly as long
as the skips are explained.

## The incident

Some tests do not run on any single machine, and that is normal: three
OS-specific isolation mechanisms, optional dependencies, no graphical display.
What is not normal is **not knowing how many tests are silent**.

A green summary of "5074 passed" says nothing about how many `skipped` sit
beside it and why. A skip added once for a flaky test and forgotten looks exactly
like a skip with the honest reason "this OS is not here".

## Why

A skip is **a hole in the claim of green**. "Everything passes" is only true
together with an answer to "and what was not checked". Without a reason a skip
is indistinguishable from a forgotten test: both are silent in the same way.

So two different views are needed, answering different questions:

- **what was skipped in this particular run** — with file, line and reason;
- **where skips are declared at all** — a static inventory of every conditional
  skip and expected failure, with a summary.

The first catches today's picture, the second catches accumulation.

## In practice

- a skip without a textual reason is a build error, not a style remark; a
  dedicated test enforces this, otherwise the rule becomes a promise again;
- the inventory counts expected failures too: an expected failure is the same
  silent test;
- the number of skips goes into the run summary next to the number of passes.

## Where it applies

**Works** anywhere part of the checking is conditional: different operating
systems, optional dependencies, paid external services.

**Does not work** if there are no skips at all — then the inventory is overhead.

**Sign of trouble:** the question "how many tests are not running right now, and
why" has no one-command answer.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § why skips are visible by
name; `scripts/skip_inventory.py`, `tests/test_skip_inventory.py`.