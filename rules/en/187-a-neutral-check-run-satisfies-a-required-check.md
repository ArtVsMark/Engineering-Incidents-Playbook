# A required check is satisfied by any record bearing its name, skipped ones included

**Area.** pipeline, reliability

**Tier.** 2 — the pipeline and CI

**The rule.** Branch protection matches the NAME of a check record, not its
conclusion: a neutral one — skipped — counts exactly as much as a successful
one. So no more than one live record with a required check's name may remain on
a head. A mechanism that "simply does no work" on some events still creates the
record: a job's condition is evaluated AFTER the job is created. Such a
mechanism must either not fire at all, or carry a different name, or evict the
previous record by cancelling it — a cancelled record holds the merge, a skipped
one does not.

**Portable beyond Claude Code.** partly — the rule describes how one platform's
branch protection behaves; on a platform with different semantics for required
checks the subject disappears, but the question "what counts as the requirement
being met" survives anywhere a requirement is matched by name.

## The incident

A profile showcase, 7 September 2026. Change #140 merged with its required check
RED. The failing run finished at 09:30:32; the merge went through at 09:52:14 —
twenty-two minutes later, so not an event race.

Three records named `PR check` sat on the head: `failure`, `skipped` and
`cancelled`. Branch protection considered the requirement met.

Both halves were deliberate fixes for earlier incidents, and each is correct on
its own:

- the job's `if` condition was added so the run would not wake on a pipeline
  label — it does not change classification, and building because of it is
  waste;
- a separate concurrency group was added precisely so label events would NOT
  cancel the real check: before that, six of eight runs were being cancelled
  (#100, #103).

Together they switched the required check off entirely: skipping by condition
left a `skipped` record, and the separated groups let records pile up side by
side instead of evicting one another.

The only way to notice was to compare timestamps — the check list looked like an
ordinary scattering of crosses.

## Why

A job's `if` does not prevent it from appearing in the check list: the platform
creates the job, evaluates the condition, and leaves a record with status
"skipped". To branch protection "skipped" is not a missing answer but a neutral
one, and it accepts neutral.

Hence the asymmetry that makes the defect invisible: CANCELLING holds the merge,
SKIPPING releases it. Two operations that look equally harmless — "this run
wasn't needed" — differ in exactly the way that matters.

The danger accumulates by addition. Each half is noise removal on its own, and
each is backed by its own measurement. What must be checked is not a half but
the result: how many live records with the required check's name remain on the
head.

## In practice

- exactly ONE live record with a required check's name remains on a head;
- a job you want to skip conditionally gets a different name, or is not started
  by the event at all — filter the event, do not condition the job;
- set up the concurrency group so a new record evicts the previous one by
  cancellation rather than lying down beside it;
- a best-effort channel is exempt — but when you promote one to required, the
  job's condition is the first thing to remove.

## Where it applies

**Works** wherever a merge is held by a check matched by NAME: GitHub branch
protection, and any system where the requirement is stated as a title rather
than an outcome.

**Does not work** where the requirement names a specific run's outcome, or where
a human holds the merge. Nor does it apply to best-effort channels: their record
holds nothing in any status, so the count is irrelevant there.

**Sign of violation:** more than one record with a required check's name on a
single head, at least one of them `skipped`.

## Trace

ArtVsMark/ArtVsMark#141 — the `if` skip removed, the concurrency group reduced
to one per head; the gate that demanded a copy of the label list stopped
demanding it when no filter is present

ArtVsMark/Engineering-Incidents-Playbook — `.github/workflows/ci.yml`: the
`catalogue` job carries no condition, and a measurement across the four most
recent changes found one record per head. `review.yml` does carry one — which is
exactly the mine that goes off if the external review is ever made required

Related: [179](179-cancellation-group-must-name-the-head.md) — there the cancel
group is named by the head so a run on the current head is not evicted by a
stale one; here is the other half: groups must not be separated all the way
either; [084](084-best-effort-channels-never-block-the-main-path.md) — a
best-effort channel holds no merge and is therefore exempt;
[053](053-queue-order-is-a-rule-not-arrival.md) — a red base freezes the queue,
whereas here the red never reached it.
