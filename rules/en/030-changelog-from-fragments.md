# The changelog is assembled from fragments, not written afterwards

**Area.** release

**The rule.** The entry arrives with the change, as a separate file. Assembly
happens at release.

## The incident

A single changelog file was edited by every branch. The result: **a conflict on
every second change**, and in the most pointless place possible — two entries,
both needed, simply added on the same line.

When the conflicts became too frequent, some authors stopped adding entries at
all — and the changelog began to be written just before release, from the commit
history.

Entries written that way retold **what was done in the code**, not what changed
for the user. Some changes were lost outright: a commit subject does not always
say whether anything was visible from outside.

## The fix

Every change drops a **separate file** into a fragments directory. At release
they are collected into the changelog.

There are no conflicts by construction: different files. The entry is written by
the author at the moment they best remember what they changed and why.

## Why

Two reasons, and the second matters more.

**Mechanical:** parallel edits to one file guarantee conflicts.

**Substantive:** an entry written afterwards is written from memory and from the
diff, so it describes **code** rather than **the change for the user**. At the
moment of the edit the author knows what the user will notice; two weeks later
they only know which lines they touched.

A side benefit: the presence of a fragment becomes checkable. A gate saying
"behaviour change without an entry does not pass" is only possible with this
scheme — in a shared file you cannot tell a new entry from somebody else's.

## What fragments do not fix

Resolving text conflicts through repository settings (`merge=union` and the
like) looks like an alternative to fragments and is not one: such a setting acts
**locally only**. A merge on your own machine goes through without intervention
exactly when the server already considers the change conflicted.

The consequence is worse than the conflict itself: a conflicting change is left
**with no checks at all** — the build runs against a merge result that does not
exist while there is a conflict. And an empty list of checks reads as "the build
broke", sending the investigation the wrong way.

## Where it applies

**Works** for any project with a changelog and parallel branches.

**Does not work** with a single author and a single branch — no conflicts there,
and a shared file is cheaper.

**Requires** an assembly step at release: one more stage in the process.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § updating the changelog