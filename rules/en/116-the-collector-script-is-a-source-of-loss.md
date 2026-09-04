# The collector script is also a source of loss, and it has its own reconciliation

**Area.** parallel work

**Tier.** 2 — the pipeline and CI

**The rule.** The script that assembles the results of parallel work is verified
alongside the work itself. The mandatory reconciliation is **count in against
count out**; a mismatch stops the assembly.

## The incident

One wave's intermediate file was **overwritten with an empty one** when the same
script was run again on another wave: the output file name did not depend on the
wave.

**18 security findings** dropped out of the register. No error, no warning — the
script succeeded on both input and output.

It was discovered by the only means available: a mismatch of numbers — **192
verdicts against 174 findings**. The verdicts came from another source, and only
their disagreement with the finding count revealed the loss.

The conclusion recorded at the time: reconciling "number of findings equals
number of verdicts" is a mandatory assembly step, not a one-off check when
something feels wrong.

## Why

Attention concentrates on the executors: they are expensive, they err, they get
restarted. The collector looks like plumbing — thirty lines, reads and writes
files. That is exactly why nobody verifies it, and it loses things **silently and
in batches**.

Losses in assembly have a nasty property: they are **invisible from inside the
result**. A report of 174 findings looks exactly as convincing as one of 192;
nothing is empty, nothing is broken, the links work. The only tell is the count,
and it has to be computed deliberately.

Hence the general point: any pipeline needs a **count invariant** running through
every stage. It is cheap, checked in one line, and catches a whole class of defect
for which no other signal exists.

## In practice

- intermediate file names include a step identifier: otherwise a repeat run
  overwrites somebody else's;
- writing an intermediate result does not overwrite a non-empty file without
  explicit permission;
- the count reconciliation runs **before** output, and a mismatch is a failure,
  not a warning;
- the collector has its own tests: at minimum for empty input and for a repeat
  run;
- the report prints how many units entered and how many left at each stage.

## Where it applies

**Works** for assembling results of parallel work, merging reports, data
processing pipelines.

**Does not work** where a stage filters deliberately: there you reconcile not
equality but "in = out + dropped, and the dropped are named".

**Sign of trouble:** two numbers describing the same set do not agree.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/archive/audit-2026-07-30-full-roles.md` §
two more lessons (192 verdicts against 174 findings). Related:
[016](016-no-silent-truncation.md), [009](009-count-unique-not-total.md).