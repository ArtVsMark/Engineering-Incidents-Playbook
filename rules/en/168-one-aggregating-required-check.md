# One required check, with a constant name, and not assembled through `needs:`

**Area.** pipeline, CI

**The rule.** Branch protection requires checks **by name**, and the name is
entered verbatim into a setting — outside the repository and outside review.
That yields two silent failures. First: a name nobody creates puts the change
into permanent waiting — which is how a typo in the setting behaves, and equally
how a renamed matrix job behaves. Second: protection counts a **skipped** job as
passed, so an aggregator assembled through `needs:` does not go red when a
dependency fails — it is skipped, and therefore permits the merge in exactly the
case where it must forbid it. Hence: **exactly one** required check, with a
constant name, not depending on other jobs through `needs:`, always reaching a
verdict, and its name matched against the setting by a test.

**Portable beyond Claude Code.** partly — "one constant name" holds on any
platform; "skipped counts as passed" is a property of GitHub branch protection,
and where a platform treats a skip as a failure the second half is redundant.

## The incident

The owner enabled a ruleset on the consumer's main branch with no bypasses and a
single required context — `PR check`. No check by that name existed in the
repository: the jobs were called `гейты · ubuntu-latest · python 3.13` (nine
matrix cells), "zone, type and link to a task", "an entry exists and it is in the
project's language".

Both open changes carried eleven green checks with unique names and
`mergeable: true` — alongside `mergeable_state: blocked`. The pipeline stopped
merging anything at all, and that state went red **nowhere**: the checks
themselves were green, and the queue kept reporting "ready".

The trap had been named in advance, in the task about the protection itself:
"matrix job names enter the required list verbatim; renaming breaks the link".
They walked into it on the very first enabling anyway — because a list of eleven
names was matched against the tree nowhere.

## Why

The name of a required check is a link held by an **external setting**. Review
does not see it, renaming does not break it, and no job verifies it: the two
sides drifting apart produces no red — it produces **waiting**, and waiting is
indistinguishable from "checks are still running".

The second half — about `needs:` — is subtler and more dangerous. The natural
thought "I'll assemble an aggregator out of the dependencies" achieves the exact
opposite: a failed dependency turns the aggregator into `skipped`, and branch
protection counts a skip as a pass. So in the normal case the aggregator is green
and decides nothing, and in the failure case it is skipped and permits the merge
([010](010-empty-checklist-is-not-green.md): an empty checklist is not green, and
here it empties precisely during the failure).

Hence the shape of the fix: **one** job with a constant name that itself asks the
platform for the checks on the change's head and goes green only when all the
others are green. It cannot be built with `needs:` for a second reason too: the
gates live in separate workflows deliberately — the matrix must not re-run when a
label is attached, while the label gates must.

## In practice

- one required name, constant; matrix job names never enter the list;
- the aggregator reads the **checks on the head**, not its dependencies, and
  reaches a verdict whatever its neighbours did;
- the name's match with the setting is held by a test, not by memory: the setting
  lives outside the tree, and matching it against the tree is a job's duty;
- permanent waiting is spotted through `mergeable_state`, not through the colour
  of the checks: that is where it shows.

## Where it applies

**Works** wherever merging is held by branch protection with a list of required
checks by name.

**Does not work** with no protection at all — there is no subject and nothing to
enforce it with; [010](010-empty-checklist-is-not-green.md) governs there. Nor
does it work on a platform where a skipped job counts as not passed: `needs:` is
safe there, and only the constant-name requirement remains.

**Sign of violation:** the required-checks list is longer than one name — or it
contains a name assembled from matrix parameters.

## Trace

ArtVsMark/Claude-Code_Usage-Token#6 — scripts/pr_check.py,
.github/workflows/pr-check.yml

Related: [010](010-empty-checklist-is-not-green.md) — an empty checklist is not
green; 168 names the way a checklist empties unnoticed.
[171](171-the-reference-set-comes-from-the-tree-under-test.md) — the reference
set comes from the tree under test; the same trap one floor down.
[051](051-warn-on-likely-block-on-certain.md) — warn on the likely, refuse on the
certain.
