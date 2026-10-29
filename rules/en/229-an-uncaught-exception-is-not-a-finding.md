# An uncaught exception is not a finding: a mechanism's entry point catches everything and reports "did not run"

**Area.** code, diagnostics, reliability

**Tier.** 4 — code and tests

**Refines.** 039

**The rule.** An uncaught exception exits with the interpreter's own code — 1 in
Python — and in a mechanism that has declared 1 as "findings", a crash reads
as "found something". A mechanism's entry point catches any exception and
returns the "did not run" outcome, naming what failed. This is held by a walk
over the tree — every mechanism with outcome 1 has a guarded entry point — not
by each author remembering it.

**Portable beyond Claude Code.** yes — the subject exists for any check whose
exit code a pipeline reads: Python, Node with `process.exit`, a shell script
with `set -e`.

## The incident

**The measurement of the neighbour the proposal came from** (the mechanisms
project). One kind of failure, three times in six weeks, each time caught by an
outside review rather than a gate:

- 17.10.2026 — the push guard exited with a traceback and code 1
  (ArtVsMark/Engineering-Pipeline-Mechanisms#1454);
- 26.10.2026 — the job time-budget guard: an `AttributeError` on an empty
  platform reply and a `KeyError` on a record exited with 1, and 1 there means
  "budget too small" (ArtVsMark/Engineering-Pipeline-Mechanisms#1700);
- 27.10.2026 — a late review found the same kind in two neighbouring guards,
  which the fix for the first had not touched.

**What did not work.** The first fix listed the exceptions to catch: it closed
one form and missed the next. The class was closed by wrapping the entry
point, at first in a single mechanism
(ArtVsMark/Engineering-Pipeline-Mechanisms#1707). A measurement on 28.10.2026,
walking the AST of `scripts/*.py`: 36 mechanisms declare outcome 1, and one
has a guarded entry point. The neighbour's answer to 039 held the three
outcomes with a gate (the outcome is a constant and is exercised), but did not
see that a traceback produces a 1 by itself. The fix is one entry wrapper for
every mechanism and a gate over the tree
(ArtVsMark/Engineering-Pipeline-Mechanisms#1720).

**We have the same thing.** Measured on 29.10.2026 over the catalogue's
`scripts/*.py`: 77 `__main__` entry points, 71 of them declare outcome 1, and
only one (`new_rule.py`) catches an arbitrary exception. A traceback from any
of the other seventy is read by the pipeline as a finding.

## Why

**The trap is visible neither in the code nor in the suite.**
`raise SystemExit(main())` looks right, and the suites stay green until the
traceback happens in production. The exit code is chosen not by the
mechanism's author but by the interpreter, and it picks exactly the code the
mechanism already uses.

**The error costs more in one direction.** "Found" on a broken check sends the
reader to fix something that is not broken, while the real cause — the
exception — goes to the run log nobody reads. "Did not run" on a real finding
costs one rerun. So doubt is resolved in favour of the third outcome.

**A list of exceptions does not close the class.** It catches the forms the
author has already seen, and the next form is a different exception at a
different entry point. The class is closed in one place every entry point
passes through.

## In practice

- the entry point of a mechanism with declared outcome 1 catches any exception
  and exits with the third-outcome code, naming the subject: what was not read
  and where ([158](158-the-third-outcome-names-its-subject.md));
- the catch is a single wrapper for all entry points, not a list of exceptions
  in each;
- a standalone module without shared imports catches the exception in its own
  entry point;
- a walk over the tree holds it, not review: "every mechanism with outcome 1
  has a guarded entry point".

## Where it applies

**Works** for a mechanism whose exit code is read as a verdict and where the
code an uncaught exception produces coincides with one of the declared
outcomes: a gate, a guard, a check in a pipeline step.

**Does not work** for a script whose exit code nobody reads as a verdict: a
builder of derived files, a button, a one-off utility. There the traceback is
an honest failure. **Does not work** either where outcome 1 is not declared
at all: the traceback is then already distinct from every verdict, and that is
the subject of [039](039-three-outcomes-not-two.md), not of this rule.

**Sign of a violation:** a mechanism declares outcome 1 as findings, and its
entry point lets an uncaught exception's traceback out with the same code 1.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — scripts/main_guard.py

Related: [039](039-three-outcomes-not-two.md) — three outcomes; this rule names
where the false 1 comes from; [158](158-the-third-outcome-names-its-subject.md)
— the third outcome names its subject; [145](145-every-declared-outcome-is-run.md)
— a mechanism is run through every outcome, but a traceback never happens in
the suite.
