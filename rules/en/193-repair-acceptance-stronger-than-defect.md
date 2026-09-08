# The acceptance test for an automated repair must be stricter than the defect it repairs

**Area.** data, quality

**Tier.** 4 — code and tests

**The rule.** A bulk automated repair of data is accepted by a criterion
STRICTER than the defect it fixes. A defect of "does not compile" cannot be
accepted by a check of "compiles": that filters out the failures and lets the
forgeries through. If no stricter criterion exists, the work is manual — and that
is an answer, not a defeat.

**Portable beyond Claude Code.** yes — the subject exists for any bulk data edit:
migrations, reference-data normalisation, automatic markup correction.

## The incident

A glossary importer had spent years stripping indentation from each line of an
example separately, and 90 of 1349 learning cards stored code that does not
compile. The cause was removed, but stored data is not fixed that way, so a bulk
repair was written: after a line ending in a colon, indent by one; the result is
accepted only if `ast.parse` accepts it.

The acceptance looked strict — it is executable, not "by eye" — and 80 cards out
of 90 passed it. Reading the diff showed the repair was wrong for 79 of those 80:
the heuristic never leaves a block, so it folds the example into a ladder of
nesting — a class definition inside a method inside a loop. A 60-line example
drifted 14 levels deep.

The parser accepts that: syntactically it is impeccable. So does a run: nested
definitions are never executed, so there is no error. Of the 80 "repaired" cards,
48 ran without raising anything.

The outcome, measured: 1 card out of 90 is repairable automatically — the only
one where there is exactly one block opener followed by exactly one line, and the
only one of the eighty accepted where the acceptance was not wrong. The rest were
done by hand.

**The danger is not the lost time.** A broken example is visible to anyone: it
fails for the student. A "repaired" one looks like working code and silently
teaches the wrong thing — the repair would have been irreversible BY APPEARANCE.

## Why

An acceptance criterion equal to the negation of the defect checks exactly one
thing: that the defect is no longer observable in its former shape. Everything
between "broken" and "correct" it accepts — and an automated repair lands there
more often than a manual one, because it works from a pattern rather than from
meaning.

The asymmetry of cost here is unusual and therefore underrated: a failed repair is
BETTER than one that succeeds by appearance. The first fails and calls a human;
the second passes acceptance, enters the data and becomes the new truth. The
closer the criterion sits to the defect, the larger the share of the second
outcome.

Hence "stricter". The criterion must check a property the broken data did not
have AND that a forgery does not grant for free: not "parses" but "parses and the
structure matches the original"; not "runs" but "produces the same result".

**If no such criterion exists, that is an answer.** Working through ninety cards
by hand is cheaper than silently corrupting a thousand.

## In practice

- the acceptance criterion is named BEFORE the repair is written, and separately
  from it;
- it checks a property, not the absence of a symptom;
- the accepted share is part of the measurement: "80 of 90 passed" is not a
  result without reading the diff;
- no criterion stricter than the defect means the work is manual, and that is
  written down as a decision.

## Where it applies

**Works** for bulk automated edits of stored data whose result is later read as
truth.

**Does not work** where the edit is reversible and reviewable by eye in full: a
dozen lines are edited and looked at. Nor does it apply where the defect is stated
as an exact invariant — there its negation is the strict criterion, and there is
no difference.

**Sign of violation:** the acceptance of a repair is phrased as the negation of
the defect, and the accepted share is high while the diff is unread.

## Trace

ArtVsMark/Stepik-Python-Grader#1454 — the analysis and manual repair;
`scripts/check_glossary_examples.py`

Related: [146](146-a-green-gate-does-not-verify-its-premise.md) — a green check
confirms itself; here it confirmed syntax while the question was about meaning;
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — a gate is tested by what
it must reject, and accepting a repair is the same question;
[019](019-audit-from-surfaces-not-files.md) — walking the code misses what is not
in the code, and here acceptance by parser missed what is not in the syntax.
