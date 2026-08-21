# Leniency is enumerated in a table and switched off by a mode

**Area.** comparison, quality

**The rule.** Every allowance in a comparison is named explicitly, with its
reason, and a strict mode exists where nothing is forgiven. Unenumerated leniency
turns into a set of heuristics nobody trusts.

## The incident

Comparing output with an expectation cannot be literal: a different number of
decimal places, a different spelling of the same number, different line-ending
characters, a trailing space, an extra blank line at the end. All of those are
legitimate matches, and treating them as differences means rejecting correct
work.

The allowances are set out in a **table**: what exactly is forgiven, an example,
and why. On a separate line comes the boundary that is easily mistaken for part
of the allowance: only three conventional variants count as a line break, and all
other control characters remain **data inside the line**. It was exactly on that
boundary that things once broke: the standard parsing function counted eight more
characters as line breaks, and corrupted output was judged correct.

And beside it, a second mode — strict — where nothing is forgiven. The lenient
mode reproduces the behaviour of the external checking system; the strict one is
for those who care about the letter.

## Why

An allowance is an **extension** of the equality relation, that is, a weakening
of the check. Each one on its own is justified, but together they form a zone
whose boundaries nobody knows. It is in that zone that the checker's worst defect
lives: accepting the incorrect.

Enumeration restores visibility to the boundaries. A row in the table is a claim
that can be disputed, verified by a test and revoked. An unwritten allowance
cannot be disputed: you learn of it once it has already fired in the wrong place.

The strict mode is needed for another reason: **leniency must be switchable, or
it cannot be verified**. Comparing the results of the two modes shows exactly
what was forgiven — and that is the only way to be sure it is what was intended.

## In practice

- a three-column table: what · example · why; no row is added without a reason;
- every allowance has its own test, and it checks **both** sides: what should be
  forgiven is forgiven, what is adjacent is not;
- the boundary of an allowance is written beside it, especially where the standard
  library understands a term more broadly than the domain does;
- the strict mode is not a debug flag but a full mode with documentation;
- a new allowance is introduced by a decision, not by editing a regular
  expression.

## Where it applies

**Works** for comparing outputs, validating formats, matching records,
deduplication.

**Does not work** where exact equality is required by contract: signatures,
hashes, identifiers.

**Sign of trouble:** the answer to "would that count as a match?" is "we would
have to try".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/use/configuration.md` § what is forgiven /
§ what is not, comparison modes. Related:
[097](097-a-checker-has-two-error-types.md),
[068](068-allowlist-not-denylist.md).
