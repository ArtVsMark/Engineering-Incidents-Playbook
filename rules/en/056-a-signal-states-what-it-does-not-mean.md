# A signal also states what it does not mean

**Area.** contracts, documentation

**Tier.** 1 — rules and roles

**The rule.** The description of a status, code or label has two halves: what it
means and **what it does not mean**. The second half matters more.

## The incident

A dedicated status marks that the isolation mechanism **proactively detected and
terminated** a quota breach: memory, output volume, processor time.

It reads as "any isolation violation". In fact it is not. Attempts to reach the
network, to write a file outside the permitted area, to spawn extra processes do
**not** land here: the kernel rejects them **inside** the sandbox, the solution
fails with an ordinary error, and that is honestly classified as an ordinary
runtime error.

And this is **a deliberate decision, not an oversight**: distinguishing "ordinary
error" from "isolation violation" by exit code turned out to be unreliable — on
one platform memory exhaustion normally arrives as an ordinary exception with
code 1 rather than as a signal.

Without the second half of the description the status would read as a guarantee
of completeness: "there are no violations, because this status is absent".

## Why

A reader fills in the unsaid **in the direction of completeness**. A status
named "isolation violation" is understood by default as "all isolation
violations" — and conclusions, reports and decisions are built on that.

The second half costs three lines and removes a whole class of errors: not only
"what the signal misses" but **why it misses it**. The reason turns the gap from
suspicious into understood: it is visible that the alternative was considered
and rejected for a measured reason, not forgotten.

The same principle applies to labels, error codes, log levels and task statuses:
any name that looks exhaustive must say where its boundary lies.

## In practice

- the section says it plainly: "what X means — and what it does not";
- the boundary comes with a reason, not just a statement;
- if the signal does not provide completeness, say what provides it instead, or
  that nothing does;
- the signal's name is no broader than its meaning: renaming is cheaper than
  explaining it forever.

## Where it applies

**Works** for statuses, exit codes, labels, severity levels — anything read
without looking at the implementation.

**Does not work** for signals with obvious completeness (success or failure of a
single operation).

**Sign that it is needed:** the same clarification has to be repeated in
conversation a second time.

## Trace

ArtVsMark/Stepik-Python-Grader — `SECURITY.md` § what `SANDBOX_VIOLATION` means
(and what it does not).