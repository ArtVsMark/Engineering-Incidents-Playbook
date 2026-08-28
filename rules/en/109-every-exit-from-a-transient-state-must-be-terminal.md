# Every exit from a transient state must be terminal

**Area.** code, interface

**The rule.** You cannot leave a state of "starting", "stopping" or "checking"
silently. Every branch, including the early ones, must leave a **final** status —
otherwise the system is stuck in the transient state forever.

## The incident

The server control window showed states: "Starting…", "Running", "Stopped". A
monitor waited for the port to answer and moved the state to "Running".

One branch held a **bare return** — for the case where a stop was requested while
the monitor was waiting. It did not change the state, and a stop landing between
the port probe and acquiring the lock left the window in "Starting…" forever.

Then comes a dead end with no exit **by the interface's own design**: "Stop"
already does nothing, "Start" is blocked by the transient state. All the user
could do was close the window.

The fix was one line: set a final status before returning.

## Why

A transient state is a promise that another one will arrive shortly. An exit
branch that does not change the status breaks that promise quietly: no error, a
clean log, an interface that looks alive and simply waits forever.

Such branches appear precisely in the "impossible" cases — races, cancellations,
early returns. The developer writes `return` because there is **nothing to do**
here; they are right about the action and wrong about the status.

Second: transient states usually **block the controls** — buttons greyed out,
restart forbidden. That is correct exactly while the state is temporary. Once
stuck, the block turns from protection into a trap, and the more carefully the
interface is built, the tighter the trap.

## In practice

- enumerate **every** exit branch from the transition, including cancellation,
  race and error, and make sure each sets a final status;
- a bare early return in code that manages state deserves a separate look: it
  almost always skips the status;
- a time bound on the transient state helps: if the final state does not arrive,
  move to "unknown" and unblock the controls;
- the control block is lifted by the same code that set it, not "upon a good
  outcome".

## Where it applies

**Works** for state machines, task states, interface indicators, process
lifecycles.

**Does not work** where there are no transient states: the operation either
completed or did not.

**Sign of trouble:** the only way out of a state is to restart the program.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/launcher.py`,
ArtVsMark/Stepik-Python-Grader#823. Related:
[078](078-cancelled-is-not-an-error.md),
[100](100-two-deadlines-start-and-work.md).