# A collapsible block reads as a stub wherever the page is consumed as text

**Area.** showcases

**The rule.** On a page read automatically or at a glance, `<details>` yields a
heading with no content. Expand it or drop it.

## The incident

A section of the front page was hidden behind a disclosure: a summary line
reading "expand the full version", with forty-odd lines inside.

**Four reviews in a row** said the same thing: the section "looks like a promise
with no follow-through", "cuts off", "is unfinished". Three times I put that
down to the reviewing tool not expanding `<details>`, and only on the fourth
took it seriously.

The cause was exact: in a text extraction of the page the disclosure collapses
into a single summary line, and the next block starts immediately after —
producing a cut-off.

A second block of the same kind turned up elsewhere on the page: a heading and a
table inside it. Same diagnosis, same stub.

## Why

`<details>` is an interactive element: it works when there is somebody to click.
Everything that reads the page another way — a screen reader, a parser, a
language model, a diagonal glance — sees only the summary.

A side conclusion from the same incident: **when four readers in a row say the
same thing, the problem is not the readers.** Three times I explained their
observation away with tooling quirks instead of looking at the page through
their eyes.

## Where it applies

**Works** for front pages, READMEs, profile pages — anything skimmed and parsed
automatically.

**Does not work** as a blanket ban: in documentation where the reader is
deliberately clicking and hunting for something specific, a disclosure is
appropriate and saves space.

A practical test: **read the page the way a parser will see it** — summary lines
only, no contents. If it still reads as coherent text, keep it.

## Trace

ArtVsMark/ArtVsMark#9, #10
