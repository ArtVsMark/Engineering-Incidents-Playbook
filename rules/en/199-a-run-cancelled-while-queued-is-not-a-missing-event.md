# A run cancelled while queued is not a missing event

**Area.** pipeline, diagnostics

**Tier.** 2 — the pipeline and CI

**The rule.** A mechanism woken by an event and running in a group with
`cancel-in-progress: false` must have a **second source of proof** that the
condition is satisfied — a poll of the state inside the run itself. The event
arrives, but the run does not survive to do the work; from outside that is
indistinguishable from a lost event, and the two are fixed by opposite means.

**Portable beyond Claude Code.** partly — the device "a second source instead of
trusting the event" carries anywhere work is woken from outside. The numbers and
the shape of the cancellation group are tied to this platform.

## The incident

The merge queue was not moving ready changes. From the `head_branch` field of
the child runs it was concluded that the `workflow_run` event **does not arrive**
from change branches — and the fix would have started there.

A check on 10 September refuted that. The queue run followed the completion of
the gates run in **25 cases out of 25**, with a median delay of **2 seconds**.
And a child run's `head_branch` always equals the default branch, because that
is where the workflow file executes: the field was answering a different
question from the one being asked of it.

The real cause was next to it, in the same data: of **120 runs, 67 were
cancelled**, and **45 of those died before starting any work**. The platform
keeps **one** waiting run per group, and every new one evicts the previous. The
survivor is the last one queued — and it comes from whichever run finished last,
which need not find the head ready.

## Why

**A queue eviction and a lost event look identical and are fixed by opposites.**
For a lost event you repair the subscription: widen the trigger, add an event.
Under eviction that makes things **worse** — more events mean more evictions,
and the share of runs surviving to work falls. A diagnosis taken from the
outward symptom leads in precisely the wrong direction here.

**An event reports a moment; the work needs a state.** A run woken by somebody
else's completion learns only that the other run finished, and learns it after
the fact. Whether the head is ready *now* the event does not say and cannot: a
queue of indeterminate length stands between them.

**`cancel-in-progress: false` protects work already started, not the right to be
woken.** The setting reads as "my runs do not cancel each other", and in that
form it is wrong: the *executing* run is not cancelled, but a *waiting* one is
always evicted. The difference shows in the count of cancellations, never in the
declaration.

## In practice

- the second source is a **state poll** at the start of the work: the run asks
  rather than trusting whatever woke it;
- cancelled runs are counted **separately from failed** ones: "cancelled" reads
  as noise in a run summary and therefore goes unread, while here it is the
  subject itself;
- distinguish **cancelled before work** from **cancelled during work**: the
  first is queue eviction, the second is the ordinary replacement of a stale run;
- a scheduled safety net **does not replace** the second source: it clears the
  stall but delays the work by its own period, and it cannot show whether the
  queue was the cause;
- the conclusion "the event does not arrive" is **not drawn from a child run's
  field**: that run has its own frame of reference
  ([044](044-check-the-premise-before-fixing.md)).

## Where it applies

**Works** wherever work is woken by an external event and execution sits in a
group that evicts waiters: a merge queue, a reaction to somebody else's run
finishing, a webhook handler with a concurrency limit.

**Does not work** when runs start immediately and never queue: a second source
is then extra work on every run. **Does not work** as an explanation for any
stall either: count the cancellations first — if there are none, the subject is
something else, and a state poll will not close it.

**Sign of violation:** a mechanism is declared "reacts to an event" while the
share of runs that died before starting work is counted by nobody.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `scripts/automerge.py`

Related: [044](044-check-the-premise-before-fixing.md) — a finding's premise is
checked before it is acted upon: here the wrong premise "the event does not
arrive" would have survived the fix;
[178](178-a-source-mismatch-is-your-reader-until-proven-otherwise.md) — a
mismatch between sources is your reading until proven otherwise, and
`head_branch` was exactly such a reading;
[179](179-cancellation-group-must-name-the-head.md) — the neighbouring half of
the same setting: there the cancellation group confuses heads, here it evicts
waiters.
