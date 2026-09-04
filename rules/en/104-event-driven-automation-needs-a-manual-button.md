# Event-driven automation needs a manual button

**Area.** CI, automation

**Tier.** 2 — the pipeline and CI

**The rule.** Events get lost. If the only way to start is an event, add a manual
launch — otherwise the only way to wake it becomes a junk change.

## The incident

Checks were started by events: change created, new commit, reopened. Measured
across one session: **four changes out of nine received no checks on creation**.
Draft and ready, different times — no correlation; pushing a commit always
worked, the other events were a lottery.

Without a manual launch the only way to wake the checks was an empty merge of the
shared branch and a push — that is, **a placeholder commit for the sake of a
rerun**, and it stays in the history forever.

Beside it a second defect of the same kind turned up: the set of event types was
not specified explicitly, and the default **does not include** a draft being
marked ready. A change created as a draft received no checks either on creation
or on becoming ready — until the first commit was pushed.

## Why

Event delivery gives no guarantee. Between "something happened" and "the
automation started" lies somebody else's infrastructure, and losses there are not
an anomaly but a statistic. Building the only start path on an unguaranteed
channel means accepting those losses as failures.

A manual launch costs one line and removes a whole class of workarounds.
Workarounds are worse than the loss itself: they leave traces in the history, look
like real work, and over time become a ritual nobody can explain.

Second, on defaults: the default event set was not assembled for your process. It
covers the common case and silently misses the rest — and that shows up not as a
failure but as **an absence of a run**, that is, as silence.

## In practice

- a manual launch with a target selector is mandatory, not a debugging
  convenience;
- the event set is enumerated explicitly even when it matches the default: an
  explicit list survives a change of defaults;
- an absent run is tracked alongside a failed one: "no checks" and "red checks"
  are different states;
- a workaround that became a habit is a sign of a missing button, not a feature
  of the process.

## Where it applies

**Works** for anything triggered by webhooks, message queues, change
subscriptions.

**Does not work** for scheduled automation — there a miss is visible by time.

**Sign that it is needed:** the history contains changes made in order to trigger
a rerun.

## Trace

ArtVsMark/Stepik-Python-Grader — `.github/workflows/ci.yml`
(ArtVsMark/Stepik-Python-Grader#1095: four of nine;
ArtVsMark/Stepik-Python-Grader#988: `ready_for_review` outside the default).
Related: [010](010-empty-checklist-is-not-green.md),
[075](075-a-guard-that-finds-nothing-must-fail.md),
[126](126-a-freeze-needs-a-thaw-path.md) — the block this button opens.