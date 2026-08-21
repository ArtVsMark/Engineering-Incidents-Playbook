# A rule without a mechanism is a promise, not a guarantee

**Area.** process, CI

**The rule.** A requirement that cannot be checked by machine will not be
followed. Either build a gate, or do not write it down.

## The incident

A review of one working session: **nine incidents out of eleven were not
ignorance of a rule but skipping it**.

The telling case: the requirement to run the full test suite had been written
into the project's rules long before a filtered selection silently broke
somebody else's test. The rule was known. The rule was written down. It was
skipped.

## Why

People and agents skip a step you have to remember in exactly the same way. Not
out of malice — under the pressure of the task, attention goes to the work
itself, not to the procedure around it.

The gap between "you must" and "you cannot do otherwise" is the gap between a
hope and a property of the system.

The conclusion drawn then: a checklist gets **rewritten into a command**, not
extended with one more item. A pre-commit runner before committing, a
readiness check before merging — things you cannot forget, because they execute.

## Second-order effect

The same holds for publicly claimed properties. The project's front page stated
that the list of branch-protection bypasses was empty — and nothing verified it.
Such a list grows by one click for an urgent fix and never shrinks back; the
build stays green while the guarantee quietly stops existing.

**A public claim about quality that nothing verifies is a promise.**

## Where it applies

**Works** anywhere with continuous integration.

**Does not work** for requirements that cannot be expressed mechanically: "code
should be readable", "the architecture should be simple". Those belong in
review, and should not pretend to be rules.

**Careful:** a gate with an unclear rejection message is worse than no gate —
people start routing around it.

## Trace

ArtVsMark/Stepik-Python-Grader#1296, #1329
