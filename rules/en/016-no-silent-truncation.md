# Output is never truncated silently — only with a marker

**Area.** output, reports

**The rule.** A trimmed result must state that it was trimmed, and by how much.
Otherwise it looks complete.

## The incident

An agent produced a result that did not fit the size limit — and returned the
first part with no annotation at all.

The host took it for a complete answer. Findings that had not fitted vanished
without trace: no error, no warning, no sign that anything had been cut.

It was discovered by chance, while reconciling the number of findings against
the journal.

## Why

Silent truncation turns **incompleteness into an invisible error**. A complete
answer and a truncated one look identical, and telling them apart requires
knowing the expected size — that is, already having what is missing.

This is the same class as "an empty list of checks means all clear": the absence
of a signal is taken for a positive answer.

A truncation marker costs nothing and changes everything: "showing 40 of 137"
turns an invisible loss into an explicit state you can act on.

## Where it applies

**Works** for any bounded output: agent results, paginated API responses, logs,
reports, summaries in an interface.

The generalisation: **any limit on output must be visible in the output
itself.** If the machinery dropped something, it says so right there, not in the
documentation.

**Does not work** where incompleteness is the contract: streaming, previews, a
deliberately partial selection the user asked for. Even there, naming the
boundary helps.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § never truncate
silently