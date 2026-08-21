# An empty state must be declared explicitly

**Area.** documentation, interface

**The rule.** "Nothing here right now, as of this date" is information. A merely
empty file is an ambiguity.

## The incident

The work queue after a large audit was kept in a file. When it had been worked
through, the entries were deleted — and the file was left empty.

Whoever opened it next could not tell: is the queue empty because everything is
done, or because nobody has filled it yet? Or did the file break during a merge?

The same question arose with the reviews directory: empty — does that mean
nothing is outstanding, or that nobody checked?

## The fix

The empty state is declared in words:

```
Nothing here right now — 2026-08-21. All waves completed, none newly raised.
```

Three things in one line: the **fact** of emptiness, the **date**, the
**reason**. The date answers "for how long", the reason answers "why".

The same in interfaces: "nothing found" beats a blank screen, and "the search
was never run" beats "nothing found".

## Why

Absence of data and absence of a check look identical — the same class as "an
empty list of checks means all clear".

A reader meeting emptiness is forced to **supply the explanation themselves**.
Usually they supply an optimistic one: it is empty, so everything must be fine.
An explicit note takes that option away.

## Where it applies

**Works** for documents, queues, reports, dashboards, search results.

**Does not work** for structures where emptiness is normal and means nothing:
temporary directories, caches.

**Cheap:** one line. It pays back the first time somebody asks "is there really
nothing here?"

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/claude-handoff.md`
