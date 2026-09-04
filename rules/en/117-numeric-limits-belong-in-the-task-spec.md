# An executor's brief carries numeric limits

**Area.** parallel work

**Tier.** 2 — the pipeline and CI

**The rule.** Numbers go into the brief: a size limit for every field of the
answer, a budget of tool calls, a list of file types that must not be opened.
Without numbers the executor chooses them itself — and chooses badly.

## The incident

A wave of parallel executors broke off the same way every time: the work was done,
transcripts ran to 180–380 kilobytes, and the final answer **never arrived**. The
journal held only a start marker and not a single result.

Three numeric measures produced measurable effects, each its own:

| Measure | Effect |
|---|---|
| limits on string length and element counts in the answer schema | **half** the spending per slice |
| a budget of tool calls (about 25) stated in the brief | a wave half as expensive as the previous one for the same output |
| a ban on opening binary files (images, fonts) | removed hangs with no progress |

The last deserves its own mention: one executor hung reading a binary file —
**180 seconds, six times in a row**, without a single sign of progress. It neither
failed nor finished; it simply consumed time.

## Why

An executor that was not given a boundary behaves reasonably **in its own way**:
it writes in as much detail as it can, and it opens everything that seems
relevant. Both habits are useful in a small task and destructive in a large one —
and only whoever set the task can see the difference.

The limit on **answer size** lands in the most expensive place: the failure comes
at delivery, when the work is already done and paid for. Constraining the fields
reduces not quality but the probability of losing everything.

The call budget works differently — it forces **choosing**. Without it the
executor walks everything in arbitrary order; with it, it starts from what
matters, because it knows the number of attempts is finite.

The file-type bans are about what the executor cannot know in advance: which
inputs are useless and expensive for it. That is the host's knowledge, and it has
to be handed over explicitly.

## In practice

- the numbers live **in the brief**, not in the head of whoever wrote it;
- every string field of the answer has a length limit, every list has bounds on
  element count;
- the call budget is stated as a number, not as the word "sparingly";
- the bans enumerate types and say **what to do instead** ("take the file's
  description from the adjacent text");
- the numbers come from measuring the previous wave and are adjusted, rather than
  invented once and for all.

## Where it applies

**Works** for parallel executors with a cap on answer size and a charge per call.

**Does not work** for solitary interactive work where a human sets the bounds as
they go.

**Sign that it is needed:** answers are lost at delivery or arrive truncated.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/archive/audit-2026-07-30-full-roles.md`
(the "what worked" table), `docs/agent/multiagent.md`. Related:
[034](034-small-zone-per-executor.md),
[061](061-environment-bans-belong-in-the-task.md).