# Collecting and analysing are separate passes

**Area.** runs, process

**Tier.** 3 — gates and processes

**The rule.** Nothing is analysed during a collection step: run it, write the
raw result, move on. Analysis is a separate pass, at the boundary of a natural
unit of work.

## The incident

A long run over real material: hundreds of steps, each one a launch, a
submission, a response from an external system. The temptation to analyse a
discrepancy on the spot, while the context is at hand, is very strong.

Four arguments against, each learned the hard way:

- **the pattern is visible over a chapter, not over a step.** A single
  discrepancy looks like chance; three in a row on tasks of the same format is a
  class of defect with a ready reproduction;
- **analysing in place triples the step time**, and the run is long enough
  already;
- **collection and analysis want different conditions:** collecting has to
  happen where the real data and the network are, while thinking, fixing and
  writing tests happen where that is cheaper;
- **a break costs one step, not the whole run** — the raw result is written
  immediately.

The only decision taken during a step is "can we continue": every submission is
failing, the external system is refusing, the credentials expired. That is a
liveness check, not analysis.

## Why

Analysing in place substitutes an impression for statistics. A person (and an
agent) sees the first discrepancy, forms a hypothesis, and from then on **looks
through it** — the following steps confirm it simply because that is what was
being sought. Analysis over accumulated material starts from the distribution,
not from the first case.

Second: collection and analysis have different costs of error. Collection is
cheap to repeat if the raw result was written. Analysis embedded in collection
is lost with the run when it breaks — and long work always breaks.

Third: the separation creates **a point of return**. A chapter boundary is where
a short summary is written and where you can stop without losing what is done.

## In practice

- a step writes the **raw** result, without interpretation: whatever came back,
  in full;
- the run has a natural unit (chapter, batch, day), and at its boundary comes a
  summary: how much was done, how many discrepancies, in which classes;
- the liveness check is separated from analysis explicitly, or it quietly grows
  into "while I am here, let me look";
- analysis happens where thinking is cheaper, not where collecting happened.

## Where it applies

**Works** for long runs over external material: reconciliations, migrations,
mass checks, crawling.

**Does not work** if continuing depends on the previous step's result — there
analysis is part of the cycle.

**Sign of a breach:** the collection step takes three times as long as planned,
and there is no answer to "which class of defect dominates".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/course-walkthrough.md` § collection
and analysis are separate.