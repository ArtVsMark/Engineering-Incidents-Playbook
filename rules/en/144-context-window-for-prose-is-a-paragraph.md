# The context window for prose is a paragraph, not a sentence

**Area.** gates, tooling

**The rule.** Machine parsing of human-written text takes its context as a
**paragraph** — blank line to blank line — not as "the sentence up to the
nearest full stop". In technical prose the full stop lives inside names
(`SECURITY.md`, `v1.2.0`, `re.finditer`), so cutting on it lops off half the
meaning of arbitrarily chosen fragments. If the window genuinely has to be
narrower than a paragraph, the boundary is a unit of markup — a line, a list
item, a heading — never punctuation.

## The incident

Reconciling an audit's registry of closed findings: 384 merged pull requests,
887 finding identifiers. Around every mention the wording was classified —
"closes" versus "remains" — and that decided whether the finding entered the
closed registry.

The context window was taken as a sentence: previous full stop to next one. On
eight findings the parse returned the exact opposite answer. The paragraph read:

```
**Scope.** Verified on Linux/bwrap; the macOS branch changes symmetrically.
Of sub-epic #986 there remain: SBX-4-01 (a broken bwrap is not rejected),
SEC-2-02 (the whole venv is mounted, contrary to SECURITY.md) and SEC-2-03.
```

The full stop in `SECURITY.md` truncated the window, so "there remain" never
entered it — while `SEC-2-03` did. The parse filed as closed three findings the
pull request author had explicitly called open.

The first fix was wrong and instructive: the "remains" vocabulary got the
missing inflections added. The symptom went away on that paragraph — a different
marker happened to match — and the cause did not: the very next paragraph with
`README.md` in the middle broke the same way.

## Why

**Punctuation is not structure.** In prose for humans a full stop ends a
sentence; in technical prose it also separates parts of names, versions, paths
and calls. A parser that takes the second for the first fails not uniformly but
**selectively**: exactly those fragments break where a filename happened to sit
nearby. The failure looks random, and from a single example the cause is
invisible — so people fix the vocabulary instead of the window.

**Asymmetry of cost.** A paragraph is wider than a sentence, so its failure mode
is a false positive: an extra word enters the window and the parse says "unclear"
or "remains". That failure complains. The narrow window's failure mode is a false
"closed" — a live defect quietly buried
([097](097-a-checker-has-two-error-types.md)).

**Markup knows its boundaries; punctuation does not.** A blank line in Markdown
ends a thought by definition of the format, not by a guess about the language.
That is why the paragraph rule carries across languages unchanged, and a list of
inflections does not.

## In practice

- the window is `text.rfind("\n\n", 0, pos)` … `text.find("\n\n", pos)`; when the
  separator is absent, take the start and end of the text and **not an offset
  from −1** (that arithmetic silently eats the first character, and "Closes …"
  stops matching the marker);
- when you need narrower: a line, a list item, a table cell — units of markup;
- a section heading outranks the shape of a line: under "## What is left" sits
  the same "`ID` — what is wrong" list as under "## What was done", and only the
  heading tells them apart;
- revisit when the corpus stops being Markdown: plain text without blank lines
  has no paragraphs, and the boundary must be defined some other way.

## Where it applies

**Works** for parsing text written by people that contains filenames, versions
and calls: pull request bodies, issues, review comments, commit messages,
documentation.

**Does not work** for formats where punctuation *is* the structure: CSV,
delimiter-separated logs, single-line messages without markup. Nor where a
paragraph is knowingly longer than the unit of meaning — in screens of solid
prose the window should be narrowed to a sentence, but then segmentation belongs
to a library that knows about abbreviations, not to `rfind(".")`.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_audit_registry.py`, function
`mention_verdict()`: the window is a paragraph, the section heading outranks the
line shape, and a missing separator yields the start of the text rather than an
offset.

Related: [141](141-a-marker-is-matched-whole-not-by-prefix.md) — a marker is
matched whole, not by prefix; [097](097-a-checker-has-two-error-types.md) — a
checker has two error types, and they cost differently.