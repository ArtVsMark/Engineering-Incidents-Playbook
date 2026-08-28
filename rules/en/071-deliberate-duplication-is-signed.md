# Deliberate duplication is signed

**Area.** code, architecture

**The rule.** A repetition left on purpose is marked right there in the code:
what it duplicates and **what merging would cost**. An unsigned duplicate will be
"fixed" by the very next tidy-up.

## The incident

Two constants in the web layer repeat identical ones in the downloader module.
They match literally. Any sweep for duplication will flag this as debt.

Beside them stands a signature: duplicated deliberately — the web layer must not
drag in a whole application module for the sake of two constants; the value is
the same.

Without that line the course of events is predictable: somebody moves the
constants to a shared place, an import appears, and with it an edge in the
dependency graph — the very edge the duplicate existed to avoid. And the person
moving them is right in their own way: they see the duplicate and not the reason.

The same technique applies to loading a table of captions: it is read **as a
file, not as an import** of a neighbouring module — otherwise the same edge would
appear.

## Why

Duplication is not a vice in itself but a **price**. A constant written twice
costs the risk of divergence; an import for its sake costs coupling. Which is
dearer depends on the boundary being defended, and that knowledge lives in the
head of whoever decided.

The signature moves the knowledge from the head into the code. It answers the one
question the next reader has: "was this forgotten or intended?" — and without an
answer they will pick the first, because the first is more common.

Second: the signature is **the place for revision**. The condition is named ("for
the sake of two constants"), and when there are twenty, the decision can be
overturned deliberately rather than discovered as a duplicate that quietly grew.

## In practice

- the signature answers three questions: what it duplicates · why it is not
  merged · under what condition the decision changes;
- a duplicate whose values must match is backed by **a test for that match**: the
  signature protects against refactoring, the test against divergence;
- the same applies to any deliberate departure from a general rule: a workaround,
  a hand-rolled implementation instead of a library one, a disabled check;
- the signature sits **next to the code**, not only in a decision document:
  people edit code, not documents.

## Where it applies

**Works** for duplicates that defend a layer boundary or the direction of
dependencies.

**Does not work** for duplicates born of laziness: there a signature becomes an
indulgence where refactoring is needed.

**Sign that it is needed:** the duplicate has already been "fixed" once and had
to be restored.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/auth_adapter.py`
(ArtVsMark/Stepik-Python-Grader#433), `src/stepik_grader/launcher.py`. Related:
[042](042-decision-records-its-alternatives.md).