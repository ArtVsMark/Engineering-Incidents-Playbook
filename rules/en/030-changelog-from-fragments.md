# The changelog is assembled from fragments, not written afterwards

**Area.** release

**Tier.** 2 — the pipeline and CI

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

## Second incident: assembly at release was a manual step

The boundary "Requires an assembly step at release" below was there from the
start — and never became a step of the release itself. Fragments were collected
by a preparation change; the release run only closed the section. Changes kept
merging between the preparation and the button press.

- **v1.9.0, 8 October** — caught by hand: a separate change #736 "collected
  fragment #734 into [Unreleased]" before the press.
- **v1.10.0, 9 October** — not caught. Preparation #759 merged at 21:59 UTC on
  8 October, the release (run 37899491212) was pressed at 07:31 UTC on
  9 October; 21 changes reached the shared branch in between, and 10 of them
  brought fragments. Section [1.10.0] closed without them: **the code is in the
  tag, the entries are not** — neither in the release changelog nor on its page,
  and the platform marked the page immutable.

The window accompanying the release told the owner the release would collect the
fragments itself, without opening `release.yml`: there was neither a collect
step nor a refusal on leftovers.

The fix is a mechanism, not a reminder: the release collects fragments itself
before building the page body, and closing the section refuses while anything
remains in `changelog.d/`.

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

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § Обновление CHANGELOG

ArtVsMark/Engineering-Incidents-Playbook#736 — second incident: the v1.9.0 miss caught by hand; v1.10.0 shipped without 10 entries (release run 37899491212); the mechanism is the collect step in `.github/workflows/release.yml` and the `scripts/collect_changelog.py --close` refusal on leftovers
