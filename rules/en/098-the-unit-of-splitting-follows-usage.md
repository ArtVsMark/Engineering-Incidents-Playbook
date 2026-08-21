# The unit of splitting follows usage, not a formal criterion

**The rule.** What counts as one entity is decided by **how it is used**, not by
a formal criterion such as "one call, one entry". A technical problem with
splitting is cured by metadata, not by splitting further.

## The incident

The reference partly consisted of bundles: one entry described several calls at
once. The formal rule "one concept, one card" demanded breaking up every bundle,
and most of them indeed were broken up.

But some **deliberately remained bundles** — those studied and used only
together: exception handling and its branch, entering and leaving a context,
starting and continuing an iteration, two spellings of one type, paired
operators. Splitting them would have produced two entries each meaningless
without the other, forcing the reader to reassemble the pair every time.

Meanwhile the technical reason the bundles were inconvenient — search could not
find an entry by the plain name of a call — was solved **not by splitting** but
by a separate keywords field. A search problem was solved by search means, and
the structure stayed as a human sees it.

## Why

Splitting always looks more "correct": smaller units are tidier, and a formal
criterion is machine-checkable. But a unit exists **for the user**, and users
operate not on formal atoms but on the bundles they are used to thinking in.

Hence the test: **does one occur without the other?** If not, this is one entity,
however many formal signals you count inside it. If yes, it is two, and they are
connected by a link.

Second: when splitting is proposed for a **technical** need (search, indexing, a
size limit), that is a sign of the wrong tool rather than the wrong structure.
Metadata, an index, aliases solve the same problem without breaking the meaning.

## In practice

- split entities are linked to each other explicitly — otherwise splitting loses
  the pair;
- the remaining bundles record **why** they are bundles: otherwise the next
  review breaks them up as unfinished work;
- search and housekeeping needs are met with fields, not with structure;
- a new entry obeys the same rule: first "does one occur without the other", then
  the form.

## Where it applies

**Works** for references, catalogues, rule sets, taxonomies, interface
components.

**Does not work** if the unit is fixed by an external contract — there the shape
is not ours.

**Sign of error:** users routinely open two entries in a row because one is not
enough to understand.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/glossary.md` § one concept, one card
(the list of deliberate bundles).
