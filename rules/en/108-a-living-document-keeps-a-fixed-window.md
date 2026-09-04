# A living document keeps a fixed window; the rest moves out verbatim

**Area.** documentation

**Tier.** 1 — rules and roles

**The rule.** A growing document has a limit expressed as a number: this many
most recent sections. Everything beyond the window moves to the archive
**verbatim** — not shortened, not ticked off. A gate holds the limit.

## The incident

A changelog grows by definition — every change adds a line. After eleven releases
it became unreadable: the current sank into the history, and the history bothered
nobody precisely because nobody opened it.

The rule came out numeric: the live file holds **the release in preparation plus
the three most recent**. At release the oldest version moves to the archive file
**verbatim**, without retelling. A separate gate checks the number: it does not
let the count of version headings exceed three.

The same scheme applies to the working audit directory: a finished document moves
to the archive **whole**, rather than lying there marked "✅ closed". The directory
holds only what is live, and an empty directory is a normal state.

And to the work queue: when a wave finishes, its entry is **deleted**, not marked
done. If it is historically valuable it goes to the archive as its own file. Notes
about what was done are exactly what bloated the previous revision to 336 lines of
dead log.

## Why

A document without a limit grows until people stop opening it — and that happens
imperceptibly, because every individual entry is appropriate. A limit moves the
decision "what is redundant here" out of the future, where nobody will deal with
it, into the moment of release, where there is an occasion for it.

Why **verbatim**: moving is not editing. Shortening on the way out loses exactly
the detail somebody will go into the archive for — and they go there rarely and
with a specific question.

Why **moving rather than ticking**: a ticked entry still occupies space and
attention. A list of thirty lines where twenty-eight are ticked takes longer to
read than a list of two — and misleads about the size of the work.

Why **a number rather than "as it grows"**: without a number there is no limit. A
gate checks a number; "it is getting to be rather a lot" checks nothing.

## In practice

- the window is a number recorded **in one place**, and the gate reads it from
  there;
- the move is verbatim, preserving headings and links; the archive is indexed,
  otherwise it is a dump;
- the empty state of the live zone is declared explicitly, with a date —
  otherwise it reads as a breakage;
- the limit only moves down: a growing number means the cleanup was replaced by
  editing the limiter.

## Where it applies

**Works** for changelogs, directories of active documents, work queues, task
lists.

**Does not work** for documents whose value is completeness on one page:
specifications, references.

**Sign that it is needed:** the current part of the document has to be found by
scrolling.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § updating the changelog (the three
most recent minors, the `check_docs_guardrails.py` gate), § open work (the audit
lifecycle; the queue is cleaned by deletion). Related:
[024](024-no-worklog-in-active-docs.md), [050](050-limits-move-down-only.md),
[027](027-empty-state-is-a-state.md).