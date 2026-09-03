# A default taken from the environment is a hidden platform dependency

**Area.** code, CI

**The rule.** A default computed from the **environment** is a hidden platform
dependency, and a job matrix does not prove it correct. The locale's encoding
behind `text=True` in `subprocess`, the timezone behind naive datetimes, the
case sensitivity of a filesystem: such code is green on some matrix cells and red
on others — and it goes red **only on the right data**. Two conditions must
coincide for the defect to appear, so a green matrix says "the coincidence did
not happen on this data", not "the default is set correctly". This is caught by
reading the source, not by running it; the requirement is one: a default that
depends on the environment is set explicitly.

**Portable beyond Claude Code.** yes — the subject belongs to any language and
any platform: locale, timezone, path separator, filesystem case.

## The incident

The cells `windows-latest · python 3.11` and `3.13` went red on change #62:
`UnicodeDecodeError: 'charmap' codec can't decode byte 0x81`. The cause was
`subprocess.run(..., text=True)` without `encoding=`: the locale's encoding is
used, which is UTF-8 on ubuntu and macos and cp1252 on the windows runner, where
byte 0x81 is not defined at all. The project is written in Russian, git returns
Russian commit subjects, and 0x81 is the second half of the letter "с" in UTF-8.

**The numbers:** the defect shows on **3 cells out of 9**, and only if the output
happened to contain the right letter — it survives the word "замер" and fails on
"список". The message misleads on top of that: decoding fails on its own thread,
`stdout` stays `None`, and what you see first is an `AttributeError` in the
caller.

**There was precedent:** two other calls in the same tree set the encoding
explicitly, and two new ones were still written without it, in separate passes. A
source review found exactly those two calls across 35 files, in a run with no
network.

**A second measurement, same class and same direction:** once the reader was
given an encoding, the three windows cells went red **again** — now the writer was
failing. Before the fix both sides erred identically and agreed; one fix pulled
them apart. So such a default has two halves, and setting one is not enough.

The quietest of all was `stderr`: its default is `backslashreplace`, so it never
fails and prints `\uXXXX` instead of the failure message. The gate keeps working
formally and stops naming what failed.

## Why

The defect requires **two conditions to coincide**: a platform with an
inconvenient default and data that triggers it. The chance of meeting both at
once is low, so the matrix is green more often than the subject is sound — and
green is read as proof.

Worse, the error is **symmetric and therefore self-compensating**: while both
sides take the same wrong locale, they agree. Fixing one side pulls them apart,
and the repair looks like a breakage — which is what the second measurement
showed.

And third, which explains why precedent does not help: an explicit encoding in a
neighbouring call is knowledge in **people's heads**, not in a mechanism. Two new
calls were written without it, in separate passes, looking at the same file
([002](002-rule-without-mechanism.md)).

Hence the method: not a run but a **source review**. A run answers "no
coincidence today"; a review answers "the default is not set", and that answer
depends on neither platform nor data.

## In practice

- **both** halves are set: reading and writing — one does not save you;
- `stderr` is checked separately: it does not fail, so it stays quiet loudest;
- text mode is switched on by **any** of `text`, `universal_newlines`, `errors` —
  `errors="replace"` without `encoding=` takes the same locale while looking like
  foresight;
- the check runs over the tree, not through a job: a run only has a subject when
  the conditions coincide;
- the same requirement applies to timezones, path case and line endings: one
  subject, several surfaces.

## Where it applies

**Works** for any default taken from the environment: locale, timezone,
filesystem case, line endings.

**Does not work** where the default is part of the language's own contract and
does not depend on the machine: dictionary order, integer width. Demanding
explicitness there only clutters the code with no subject. Nor does it work for a
single-platform delivery with a fixed, known environment — but then that must be
written down rather than assumed.

**Sign of violation:** a call reading someone else's output in text mode does not
name an encoding.

## Trace

ArtVsMark/Claude-Code_Usage-Token#63 — scripts/subprocess_encoding.py, the
incident on change ArtVsMark/Claude-Code_Usage-Token#62; measured 3 September: 2 findings across 35 sources

Related: [037](037-finding-status-depends-on-window.md) — green on a forgery is a
hypothesis; here the hypothesis is green on **part of the matrix**, and for a
different reason: a forgery checks the wrong subject, while a matrix checks the
right one under the wrong conditions.
[170](170-green-on-a-forgery-is-a-hypothesis-too.md) — the other side of the same
question about trusting green.
[002](002-rule-without-mechanism.md) — knowledge in people's heads is not a
mechanism: precedent in a neighbouring call did not stop two new ones being
written without an encoding.
