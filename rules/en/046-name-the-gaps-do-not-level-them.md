# Name the gap in a guarantee; do not level it on paper

**Area.** documentation, security

**Tier.** 5 — everything else

**The rule.** If the guarantee differs across platforms, publish a **table of
asymmetry**, not a single word. Every gap says why it was left and what the
right solution would be.

## The incident

There are three isolation mechanisms, one per operating system, and they deliver
**different things**. The network is cut by the kernel on two platforms and not
cut on the third. Writing outside the temporary directory is blocked entirely on
two and only for relative paths on the third. Memory limiting works through the
kernel on two and by polling on the third.

The temptation was to describe this with the single word "supported" and not
spend a paragraph explaining. Instead a table appeared, row by row: the row is a
guarantee, the column is an operating system, the cell is ✅ by the kernel,
⚠️ partial, ❌ none.

Below the table are the **named gaps**: not "not done" but "the right primitive
is such-and-such, it requires this, which is disproportionately complex at this
stage; a separate task, not blocking this stage".

## Why

A user decides based on **their own** platform, not on the average. The word
"supported" covering ✅ and ❌ at once promises what does not exist on their
machine — and the promise is discovered exactly when somebody relied on it.

Second: a named gap **is not forgotten**. Written down with its reason and the
right solution, it remains a task. Unwritten, it becomes a property of the
product that everybody vaguely suspects.

Third: a table distinguishes the **level** of a guarantee, not merely its
presence. "By the kernel" and "by polling at an interval" both read as
"present", but one withstands hostile code and the other does not.

## In practice

- the section heading says it plainly: the asymmetry is a **documented
  trade-off**, not a defect and not an oversight;
- a gap is described in three parts: what is missing · which primitive would be
  correct · why it is not taken now;
- partial guarantees say exactly how they are partial;
- the front page never promises more than the table: a word in the README must
  not be broader than the worst row.

## Where it applies

**Works** for cross-platform guarantees, tiers of subscription, degradation when
an external service is unavailable.

**Does not work** if the difference is not yet known — then it is more honest to
say "we did not measure" than to draw a table from guesses.

**Sign of trouble:** the answer to "does this work the same on my system?" is
"broadly yes".

## Trace

ArtVsMark/Stepik-Python-Grader — `SECURITY.md` § per-OS guarantees (asymmetry is
not a bug but a documented trade-off).