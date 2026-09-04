# A check has three outcomes, not two

**Area.** CI, reliability

**Tier.** 2 — the pipeline and CI

**The rule.** "Clean", "found a problem" and **"the check did not run"** are
three different outcomes with three different responses. The third is told apart
by the presence of a result, not by an exit code.

**Portable beyond Claude Code.** yes — any checker needs three outcomes, and the remedy is the same: the third is told apart by the presence of a result, not by an exit code.

## The incident

The dependency audit exited non-zero both when it found a vulnerability and when
it **fell over itself** — the index would not resolve, the network dropped, the
advisory database did not answer. While the step judged by exit code, both cases
printed the same thing: "vulnerability found".

The job was non-blocking, so a silent failure of the tool looked exactly like a
clean result. In other words, **a broken check and a successful check produced
the same picture**.

## Why

The difference leads to different actions. "Checked and clean" closes the
question. "Could not check" means that today we **know nothing** about the
subject — and that is not softer than a finding, it is worse: a finding is
visible, ignorance is not.

Telling them apart by exit code is impossible, because the code for a crash and
the code for a finding coincide. What distinguishes them is **the artefact**:
the tool is asked to write its report to a file, and a separate parser names the
outcome by the presence and readability of that report — a crash leaves no
report.

The parsing lives in a script, not a line of build config: a script has tests.
Otherwise you get one more gate, green regardless of whether it works.

## The same skew in exit codes

A second case of the same shape, this time on the checked side. The tool that
grades solutions returned zero both on success and when **there was nothing to
check**: file not found, no solutions, empty case set. A gate went green on an
empty set — that is, it failed exactly when it was needed.

The difference leads to different human actions: "the checks failed" means fix
the solution, "there is nothing to check" means fix the environment — the task
did not download, or the directory is wrong. Hence a separate exit code, rather
than a clarification in the text.

The flip side of the same decision: modes with no verdict of "right or wrong"
(comparison, speed measurement) always exit zero — and that is stated plainly,
so the exit code is not read as a grade.

## In practice

- the three outcomes are named explicitly, each with its own message: `0` ran
  and clean, `1` findings with a count, `2` did not run;
- "did not run" never stays silent: the warning is printed even for a
  non-blocking job;
- the outcome signal is a **by-product of the work** (a report, an artefact, a
  record), not the exit code, if the code is overloaded;
- the parser has tests of its own.

## Where it applies

**Works** for any automatic check whose failure does not break the build:
scanners, linters, metric publication, external APIs.

**Does not work** where the tool honestly distinguishes codes itself — then the
codes are enough.

**Sign of trouble:** from the log you cannot tell "the check passed and all is
well" from "the check never started".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/supply-chain.md` § three outcomes,
not two. Related: [010](010-empty-checklist-is-not-green.md) — an empty list of
checks.