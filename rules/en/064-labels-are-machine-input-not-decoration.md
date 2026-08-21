# Labels are machine input, not decoration

**The rule.** Classifying a task and a change is mandatory and machine-checked.
Closing the task, queue order and the zone of work all depend on it — so a
missing label breaks behaviour, not presentation.

## The incident

The measurement the rule grew from: of twelve open changes, **four** had labels,
and four had a link to a task. In other words **the machine labelled more
diligently than the human**: everything applied by automation was in place, and
everything depending on discipline was missing on two thirds.

The consequences are not cosmetic:

- a change without a link line **does not close its task** on merge — the tracker
  starts lying, and the task hangs open after it is done;
- queue priority is inherited through the same link — without it, important work
  travels as ordinary;
- the zone of work is invisible until you read the diff, which is the most
  expensive step.

So the requirement became a check: the gate rejects and **names what exactly is
missing**. An explicit exemption is provided — a line saying "no task, because…"
— and that too is a filled field, not an omission.

## Why

A label is valuable not for what it describes but because **machinery reads it**.
While classification is a matter of taste it gets filled in when there is time —
that is, never. As soon as the outcome depends on it, an omission becomes an
error rather than carelessness.

Second, important for ordering: **labels of different natures must not be
mixed**. Some describe content — zone, type of work, link to a task; the author
applies those. Others drive the pipeline — "merge when green", "hold", "needs
rebase"; automation applies those, and demanding them from a human means
breaking the machinery by hand.

Third: the rule needs an exception for outsiders. An external contributor is not
obliged to know the local label system — for them it is a **warning**, and the
merger fills in what is missing.

## In practice

- the gate names the missing item individually, rather than answering "formatted
  incorrectly";
- the explicit exemption is a filled field with a reason, not emptiness;
- the split between content labels and pipeline labels is written down, or people
  start duplicating the automation by hand;
- for an external contributor the rule is soft, and that is said out loud.

## Where it applies

**Works** when automation depends on the classification: closing, routing,
priority, reporting.

**Does not work** if nobody reads the labels — then it is more honest to abolish
them than to demand them.

**Sign of trouble:** labels are reliably present where a machine applies them and
absent where a human does.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § labels when raising an issue;
#1329. Related: [053](053-queue-order-is-a-rule-not-arrival.md),
[002](002-rule-without-mechanism.md).
