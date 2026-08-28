# Do not push into somebody else's branch

**Area.** collaboration

**The rule.** A change to a branch driven by another person or another session
is made by its owner. You report what needs resolving and how.

## The incident

A locale conflict looked trivial — "keep both lines". The fix was pushed
straight into the neighbouring session's branch.

The mechanical check let it through: a gate sees a **matching branch name**, not
an intention. Formally everything lined up: the branch exists, access is
granted, the change is correct.

## Why

The branch owner holds context the newcomer does not have: why this approach was
chosen, what has already been tried, what the "obvious" fix will break.

The triviality of a conflict is an outsider's illusion. Whoever sees two lines
is not seeing everything.

The second layer: someone else's commit in the branch breaks the owner's mental
model of its state. They come back and find a tree that is not the one they
left — with no notification.

## Where it applies

**Works** for any shared branch work, with people and with agents alike.

**Does not work** when the owner has explicitly handed the branch over — that is
a different situation: it now has a new owner.

**Generalisation:** this rule belongs to the class of requirements that **cannot
be checked by machine**. A gate distinguishes names, not intentions. Such rules
deserve to be named separately and honestly — otherwise they look "obvious" and
are the first to be broken.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § what the gates miss