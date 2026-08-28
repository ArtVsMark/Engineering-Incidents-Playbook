# Debrief after every wave, and quality matters more than mechanics

**Area.** parallel work

**The rule.** The next wave launches only after the previous one is reviewed,
along two axes: who fell over — and **what came out**. The second axis matters
more.

## The incident

Counting successes alone turned out to be insufficient. Five "successfully
completed" executors are perfectly capable of producing coherent rubbish: a
retelling of what is already written, forbidden markup, filler, wrong facts —
all of it reported as "done".

Across four waves in a row this is discovered **at the very end**, when hundreds
of content units are already spoiled. The mechanical axis stays green the whole
time: as many launches as planned, no failures, no delta to collect.

Hence the order of the debrief: mechanics first — who fell over and why, collect
the delta up to a full set. Then quality — **read a sample of the actual output**
and compare it with the task. If the sample fails, the task is edited first and
only then is the wave rerun.

## Why

Successful completion is a property of the process, not of the result. An
executor that misread the task completes successfully in exactly the same way as
one that read it correctly; the difference is visible only in the text returned.

An error in the task is **multiplied by the wave**. One misunderstood point
produces five identically spoiled results in one launch and twenty across four.
So checking a sample after the first wave costs less than the whole job, and
after the fourth it costs more.

The order "fix the task, then rerun" is not a formality: rerunning with the same
task reproduces the same error, only for fresh money.

## In practice

- the sample is read **in full**, not skimmed: compared with the task point by
  point;
- four things are checked: is it a retelling, is any forbidden format present,
  is it filler, are the facts right;
- the sample size is at least one result per executor in the first wave; later it
  can be less frequent, but never "never";
- a discovered task error stops the next wave; it is not a note for later.

## Where it applies

**Works** for any parallel generation whose output is text or code.

**Does not work** where the result is fully machine-checkable (the test passes or
it does not) — there the mechanical axis suffices.

**Sign of a breach:** output quality is first assessed after the last wave.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § debrief after
EVERY wave. Related: [031](031-waves-not-salvos.md),
[020](020-restart-only-the-delta.md).