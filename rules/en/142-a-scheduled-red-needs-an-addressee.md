# A scheduled red needs an addressee, or nobody reads it

**Area.** pipeline, observation

**The rule.** A check that runs on a schedule must, when it fails, **reach a
person** — through an issue, a message, anything addressed. Red on the runs tab
is not an addressee. Until one exists, such a check differs from an unrun one
only by the machine time it bills.

## The incident

The catalogue keeps a "where it applies" summary: it is computed from the
answers of consumer projects rather than maintained by hand. A separate
scheduled run checks that the summary is fresh, daily. Its header says so
outright:

> Red here means one of two things, and both need a human.

The run went red on 23 August and stayed red **every day**: a consumer had
updated its answer while the summary in the repository stayed as it was. By the
time anyone looked, the drift was twenty-four rows of the table — one of which
changed the number of rules the consumer answers for.

**A human spotted it, by glance.** Not a mechanism. Over four days no session
working in the repository noticed the red: sessions go to the tracker, the
rulebook and the changes — precisely where a scheduled failure is not visible.

Tellingly, the first attempt to make the check legible had already been made,
and it **worked as designed**. The error message is detailed, the diff is
printed, the fix command is named in the text. What was missing was not the
wording but the addressee: the text was written somewhere nobody reads.

## Why

**A failure is as visible as it is obstructive.** Red on a change blocks the
merge, sits in front of its author and inconveniences them personally — so it is
fixed the same day. Red on a schedule blocks nothing and belongs to nobody: the
run has no author, no change to hang off, and it lives on a separate tab.

**Hence a skew, and it runs the wrong way.** The more important a check, the
more likely it runs on a schedule: state drift, stale data, someone else's
server going away — everything not tied to a change. So **the least visible
failures belong to the most important checks**.

**Silence is indistinguishable from health.** A green run and an unread red one
look the same — like nothing. It is the same defect as a check without a third
outcome ([075](075-a-guard-that-finds-nothing-must-fail.md)): "could not" and
"all is well" collapse into one state, except here they are collapsed by the
delivery, not by the code.

**Asymmetry of cost.** Adding an addressee costs one step in the run's
definition. Omitting it costs a drift that grows in silence and is found by
accident — that is, the later the less often somebody looks.

## In practice

- the addressee is set up **together with the check**, not after the first
  missed failure: a check without one is unfinished;
- exactly **one** issue is opened, and it is not repeated while it stays open. A
  daily copy in the tracker fixes visibility by the very means that destroys it
  ([051](051-warn-on-likely-block-on-certain.md));
- the issue text carries the fix command, not a description of the symptom: the
  addressee must be able to close it without studying how the run works;
- **a scheduled red does not clear when you fix it** — it clears on the next run
  only. If the next run is a day away, the tab shows a failure that is already
  fixed for a day, and it cannot be told apart from a live one. So such a check
  needs a cheap reason to re-run — a merge into the shared branch, not just the
  schedule;
- the self-check: open the runs tab and look at the schedules. Red for longer
  than one cycle is already an incident.

## Where it applies

**Works** for any automation with no change attached: schedules, periodic state
reconciliation, polling other systems, report builds.

**Does not work** where an addressee already exists: an on-call rotation, an
external alerting system, a run whose failure blocks the release. A second
addressee there produces noise, not visibility.

**Sign of the violation:** a scheduled run has been red for more than one cycle
and the tracker says nothing about it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#77 — four days of daily red and the post-mortem;
`.github/workflows/consumers-sync.yml` — the step "the finding has an
addressee".

Related: [075](075-a-guard-that-finds-nothing-must-fail.md) — "could not read"
must not be indistinguishable from "all is well";
[051](051-warn-on-likely-block-on-certain.md) — why noise destroys visibility
more reliably than silence;
[104](104-event-driven-automation-needs-a-manual-button.md) — an event always
has a manual button; [049](049-derive-state-from-live-artifacts.md) — the
computed state that went stale.