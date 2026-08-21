# The critic checks the phase's method, not the subject of the work

**Area.** audit, process

**The rule.** At the end of every phase a separate checker answers not "what is
wrong with the product" but "what is wrong with how we checked it": what share of
the output is genuinely new, what the phase did not cover, where the declared
method turned out to be imaginary.

## The incident

The phase existed for the sake of running things: launch the product and see what
actually happens, instead of reading code. It ran, produced findings, reported.

A wave of critics fed its collection showed something else:

- **a third** of the executable surface was covered — the menu and the browser
  were **never** launched;
- the runs happened in **one environment out of the nine** declared in the
  matrix;
- **not one finding from the previous phase was verified** — although that was
  what the phase was for.

None of the three facts is visible from inside the phase. Every executor worked
honestly, the reports are complete, the findings are real. What was imaginary is
the **method**: what was called a run phase was two-thirds the same reading of
code.

## Why

Checking the subject and checking the method look in different directions, and
the first physically cannot notice the second. An executor answers the question
they were asked; they do not answer the question of **whether the right question
was asked**.

Hence the peculiarity of the input: the critic is fed not the product but **the
phase's collection** — what was launched, where, how many times, and what of that
produced anything new. They compare the declared method with the actual trace,
and the divergence between them is their finding.

Second: the critic comes **last**, and if anything was launched afterwards their
conclusion is re-read. Otherwise they certify a phase that no longer exists.

Third: without such a check the method degrades invisibly and in one direction —
towards what is more convenient for the executor. Running costs more than
reading, the browser costs more than running; in the absence of a critic the work
slides towards the cheap while keeping the name of the expensive.

## In practice

- the critic's questions are fixed: **share of new findings · what is not
  covered · where the method is imaginary**;
- the input is the phase's trace, not its conclusions: commands, environments,
  launch counters;
- the critic is last in the phase, and their conclusion is void after any
  additional launches;
- their findings are raised as process tasks rather than filed with product
  findings: different lists, different audiences.

## Where it applies

**Works** for multi-phase audits, long investigations, any work whose method is
declared in advance.

**Does not work** for single-phase work: there is nothing to criticise, the
method is the whole work.

**Sign that it is needed:** the phase is named with an expensive word and its
trace consists of cheap actions.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § in a multi-phase
audit the critic checks the METHOD of its own phase; the 2026-08-10 audit.
Related: [032](032-role-must-run-the-product.md),
[060](060-debrief-every-wave-quality-first.md).
