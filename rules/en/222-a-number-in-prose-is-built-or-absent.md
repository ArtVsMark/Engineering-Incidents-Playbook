# A number in prose either sits in a marker a guarded build rewrites, or it is absent

**Area.** documentation, gates

**Tier.** 3 — gates and processes

**The rule.** A number sits in prose only inside a named marker that a build
rewrites from the source producing that number, and a missing marker fails the
build; otherwise there is no number in the text. A number typed by hand goes
stale in silence, and a marker without a gate on its loss is not a mechanism —
it is the same hand-written number with an extra step. There is one exception:
a number with nothing to be recomputed from — a constant fixed by meaning —
needs no marker.

**Portable beyond Claude Code.** yes — a number in text goes stale the same
way in any project, and a build with a gate on the marker asks nothing of an
agent window; the window only writes such numbers more often.

## The incident

**Two hand-written numbers on a front page in one day** (ArtVsMark/ArtVsMark,
#7 and #8; recorded in the catalogue on 21 August 2026 as rule 005).

*The first case.* The project's front page read "11 releases shipped". Release
`v1.11.0` went out at 13:46 — the figure became wrong four hours after it was
typed. Noticing that could only happen by chance.

*The second, more expensive.* The same page claimed "32 checks per PR". The
metrics collector, run for the first time, wrote **16**. The investigation
showed the machine was right:

```
PR #1294: 16 records, 16 unique names, no duplicates
PR #1293: 32 records, 16 unique names, duplicates: coverage-combine,
          test (windows-latest, 3.14, true), test (macos-latest, 3.12, false)…
```

After a branch update GitHub creates a second set of check runs while the first
stays on the old commit. `total_count` adds them together: sixteen becomes
thirty-two.

The wrong figure lived for a day, survived four revisions of the page and
**five external reviews** — none caught it, because reviews read the text
instead of checking it against the source.

*The tail that follows.* After the fix, one more "32" survived on the page —
inside an image's `alt` text. Invisible to the eye, but `alt` is exactly what
screen readers and text dumps consume: an external review reporting "32 in the
header against 16 below" had read it from there. **When it drifts from the
picture, alt text lies more quietly than anything else.** The fix was not an
edit but the same mechanism: the alt text is now written by the same script
that draws the image.

**Markers with a build caught two numbers within an hour**
(ArtVsMark/ArtVsMark, #12, commit `a572a04`; recorded in the catalogue on
21 August 2026 as rule 127). A profile storefront was rebuilt. Nine numbers sit
**in prose**: test modules, required checks, matrix size, releases, glossary
cards, the newcomer task pool, records in the catalogue. Each one lives inside
an `m:key` marker comment, and once a day a build rewrites them from the
repositories that produce those numbers.

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

**Where the merge came from.** Two projects proposed merging 005 and 127
independently:
ArtVsMark/Engineering-Pipeline-Mechanisms:merge/a-number-in-prose-is-built-or-absent
(a mutual 005↔127 reference; 127's boundary is a branch inside 005, and both
exceptions are one branch, "nothing to recompute from"; in that project one
pair holds both halves: `scripts/build_facts.py` builds the numbers,
`scripts/check_version.py` turns a marker with a foreign value red) and
ArtVsMark/ArtVsMark:merge/a-number-in-prose-is-a-guarded-marker-or-nothing
(apart, 005 reads as a ban and 127 as a technique, and the main point falls out:
a ban without a mechanism does not hold, and a mechanism without a gate on the
marker is the same hand-written number; on the storefront one place holds both —
`scripts/build_metrics.py::patch_readme`). The decision is
ArtVsMark/Engineering-Incidents-Playbook#645, the review of candidates is
ArtVsMark/Engineering-Incidents-Playbook#744: all six projects of the family
answered `active` to both numbers, with no divergence.

## Why

A number in prose is a snapshot of a moment, and the world keeps moving. The
author remembers it exactly until the edit is finished. Worse, a hand-written
figure **propagates**: the same quantity ends up in three places — image, text
and alt text — and gets fixed in two of the three.

The reason for the ban is made of two words, not one: text goes stale
**silently**. A marker plus a build removes "stale". "Silently" remains — and it
is the sharper half. A failure of such a build **looks exactly like its
success**. A pattern substitution that matches nothing returns the same text;
the script exits zero; the pipeline honestly reports "numbers unchanged". A
lost marker and an unchanged number are indistinguishable from outside — the
very indistinguishability [075](075-a-guard-that-finds-nothing-must-fail.md)
was written about. Hence the gate on the marker: if the marker is not found,
fail, rather than report an absence of changes.

That is why the ban and the technique are one rule, not two. Apart, the ban
reads as "write no numbers" and does not hold, because numbers in text are
needed; the technique reads as "put a marker" and without a gate fails as
quietly as a hand-written figure. Both have one cause — the number came loose
from the source that produced it — and one failure: the text holds a number
that is already wrong.

Badges and text, meanwhile, pull in opposite directions. "All numbers in
badges" optimises for the eye; "the page is read as text" optimises for the
parser. While a badge was the only mechanism that recomputed anything, there
was no choice to make. Once text acquired a mechanism of its own, the choice
appeared — and it should be made deliberately. A **badge** when the number is
for the eye and a live source already exists: the version in a package
registry, the state of the pipeline. **Text** when the number has to reach a
reader that parses the page rather than looks at it.

## Practical boundaries

- the marker is **named and machine-findable**: `m:key`, not "the number after
  the word 'tests'" — otherwise a rewritten sentence breaks the build;
- the source is the one that **produces** the number, not a copy of it:
  recomputing from another storefront reproduces
  [125](125-a-generated-file-is-not-a-store.md);
- a quantity has one source of truth: if a script writes the picture while the
  alt text is edited by hand, the same disease comes back — the alt text is
  written by the same script;
- the build fails in three cases: the marker is not found, the source returned
  nothing, an image has no `alt`. All three are failed checks, not "no changes";
- the failure scenarios are exercised **on a copy of the page** before the first
  live run: testing the guard on the live storefront means being the last to know
  it does not work;
- a number for which you cannot name the command that rewrites it does not go
  into text, with no concessions.

## Where it applies

**Works** for any metric on front pages, dashboards and reports — number of
tests, coverage, release count, size — and for pages somebody rebuilds: profile
and project storefronts, summary reports, status pages.

**Does not work** for numbers that nothing produces and that therefore have
nowhere to be recomputed from: those fixed by meaning — founding year, protocol
version, domain constants — stand in text as they are; an estimate, a plan, a
promise likewise, and a marker around them is only decoration.

**Branch:** where there is no build and none is coming — a one-off page,
somebody else's repository, a document in an email. Nobody is there to place
a marker, and the rule applies through its "otherwise there is no number" half:
the number is either absent or rotting.

**Sign of a violation:** answering "what rewrites this number" requires saying
"by hand, when we notice" — or the build with markers has never failed although
a marker has already disappeared from the page.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/ArtVsMark#7, ArtVsMark/ArtVsMark#8 (005).
ArtVsMark/ArtVsMark#12; the storefront rebuild — commit `a572a04` (127).

Replaces: [005](005-hand-written-numbers-rot.md),
[127](127-a-number-in-prose-needs-a-guarded-marker.md) — the ban and the
conditions under which a number may sit in text after all; apart, the ban does
not hold, and the technique without a gate on the marker fails silently.

Related: [075](075-a-guard-that-finds-nothing-must-fail.md) — why the gate on
the marker is mandatory; [008](008-details-is-a-stub-in-text.md) — the reader
that sees text but not the picture; [125](125-a-generated-file-is-not-a-store.md)
— the source, not a copy; [002](002-rule-without-mechanism.md) — without a gate
this is a promise; [023](023-readme-is-a-storefront.md) — the storefront where
it is applied.
