# An expensive run is keyed by its subject, not by the head

**Area.** pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** An expensive run whose verdict depends only on the change's own
diff against the base (an agent's outside review, a long analysis) is keyed by
that diff, not by the head. A new head with the same diff gets the earlier
verdict instead of a new run. And pulling the base into the branch does not
cancel a running expensive run; it waits for its verdict. Otherwise a verdict on
an equal diff is never allowed to exist, and the key has nothing to reuse.

**Portable beyond Claude Code.** partly — keying by subject holds for any
expensive run on any platform; the cost here is minutes of an agent's outside
review, and for an ordinary check run it is often lower than the cost of the
key itself.

## The incident

The mechanisms project, `review.yml` runs on `pull_request` (a project
proposal, ArtVsMark/Engineering-Pipeline-Mechanisms, trail
`scripts/look_mode.py`). Every merge into `main` was pulled by the queue into
open branches, the new head started a new review run, and the group with
`cancel-in-progress` cancelled the running one. Measured 4–7 October 2026, 3.7
days: **291** completed runs, **97** cancelled (33%), **902** minutes inside the
cancelled ones — about **244** a day. The change's own diff usually did not
change on a pull.

**The first measure gave almost nothing**
(ArtVsMark/Engineering-Pipeline-Mechanisms#1161, 6 October): a run is skipped
when the diff against the base equals one already reviewed. The key changed
three hours later (#1164, 6 October 03:34 UTC): patch lines with context,
without the `@@` hunk header lines, and the blob for a file without a patch.
Over a day and a half, 6 October 00:48 to 7 October 16:24 UTC, there were **two**
skips on an equal diff. The pull arrived before the verdict, cancelled the
running review, and the verdict that could have been reused was never born.

**The second measure** (#1194, 7 October): the queue does not pull the head
while a review is running on it — it pulls after the verdict. Final
measurement 7–14 October, 7.2 days: **406** runs, **14** cancelled (3%), about
**28** cancelled minutes a day. **105** skips on an equal diff, about 15 a day;
in a sample of 15 of the 105, every one passed the "diff already reviewed"
step. An average full run is **18.8** minutes, so the skips saved about **275**
minutes a day.

**Only the first measure was measured on its own.** The second was never
switched on alone: what waiting without the key would give is not measured,
and the conclusion about it is reasoning (a new head without the key would
still get a full run).

## Why

**The head is the wrong key for a run that does not read the head.** An
outside review's verdict is a function of the change's diff against the base.
A base pull changes the head and almost never changes that diff, and a key by
head declares it a new subject. Every pull becomes a full run, and with
cancellation by group also a discarded one.

**A key without waiting for the verdict is useless, and this is not obvious.**
Only a verdict that exists can be reused. If a pull cancels the running review,
there is never a verdict on an equal diff, and the key compares the new diff
with nothing. So there are two halves and they are required together: a key by
subject and a queue that waits for the verdict.

The asymmetry of cost sets the form. A key error towards "equal" hands out an
old verdict on a changed subject — a defect the review will miss. An error
towards "not equal" costs one extra run. So the key is built conservatively:
everything that can change the verdict goes into the key; only what the verdict
certainly does not read is dropped (line numbers in hunk headers).

## Practical boundaries

- the key is the change's diff against the base, normalised exactly by what the
  verdict does not read — not the head and not the change number;
- pulling the base into the head waits for the verdict of a running expensive
  run instead of cancelling it;
- the second half is easy to miss: a key without waiting gives skips by ones,
  not by dozens — two in a day and a half for the mechanisms against a hundred
  and five in a week;
- **this does not override 179.** A required check is keyed by the head: its
  subject is the commit that will land in the shared branch, and a verdict
  about another commit is false for it. This rule is about an expensive
  optional run whose verdict does not depend on the head;
- the decision is revisited if the verdict starts reading anything besides the
  diff — the whole base, neighbouring changes, an outside source: then that
  goes into the key.

## Where it applies

**Works** for expensive runs whose verdict depends only on their own diff: an
agent's outside review, a long analysis of a change, with frequent base pulls
by a queue.

**Does not work** for a required check whose subject is a commit (that is 179),
or for a cheap run where the key and its upkeep cost more than a repeated run.
The catalogue has the subject, but a small one: over 9–16 October, 9 of 100
review runs were repeats on the same branch, with an average run of 1.2
minutes — the catalogue's answer says so.

**Sign of a violation:** among the expensive review runs, runs on different
heads of one change with the same diff against the base, or `cancelled` review
runs right after a base pull.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — scripts/look_mode.py

Related: [179](179-cancellation-group-must-name-the-head.md) — the head in the
cancellation group for a required check; here the key for an expensive
optional one, and the boundary between them is stated above.
[020](020-restart-only-the-delta.md) — repeat only what is missing; keying by
subject does this for a run. [052](052-only-the-head-of-the-queue-moves.md) —
the same queue pull that moves the head here.
[078](078-cancelled-is-not-an-error.md) — cancelled is not an error, but a
cancelled expensive run is one paid for and thrown away.
