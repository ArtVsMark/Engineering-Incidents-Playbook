# Only the head of the queue updates from the shared branch

**Area.** pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** While changes land one at a time, the one to synchronise with the
shared branch is **whoever is next**. Updating everyone after every merge is a
quadratic amount of wasted work.

## The incident

The rule used to be: after each merge, update every ready change so that none
falls behind. It sounds caring and does exactly the opposite.

Every update restarts the checks. But the very next merge moves the shared
branch again — and everyone just updated is behind again. With N ready changes
that is N(N−1)/2 updates instead of N.

The measured case: **six changes — 21 pointless runs against 12 useful ones**.
And the pointless runs occupy the same executor queue as the useful ones, so
they slow down exactly the work they were meant to speed up.

## Why

An update is only meaningful right before the merge: it checks the change
**against the state that will actually land** on the shared branch. A check
against a state that will be stale in ten minutes gives nothing — neither review
value nor a guarantee.

Hence an order in which each change is updated exactly once, when its turn
comes: wait for the turn → update → enable auto-merge → wait for the shared
branch to go green → take the next one.

Two runs per change is a **lower bound, not extravagance**: one on the branch so
that review looks at working code, one after the update, on the state that will
land. Only the first can be removed — do not run checks until the turn comes —
but then defects surface when the change is already at the head, and the queue
stops for the whole debugging session.

## In practice

- anyone who is not the head **stands still**: no updates, no restarted checks;
- auto-merge is enabled only on the head as well: enabling it on everyone at
  once restores the race the queue was built to remove;
- the next one is taken after the shared branch is **green**, not after the merge
  happens;
- the head is advanced by machinery, not by a person: otherwise the queue stalls
  for exactly as long as nobody is watching it.

## Where it applies

**Works** when protection requires branch freshness and merges happen one at a
time.

**Does not work** if branches are independent and freshness is not required —
there updating is pointless anyway.

**Sign of trouble:** checks restart more often than merges happen.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § merge queue.