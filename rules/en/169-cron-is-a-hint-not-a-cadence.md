# A platform schedule is a hint, not a cadence, and a safety net needs a measurement

**Area.** automation, CI

**Tier.** 2 — the pipeline and CI

**The rule.** A platform scheduler says "sometime", not "every half hour". So a
mechanism that must fire within minutes cannot be backed by a schedule, and the
reasoning "if the event is lost, the schedule will pick it up" is wrong by
construction. The general part is wider than the scheduler: a mechanism declared
to be a **safety net** must have a measurement of how often it actually fires.
Until that measurement exists, the primary path is built as if the net were not
there, and the comment beside it states what was observed, not what was
intended.

**Portable beyond Claude Code.** partly — the numbers belong to the GitHub
Actions scheduler; the demand that a safety net be measured carries anywhere,
including retries and queues with delayed delivery.

## The incident

The consumer's merge queue woke in two ways: on an event from the checks job, and
on the schedule `13,43 * * * *`. The schedule was introduced precisely as a
safety net — "event delivery is not guaranteed, and a lost event would mean a
green change standing forever" — and that wording sat in the file's header.
Relying on it, the event list was made narrow: a single workflow name.

When an aggregating required check was added to the project, the last thing to go
green on a change became that new workflow, which was not in the event list. The
queue stopped seeing the moment of readiness at all.

The safety net was then supposed to fire. First day's measurement: of twenty-one
queue passes, twenty-one arrived by event and one by the manual button; by
schedule — **zero**, even though the file had been on the main branch since
09:10 and firings were expected at 09:13, 09:43, 10:13, 10:43 and 11:13. A ready
change stood for fifty minutes, and the queue was moved by hand.

A day later the measurement was repeated, and it **corrected the conclusion**.
The schedule does not "fail to work" — it works five to six times less often than
requested: `13,43 * * * *` promises seventy-two firings over thirty-six hours,
ten happened, the intervals ran from 1 h 56 min to 5 h 48 min, and not one landed
on the requested minute. A neighbouring daily schedule in the same repository was
five to seven hours late on all four occasions.

The first edition of this record claimed "it never fired once". On the first
day's data that was a correct observation and a false conclusion; it was fixed
the same way it was obtained — by measurement.

## Why

A platform schedule is not a timer but a request into a shared queue: execution
depends on load, and the promised minute is guaranteed by nothing. A mechanism
whose subject lives for minutes is not backed by such a request — it is
**replaced by nothing**.

The costliest part is not the delay itself but that a safety net changes
decisions about the **primary** path. The event list was narrowed exactly because
"worst case, the schedule will pick it up". So an unverified net did not merely
fail to fire — it paid for the narrowing of the primary path
([139](139-a-mechanism-is-confirmed-by-a-run.md): a mechanism is confirmed by a
run, not by reading).

And the third layer, for which this record was rewritten: a conclusion drawn from
the first day is a hypothesis too. "It never fires" would have been written into
the code and would have proved false a day later, dragging a sound rule down with
it ([055](055-your-own-expectations-are-a-hypothesis.md)).

## In practice

- what must fire within minutes is not backed by a schedule;
- a safety net has a counter: how many passes arrived from each source —
  otherwise "it works" rests on faith;
- the event list is made wide **on the merits**, not narrow "because of the net";
- the manual button
  ([104](104-event-driven-automation-needs-a-manual-button.md)) is a human's
  lever, not a safety net: it does not fire on its own;
- a conclusion from a single day is re-measured before it is written into a
  comment.

## Where it applies

**Works** for mechanisms with a short deadline: a merge queue, a response to an
event, watch duty over the main branch.

**Does not work** where the subject is itself daily: a nightly digest, a weekly
report, a monthly export. Hours of lateness change nothing there, and a schedule
is exactly the right instrument.

**Sign of violation:** the file header says "if the event is lost the schedule
will pick it up", and nobody has counted how often the schedule fired.

## Trace

ArtVsMark/Claude-Code_Usage-Token#43 — .github/workflows/merge-queue.yml, the
`on.workflow_run` block; re-measured on 2 September

Related: [142](142-a-scheduled-red-needs-an-addressee.md) — a scheduled red needs
an addressee; 169 is about the schedule itself: it also arrives later than
promised.
[139](139-a-mechanism-is-confirmed-by-a-run.md) — a mechanism is confirmed by a
run.
[055](055-your-own-expectations-are-a-hypothesis.md) — your own expectation
proves nothing, including your expectation of your own measurement.
[104](104-event-driven-automation-needs-a-manual-button.md) — event-driven
automation needs a manual button.
