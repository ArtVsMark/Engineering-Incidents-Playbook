# A compatibility shim makes the migration permanent

**The rule.** A migration is either clean or does not start. A compatibility
layer left in "for the time being" turns one canonical path into two and outlives
the migration itself.

## The incident

Moving to a new package layout was discussed in two variants. The second looked
considerate: the new layout **plus thin shims** in the old places, so that the old
way of launching kept working.

It was rejected explicitly, and the arguments were recorded: two import paths and
their inevitable drift, and above all the shims **would again disguise the
packaging** — the shadow of exactly the problem the migration existed to solve.

Clean migration was chosen: one canonical path, the old one does not work.

## Why

A shim removes the **pressure** that makes a migration finish. While the old path
works, nobody moves: moving has a cost now and a benefit later, and with a live
alternative the balance is always against moving.

Second: two paths **diverge**. Not because anybody is lazy but because fixes go
into whichever is being used, and both are used. A few months later the shim is
not a thin adapter but a second implementation with its own behaviour.

Third, and most unpleasant: a shim **reproduces the original defect**. It exists
precisely so that the old behaviour survives — so it preserves what was being
migrated away from.

Hence an honest fork: either break it now and concentrate the cost into one
painful moment, or do not migrate at all and admit the old path remains
canonical. A third option — "migrate gently" — does not exist in practice.

## In practice

- if you break it, break it **visibly**: a clear error pointing at the new path,
  not quiet operation the old way;
- the migration has a version in which it happened, and an entry in the
  changelog;
- temporary compatibility is acceptable only with **a removal date** and a
  recorded decision: without a date it is indefinite by construction;
- "two paths for a transitional period" is a reason to recount: a one-off
  breakage is usually cheaper than six months of maintaining both.

## Where it applies

**Works** for layout moves, renames, changes of data format and of interfaces
inside your own code.

**Does not work** for public interfaces with external consumers: there a
compatibility layer is mandatory, and the rule becomes "it has a deadline and the
deadline is declared".

**Sign of trouble:** the transitional layer has outlived the people who
introduced it.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0004 § alternatives (root shims explicitly
rejected). Related: [043](043-decisions-are-superseded-not-edited.md).
