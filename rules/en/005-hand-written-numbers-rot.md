# A number typed by hand goes stale in silence

**Area.** documentation

**The rule.** A figure in documentation is either recomputed automatically, or
it does not belong there.

## The incident

Two cases in a single day.

**The first.** The project's front page read "11 releases shipped". Release
`v1.11.0` went out at 13:46 — the figure became wrong four hours after it was
typed. Noticing that could only happen by chance.

**The second, more expensive.** The same page claimed "32 checks per PR". The
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

## The tail that follows

After the fix, one more "32" survived on the page — inside an image's `alt`
text. Invisible to the eye, but `alt` is exactly what screen readers and text
dumps consume: an external review reporting "32 in the header against 16 below"
had read it from there.

**When it drifts from the picture, alt text lies more quietly than anything
else.** The fix was not an edit but the same mechanism: the alt text is now
written by the same script that draws the image.

## Why

A number in prose is a snapshot of a moment, and the world keeps moving. The
author remembers it exactly until the edit is finished.

Worse, a hand-written figure **propagates**: the same quantity ends up in three
places — image, text and alt text — and gets fixed in two of the three.

## Where it applies

**Works** for any metric on front pages, dashboards and reports: number of
tests, coverage, release count, size.

**Does not work** for numbers that are fixed by meaning: founding year,
protocol version, domain constants.

**Careful:** automatic collection requires a single source of truth. If a script
writes the picture while the alt text is edited by hand, the same disease comes
back.

## Trace

ArtVsMark/ArtVsMark#7, ArtVsMark/ArtVsMark#8. The conditions under which a
number may sit in text after all —
[127](127-a-number-in-prose-needs-a-guarded-marker.md).