# An irreversible step is guarded by invariants checked in advance

**Area.** release, CI

**The rule.** What fires once and cannot be undone cannot be verified by running
it. Guard it with a separate invariant check — before the occasion arrives.

## The incident

An error in a pipeline definition is invisible to linters and to tests. It
manifests **once** — at release — and it is expensive: a published version cannot
be overwritten, and the release page is seen before anyone notices that no files
are attached to it.

That is exactly what happened: in the publishing job, the source checkout step
stood **after** downloading the built artefacts and wiped the working directory
along with them. No ordinary check would have caught it: the job runs only at
release, and before a release nobody executes it.

Hence a separate check of facts that break silently: the order of steps; the
presence of a step that rejects an empty build result; validation of the built
artefacts before publication; declared permissions — without a declaration the
token gets defaults; and a subscription to draft-ready events — without it a
change created as a draft receives no checks either on creation or on becoming
ready.

## Why

Ordinary testing relies on **repeatability**: it broke, we saw it, we fixed it,
we ran it again. An irreversible one-shot step has no such loop. The first error
is also the last, and its consequences are already public.

So what must be checked is not behaviour but **form**: the invariants that must
hold in the description of the process. That is weaker than a test, but it
applies where a test is impossible.

Second: the list of invariants is written not from general considerations but
**from what actually happened**. Every item is the trace of a specific breakage,
and that is its strength: general recommendations do not stick to such
definitions, while "step A must come before step B" is checked literally.

## In practice

- the check lives in a script with tests, not in a line inside the definition
  itself: the checker must not break together with the checked;
- **facts are checked, not style**: order, presence, non-emptiness, permissions;
- the irreversible step has a safety catch on empty input: nothing to publish
  means fail, not publish emptiness;
- permissions are declared explicitly everywhere: a default is also a decision,
  just not one you made.

## Where it applies

**Works** for releases, migrations, mailings, data deletion — anything that
happens once and does not roll back.

**Does not work** where the step is easy to repeat: running it is cheaper than
describing invariants.

**Sign that it is needed:** "we will only find that out at release".

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_workflow_guardrails.py`, #988.
