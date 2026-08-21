# A freeze needs a thaw path that does not run through the frozen action

**Area.** automation, pipeline

**The rule.** If a system can freeze itself, it must have a thaw path that does
**not** run through the frozen action. Otherwise the protection turns into a
permanent block at the first flake.

## The incident

The merge queue freezes while the shared branch is red. Correct in itself: while
the base is broken, the next change only adds to the mixture somebody will have
to untangle.

The health of the base was read from a single query: the latest runs on the
shared branch, **filtered to `event = push`**. The logic is transparent and looks
impeccable — a merge is what changes the state of the base, so a run triggered by
a merge is what should prove it healthy.

Then came a single failure: one matrix cell (macOS × 3.12) on a commit that
touched three documentation files and **zero lines of code**. The same cell had
been green on the five preceding commits. A flake, not a breakage.

And there was no way out — all three doors led into the same wall:

- a push to the base only ever happens through a merge, **and merges were
  frozen**;
- the nightly scheduled run and a manual run execute against the same state and
  come back green — but they fall outside the event filter, so the freeze **does
  not see them**;
- re-running the failed run preserves the original event and would have lifted
  the freeze — but it requires CI write access the cloud executor **does not
  have**.

Eight ready changes stood for five hours. The only thing that could lift the
freeze was the action the freeze itself forbids.

## Why

A freeze is a **condition**, and a condition has a source of truth. The mistake
is not that the base was frozen: the freeze did exactly what it was designed to
do. The mistake is that proof of health was accepted **from one event only** —
the very event the freeze blocks. The loop closed not through a defect in the
code but through the **shape of the check**.

Hence the question to ask of every blocking check: **which event clears its
condition, and is that event available while the block is in force?** If the only
such event is the one the block forbids, this is not a protection but a trap, and
it will spring on the first flake rather than on a real breakage.

Second, and this is why such things survive for a long time: **the trap looks
healthy**. There is no error, the automation reports correctly — "the latest run
is red, the queue is frozen" — and from outside it is indistinguishable from
ordinary waiting. The stall is found not by a signal but by the clock: somebody
notices it has been standing too long.

Third: the cost grows silently and not on a single change. A frozen queue
accumulates everything that is ready, and the price of the trap is multiplied by
the number of things waiting.

## In practice

- proof that "the condition is cleared" is accepted from **any equivalent
  source**, not from one event: a scheduled run, a manual run, a re-run — if they
  execute against the same state, they are equivalent;
- freezing automation has a manual trigger
  ([104](104-event-driven-automation-needs-a-manual-button.md)) — and it is
  reachable by whoever is on duty, **including an executor with reduced rights**:
  a button nobody can reach does not open the trap;
- the thaw path is documented next to the freeze: not "CI will go green", but
  which command to run when there is nothing to wait for;
- time spent frozen is measured. A freeze lasting more than an hour with green
  changes queued is a signal of a trap, not of traffic.

## Where it applies

**Works** for any blocking automation with an external condition: a merge queue,
a release pipeline, a degradation flag, an automatic hold on a rollout.

**Does not work** where the condition clears with time — a quiet window, a
timeout, an exponential back-off: there the exit arrives on its own and no
separate path is needed.

**Sign you need it:** the recovery instructions begin with the words "wait until
somebody…".

## Trace

ArtVsMark/Stepik-Python-Grader#1347; related #1326 (the freeze as such — works as
designed), #1344. Related rules:
[104](104-event-driven-automation-needs-a-manual-button.md) — the manual button,
whose absence makes the trap unsolvable;
[109](109-every-exit-from-a-transient-state-must-be-terminal.md) — there the dead
end comes from a bare exit, here from the shape of the condition;
[124](124-rerun-the-minimum-and-record-the-flake.md) — the re-run as diagnosis;
[052](052-only-the-head-of-the-queue-moves.md) — how the queue moves.
