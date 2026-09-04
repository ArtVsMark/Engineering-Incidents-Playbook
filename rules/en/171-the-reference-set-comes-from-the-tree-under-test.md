# The reference set comes from the tree under test, not from the main branch

**Area.** gates, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** The reference a change is compared against comes from **the tree of
that same change**. A reference taken from the main branch arrives from the past
and makes unresolvable exactly the class of changes that alters the reference
itself: for the reference to update, the change must first land on the main
branch, and it cannot land — the check is red. The circle closes, and the only
way out is by hand, by lifting the protection. Sign that the rule applies: the
check compares a **composition** — job names, a file set, a list of keys — and
the source of that composition lies outside the change under test.

**Portable beyond Claude Code.** yes — the subject belongs to any composition
check: a schema comparison, a list of exported names, a set of required files.

## The incident

The consumer's required branch check compared the job names on a change against a
reference — the names from the last run on the main branch. It worked while the
matrix composition stayed put.

Reproduced on forged data: a change raising Python from 3.13 to 3.14 produces the
names `гейты · ubuntu-latest · python 3.14`, the reference demands `3.13`, and
the verdict is "jobs not created". And it is **permanent**: the new names reach
the reference only after a merge. The check's context was required and the
ruleset had no bypasses, so the only way out would have been to lift protection
from the main branch by hand.

The trap had already been named in the task about the protection itself — "matrix
job names enter the required list verbatim, renaming breaks the link" — and it
reappeared one floor down, inside the reference.

The fix: ask the platform for the runs **on the change's head**, and read the
required composition from `.github/workflows/` of that same tree; matching goes
by file path, not by job name.

## Why

The reference is part of what is under test, not an external truth. Taken from
the main branch, the check compares the change not against its own declaration
but against the project's past state — and therefore answers correctly only for
changes that leave the composition alone.

The class of failure here is not a "false positive" but a **deadlock**. An
ordinary false red is cleared by editing the change; this one is cleared by
nothing inside the change, because the required condition becomes reachable only
after the merge. The cost is asymmetric to the limit: to make a change to the
composition you must weaken the protection — a broken gate is paid for by
removing the gate.

Hence the second half of the fix — matching by **file path** rather than by job
name: a name is assembled from matrix parameters and moves with them, while a
path belongs to the tree and moves only when that tree is edited
([049](049-derive-state-from-live-artifacts.md)).

## In practice

- read the composition from the change's tree: `.github/workflows/`, the
  manifest, the schema — whatever the change may fix along with itself;
- match on a stable key — a file path, not a name assembled from parameters;
- ask the platform for **state** (the runs on the head), not for composition:
  state is external by definition;
- an external setting is matched the other way round — the setting against the
  tree, not the tree against the setting
  ([168](168-one-aggregating-required-check.md)).

## Where it applies

**Works** for composition checks the change itself is entitled to alter: job
names and sets, required file lists, schema keys.

**Does not work** where the reference is genuinely external and does not belong
to the change: "the dependency version is not below the published one", "the
answer matches the publisher's contract". The past is the subject there. Nor does
it work for state checks — "is the main branch green": state is taken from
outside, or it stops being state.

**Sign of violation:** for the check to go green, the change must be merged
first.

## Trace

ArtVsMark/Claude-Code_Usage-Token#46 — scripts/pr_check.py

Related: [168](168-one-aggregating-required-check.md) — one required check with a
constant name; 171 is the same drift one floor down, inside the check itself.
[049](049-derive-state-from-live-artifacts.md) — state is derived from live
artifacts.
[010](010-empty-checklist-is-not-green.md) — an empty checklist is not green.
