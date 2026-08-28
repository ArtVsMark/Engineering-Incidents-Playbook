# Cancellation is its own outcome, not a kind of error

**Area.** contracts

**The rule.** Termination by the user's own will gets its own terminal status.
Mixing it with failure is not allowed: the response differs for both machine and
human.

## The incident

At first cancellation was reported as an error with a clarifying message code.
Formally the information was there: the code distinguished the reason. In
practice the distinction was lost at the very first consumer that looked only at
the status.

The difference is fundamental and comes down to two questions:

- **retry or not?** A failure is worth retrying, a cancellation is not.
  Automation that sees "error" dutifully retries what a human just stopped;
- **how to display it?** The interface must present them differently: "it did
  not work" and "you cancelled" are different messages, and the second must not
  look like a breakage.

So cancellation became a separate terminal status while the clarifying message
code was kept — the status speaks to the machine, the message to the human.

## Why

A status is **an instruction to the consumer**, not a description of what
happened. The right set of statuses is determined not by how events differ in
nature but by how the **response** to them differs. Two events with different
responses must have different statuses, even if they are built identically
inside.

Hence the test when adding a new outcome: name what changes in the consumer's
behaviour. If nothing changes, it is a clarification and belongs in the message,
not in the status set. If retrying, display or accounting changes, it needs its
own status.

Second: a cancellation is a failure of neither the solution nor the system.
Counted as an error, it spoils failure statistics and needlessly alarms whoever
watches them.

## In practice

- the set of terminal statuses is enumerated explicitly and in one place;
- each says what the consumer does: retries, displays, counts;
- entering a terminal status stamps the completion time — everything else is
  measured from it;
- the clarifying message code complements the status, it does not replace it.

## Where it applies

**Works** for background jobs, runs, downloads — anything a user can interrupt.

**Does not work** if cancellation does not exist by design — then an extra status
only complicates things.

**Sign of trouble:** automation retries what a human stopped.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/runs.py` (`_STATUSES`),
ArtVsMark/Stepik-Python-Grader#262, ArtVsMark/Stepik-Python-Grader#296. Related:
[056](056-a-signal-states-what-it-does-not-mean.md).