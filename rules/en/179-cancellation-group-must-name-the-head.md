# A cancellation group must name the head, not just the change number

**Area.** pipeline, CI, concurrency

**Tier.** 2 — the pipeline and CI

**The rule.** A `concurrency` group that **cancels** a previous run must carry
in its name the commit that run is checking, not merely the change number or a
ref to it. Otherwise runs on **different** commits land in one group, and the
one evicted may be the newer: the platform delivers events out of the order the
commits were made, and the head is taken from the event payload. The last word
then belongs to a run on a stale commit, while the current head has no required
check at all — and nothing can create one any more, because a new run is born
only from a new event. The other half is mandatory: the head is **added** to the
group and cancellation is not switched off — duplicates on one head still need
suppressing.

**Portable beyond Claude Code.** partly — "cancel only your own generation" holds
for any run system; the binding to an event payload and the endless wait for a
name are properties of GitHub Actions together with branch protection.

## The incident

Change #87 in `Claude-Code_Usage-Token`, 3 September, 09:22:32 → 09:24:03.
**Four** events arrived within **35 seconds**: `opened`, two `labeled`, and a
`synchronize` from the merge queue pulling in the shared branch. **Five** runs of
the required check, group `pr-check-87`, `cancel-in-progress: true`.

Delivery order did not match commit order: a `labeled` queued before the
`synchronize` was delivered after it and carried head `1e9cce5`, stale by then —
the change's head was already `4e596cc`. Run 177 on the current head was
cancelled by run 178 on the stale one.

**Run 178 behaved correctly and went red honestly:** it saw that the gate run on
its commit was cancelled and refused to count `cancelled` as success. What was
wrong was not the verdict but the commit it was passed on.

Result: no required check on the current head, branch protection waiting for a
name nobody will create; a plausible red hanging on the stale one. Automation
does not leave this state: labels are set, there are no pushes, the queue has
already pulled the branch in — there will be no more events. It was unjammed by
hand, by re-running the three cancelled runs on the current head.

**Measured across the tree:** the defect was present in **all four** of the
project's `pull_request` runs, not one.

## Why

A cancellation group answers the question "which run is stale", and it carries
one silent assumption: **arrived later means newer**. That is false, because the
group is keyed by the change number while what is checked is a commit; the
number does not change over the life of the change, the commit does, and the
relation "newer" is defined only over commits. All the group knows about a run's
generation is the delivery time of an event — which the platform does not order.

The asymmetry of price fixes the shape of the rule. A redundant run on one head
costs a minute of machine time. A cancelled run on the **current** head costs an
exit from automation: no required check with that name will appear until a new
event happens, and there will be no more events — labels are set, there are no
pushes. That is not "slower", that is a **dead end only a human leaves**.

Hence the head is added and cancellation is kept: switching it off would pay a
permanent price for a rare case, whereas adding the head makes the group exactly
what it was pretending to be — the name of a generation.

The most expensive part of the incident is worth remembering separately: **the
red was plausible**. The run on the stale head behaved correctly and refused to
count a cancellation as success — that is, the mechanism built to catch exactly
that lie fired, and still pointed at the wrong commit. A verdict without the
commit it was passed on is not verifiable.

## Practical boundaries

- every group with `cancel-in-progress: true` names the head:
  `${{ github.event.pull_request.head.sha || github.sha }}`;
- easy to miss: `github.ref` is **not** the head — on `pull_request` it is
  `refs/pull/N/merge`, identical for every event of that change;
- a group with `cancel-in-progress: false` is out of scope: it evicts nothing,
  and a head in its name would only fragment the very queue it exists to
  assemble (that is how our `automerge` and `thaw` are built);
- revisit the decision if the platform starts ordering delivery by commit — the
  assumption "arrived later, therefore newer" would then be true.

## Where it applies

**Works** for runs that cancel their predecessors where the subject under check
is a specific commit: change gates, builds, the required check.

**Does not work** where the subject is not a commit but **state**: a run
rebuilding a showcase or a summary from the shared branch must suppress the
whole older generation, and a head in the group would bring back a race between
writers. Ours is `badges`.

**Sign of violation:** the change's run list holds a `cancelled` on a head that
**is the current one**, with a `completed` on the previous head beside it.

## Trace

`scripts/concurrency_head.py` at the consumer; change
ArtVsMark/Claude-Code_Usage-Token#87, 3 September.

Related: [168](168-one-aggregating-required-check.md) — the same outcome,
"protection waits for a name nobody will create", from a different cause: there
the name is never created by configuration, here by cancellation.
[052](052-only-the-head-of-the-queue-moves.md) — about the same `synchronize`
from the queue that moved the head here.
[139](139-a-mechanism-is-confirmed-by-a-run.md) — a verdict is confirmed by a
run, and the run still has to be tied to a commit.

[078](078-cancelled-is-not-an-error.md) — there is no contradiction here, and it is worth saying out
loud: "a cancellation is not an error" does not mean "a cancellation is a
success". The run in the incident refused to count `cancelled` as success and
was right; what was wrong was the commit the verdict was passed on.
