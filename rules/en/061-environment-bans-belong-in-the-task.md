# Environment prohibitions go into the task text, never implied

**Area.** parallel work

**The rule.** An executor that will run the product receives the list of
prohibitions **in the task text**. It cannot see what the host knows, and it
will hit a guard without understanding what it hit.

## The incident

Two executors were stopped by a guard mid-work. One was creating a fake file in
a temporary directory under a name reserved for secrets. The other was
overriding the home directory to isolate its run.

Both prohibitions are justified and both are in the project's rules. But the
executors did not know about them — and lost **all** their work, not just the
last step.

A second effect surfaced after the very first run wave: **13 junk files** were
left in the repository root. Exactly what will happen to a user running the
checker from their own project folder — so the executor's side effect turned out
to be an unnoticed product defect as well.

Hence a block of prohibitions in every run task: do not create files with
reserved names, not even fake ones; do not override environment variables that
define the home directory; isolation comes from a working directory and the
product's own parameters; do not write into the repository; nothing interactive
without an input stream; every command gets a time limit; if you started a
process, kill it at the end.

## Why

An executor has access to the task text, not to the host's context. A rule
written into the project's rulebook and absent from the task does not exist for
it — and a guard that fires mid-work differs from an ordinary error in that it
**cancels what was already done**.

Second: a list of prohibitions is cheaper than any alternative. It takes seven
lines in the task and prevents the loss of a whole wave, while explaining
afterwards why the work does not count costs more.

Third, and not obvious: **junk left by an executor predicts junk left for the
user**. A run wave is the first honest answer to what the product leaves behind
in somebody else's directory, and its side effects are worth reading as findings
rather than as untidiness.

## In practice

- the prohibitions are a **shared block** inserted into every run task, not
  paraphrased afresh each time;
- each prohibition says **what to do instead** ("isolation comes from a working
  directory"), or the executor will invent a workaround;
- cleaning up after yourself is an item in the task, not implied courtesy;
- after the wave the directory is inspected for traces, and whatever is found is
  raised as a finding.

## Where it applies

**Works** for executors that run the product or commands in a shared working
environment.

**Does not work** for purely reading tasks — there prohibitions only lengthen
the brief.

**Sign of a breach:** an executor is stopped by a guard its task never
mentioned.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § environment
prohibitions go straight into the prompt of run agents. Related:
[034](034-small-zone-per-executor.md).