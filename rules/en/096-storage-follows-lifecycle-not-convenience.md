# Storage is chosen by the data's lifecycle, not by convenience

**Area.** architecture, data

**The rule.** Data with different lifetimes and different write patterns is not
merged into one store. A shared file glues together what does not belong
together and takes away the properties the formats were chosen for.

## The incident

Three kinds of persistence had accumulated: run history, a cache and a queue of
missing items. The tempting answer is a single database for everything.

Rejected, with the arguments recorded: it mixes **different lifecycles**,
complicates clearing and resetting, and increases contention on one file.
Clearing the cache without touching the history becomes its own task in a shared
store, instead of deleting a file.

The second rejected variant was the opposite: migrate **everything** into the
database. The specific downside: the statistics journal loses its append-only
property, and with it the cheap merging of concurrent writes from different
processes.

The middle path was chosen: shared **code** for database access — yes; a shared
**file** — no. Only the part that genuinely needs transactions was migrated; the
rest stayed in its own formats.

## Why

A storage format is a set of properties, not a matter of taste. Append-only
gives resistance to concurrent writing and simple merging. Transactions give
consistency. A separate file gives **deletion in one gesture**. The properties do
not add up: merge everything into one and you get their intersection, not their
union.

Second: lifecycles determine the **operations** that must be cheap. A cache is
cleared entirely and often. History is never cleared. A queue drains as it is
processed. A shared store makes expensive the very operation that should be the
cheapest.

Third: one file is one point of contention. Three independent write streams begin
waiting for each other for no reason at all.

## In practice

- shared **code** for access is normal and useful; a shared **file** is a
  decision requiring justification;
- each store records: lifetime, write pattern, who clears it and how;
- migration is selective: what is moved is what needs the new format's
  properties, not everything at once "for uniformity";
- if a format was chosen for a property (append-only, mergeability, atomicity),
  that property is named explicitly — otherwise the next refactor takes it away.

## Where it applies

**Works** where there is more than one kind of data and they live differently.

**Does not work** with a single kind of data: there the separation is a
needless entity.

**Sign of trouble:** "clear the cache" has become its own task instead of
deleting a file.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0011 § alternatives. Related:
[090](090-shared-helpers-move-up-not-sideways.md) — shared code without a shared
file.
