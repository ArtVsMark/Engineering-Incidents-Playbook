# One topic, one canonical document; everything else links to it

**Area.** documentation

**Tier.** 1 — rules and roles

**The rule.** Duplicated descriptions diverge. Always. The only question is how
many weeks pass before you notice.

**Portable beyond Claude Code.** yes — the claim about duplicated descriptions depends on neither the agent nor the platform: any two copies edited separately will drift.

## The incident

The same things were described in several places: working rules in the main file
and in the working documentation, the feature list in the README and in the
help, finding statuses in the audit document and in the tracker.

Within weeks the copies had diverged — and **there was no way to tell which was
right**. Each looked sensible, each had its own author and its own edit history.

A separate case: the register of findings was kept both in a document and in
issues. The conclusion is stated plainly in the project's rules: "two sources
mean one of them is stale".

## The fix

A table of "topic → canonical document", with exactly one row per topic. Every
other mention is a link.

The pattern that works for the main file: **a compact trigger plus the canon**.
In the rules file, a short block — what you need to know immediately — and an
explicit note: "do not duplicate the details here, they live in that file".

The trigger answers "do I need to go there"; the canon answers "how exactly".

## Why

A copy is under no obligation to update. Whoever makes a change sees one
document and edits it; the second one they do not know about, or forget.

Then it gets worse: the divergence surfaces not immediately, but when somebody
has made a decision from the stale copy.

A link does not have this problem: it either leads where it should or breaks
visibly.

## Where it applies

**Works** for any documentation of more than a few files.

**Does not work** literally for short statements: a one-line invariant is worth
repeating where it is critical. The boundary is volume and likelihood of change:
whatever will change must not be duplicated.

**Machine-checkable** in part: broken links yes, semantic divergence of copies
no.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § sources of truth