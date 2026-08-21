# Whatever the tool created, it must be able to delete

**Area.** privacy, product

**The rule.** Every accumulation the product created has a first-class delete
command. "Delete the file manually" is not a method: the user did not create that
file and is not obliged to know about it.

## The incident

The product kept a local learning journal. There was a switch for recording: it
stopped **writing**. But removing what had already accumulated required deleting
the database file by hand — along with two service files beside it whose
existence the user could not have known about.

So the data controls looked complete while in fact they covered only the future.
The past stayed on disk, and the only route to it required knowledge of the
internals.

The fix was a dedicated delete command, with two details. First: without further
qualification it clears the accompanying statistics **as well** — that is the same
personal data, and leaving it would be keeping the promise by halves. Second:
there is a preview — what exactly will be deleted, before it happens.

## Why

The right to delete is part of the right to own. A product creating an
accumulation on somebody else's machine takes on an obligation: whoever owns that
data must manage it with the product's own tools, not with a file manager.

Second: "delete it manually" requires **knowledge of the internals** — where it
lives, what it is called, which files sit beside it. The user cannot obtain that
knowledge legitimately and is not obliged to have it. An instruction requiring it
is equivalent to a refusal.

Third, frequently missed: switching off recording and deleting what was recorded
are **different operations**. The first is about the future, the second about the
past, and the presence of the first creates a false impression that the second
exists too.

## In practice

- the delete command enumerates **every** place the product accumulated data: the
  main store, service files beside it, caches, statistics;
- there is a preview and a confirmation — deletion is irreversible;
- deletion is available both selectively (per object) and wholesale;
- the documentation says **where** the data lives and what exactly is deleted:
  that is part of the promise, not a technical detail;
- the same rule applies to withdrawing consent: permission is revoked by the same
  means it was given.

## Where it applies

**Works** for journals, caches, histories, accumulated statistics, settings,
consent records.

**Does not work** for what must be retained under external obligations — there
the boundary is explained rather than left unsaid.

**Sign of a breach:** the answer to "how do I remove this" contains a file path.

## Trace

ArtVsMark/Stepik-Python-Grader — `cli/__init__.py` (`--purge-history`), #813.
Related: [095](095-the-default-is-chosen-for-the-user.md),
[096](096-storage-follows-lifecycle-not-convenience.md).
