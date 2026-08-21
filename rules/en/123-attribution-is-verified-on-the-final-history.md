# Attribution is verified against the final history, not against the branch commit

**The rule.** The commit message that lands on the shared branch is
**recomposed** at merge time. Whatever the author wrote in the branch is only
input to that recomposition, and the platform may substitute its own authorship
fields.

## The incident

Co-authorship in the project is set explicitly: the commit trailer carries an
agreed name. The branch looked right — the trailer was there, with the right
name.

What landed on the shared branch carried a **different** trailer: on squash the
platform substituted its own, taking the identity of the **environment the merge
ran from** rather than the line in the branch commits. The author stayed a
human, as intended — only the co-authorship broke.

The result: the same co-author appears in history under **two different names**.
Precisely the case already documented as having happened once — the one the
rules warned against repeating.

There is nothing to fix retroactively: the shared branch is protected and
rewriting history is forbidden. An attribution error is irreversible from the
moment of the merge.

## Why

A squash merge **does not transfer a commit; it composes a new one**. The
subject comes from one place, the body from another, and the platform fills in
service fields itself from what it knows about the merger. Checking the message
in the branch means checking a draft, not the result.

The second half of the trouble is **irreversibility**. A branch can be
rewritten; the history of the shared branch cannot. So the check must sit
**before** the merge — after it, all that remains is a follow-up commit
apologising.

Third, and less obvious: wrong attribution breaks nothing and wakes nobody. The
build is green, the code is correct, the change works. It is noticed by eye, by
chance, and usually after several such commits have accumulated.

## In practice

- verify **the final message**: what is visible on the shared branch after the
  merge, not what the author typed in the branch;
- authorship trailers are checked against the list of agreed names — a mismatch
  is a rejection, not a detail;
- the merging party carries their own responsibility: they write the subject and
  body of the final commit, and the attribution rule is part of their checklist;
- **the irreversible is checked in advance**: since history cannot be rewritten,
  the gate stands before the merge, not after;
- if the platform substitutes its own field and that cannot be disabled, the
  limitation is stated out loud as a known gap rather than treated as an
  oversight.

## Where it applies

**Works** anywhere the final commit is assembled by someone other than the
author: squash merges, merge bots, pipelines with automatic signing.

**Does not work** when commits are transferred as they are — there the author's
message is the final one.

**Sign of a breach:** one participant appears in the history under several
names.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § commit format (authorship under
squash merge). Related:
[074](074-one-shot-irreversible-steps-get-their-own-guard.md),
[002](002-rule-without-mechanism.md).
