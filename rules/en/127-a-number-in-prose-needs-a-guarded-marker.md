# A number in prose lives only with a marker, a build and a guard on that marker

**Area.** documentation, gates

**The rule.** A number may sit in prose under three conditions at once: it is
inside a **named marker**, a **build rewrites it from the source that produces
it**, and **a missing marker fails the build**. Without the third condition there
is no mechanism — only a hand-written number with an extra step.

## The incident

A profile storefront was rebuilt. Nine numbers sit **in prose**: test modules,
required checks, matrix size, releases, glossary cards, the newcomer task pool,
records in the catalogue. Each one lives inside an `m:key` marker comment, and
once a day a build rewrites them from the repositories that produce those
numbers.

The test came sooner than expected. About an hour passed between the local
measurement and the first run in CI — and **two numbers moved on their own**: the
catalogue went from 124 rules to 125, the grader from 209 test modules to 210.
The build caught both and rewrote the page in commit `a572a04`, touching nothing
beyond the three marker lines.

The second observation, the one the whole exercise was for: **moving those
numbers into badges is not free**. A badge is an image, and its `alt` carries a
caption rather than a value: with shields it reads "PyPI", "CI", "coverage". The
reader [008](008-details-is-a-stub-in-text.md) was written for — a parser, a
screen reader, a language model — never receives the number at all.

## Why

The reason for banning numbers in prose is made of two words, not one: text goes
stale **silently**. A marker plus a build removes "stale". "Silently" remains —
and it is the sharper half.

A failure of such a build **looks exactly like its success**. A pattern
substitution that matches nothing returns the same text; the script exits zero;
the pipeline honestly reports "numbers unchanged". A lost marker and an unchanged
number are indistinguishable from outside — the very indistinguishability
[075](075-a-guard-that-finds-nothing-must-fail.md) was written about. Hence the
third condition: if the marker is not found, fail, rather than report an absence
of changes.

Second, and less obvious: **badges and text pull in opposite directions**. "All
numbers in badges" optimises for the eye; "the page is read as text" optimises
for the parser. While a badge was the only mechanism that recomputed anything,
there was no choice to make. Once text acquired a mechanism of its own, the
choice appeared — and it should be made deliberately rather than by habit.

Hence the boundary between the two. A **badge** when the number is for the eye
and a live source already exists: the version in a package registry, the state of
the pipeline. **Text** when the number has to reach a reader that parses the page
rather than looks at it.

## In practice

- the marker is **named and machine-findable**: `m:key`, not "the number after
  the word 'tests'" — otherwise a rewritten sentence breaks the build;
- the source is the one that **produces** the number, not a copy of it:
  recomputing from another storefront reproduces
  [125](125-a-generated-file-is-not-a-store.md);
- the build fails in three cases: the marker is not found, the source returned
  nothing, an image has no `alt`. All three are failed checks, not "no changes";
- the failure scenarios are exercised **on a copy of the page** before the first
  live run: testing the guard on the live storefront means being the last to know
  it does not work;
- a number for which you cannot name the command that rewrites it does not go
  into text: [005](005-hand-written-numbers-rot.md) applies with no concessions.

## Where it applies

**Works** for pages somebody rebuilds: profile and project storefronts, summary
reports, status pages.

**Does not work** where there is no build and none is coming: a one-off page,
somebody else's repository, a document in an email. There the ban in 005 stands
as written — the number is either absent or rotting.

**Does not work** either where nothing produces the number: an estimate, a plan,
a promise. Such a number has nowhere to be recomputed from, and a marker around
it is decoration.

**Sign of a violation:** answering "what rewrites this number" requires saying
"by hand, when we notice".

## Trace

ArtVsMark/ArtVsMark#12; the storefront rebuild — commit `a572a04`. See also:
[005](005-hand-written-numbers-rot.md) — the ban whose boundary this record
refines; [075](075-a-guard-that-finds-nothing-must-fail.md) — why the third
condition is mandatory; [008](008-details-is-a-stub-in-text.md) — the reader that
sees text but not the picture; [002](002-rule-without-mechanism.md) — without a
gate this is a promise; [023](023-readme-is-a-storefront.md) — the storefront
where it is applied.
