# Settings have one anchor and a bounded search area

**Area.** configuration

**The rule.** The upward search for a settings file stops at the project
boundary, not at the root of the file system. And all the product's surfaces share
**one** anchor — otherwise a single launch reads settings from two different
places.

## The incident

The settings search went up all the way to the file system root and took the
first matching file it found. The consequences came in two kinds, both
non-obvious.

**Somebody else's parameters.** A correct solution that produced the right result
in its own folder was rejected on time if somebody's file with different run
parameters sat one level above. The cause lay outside the working directory, and
nobody thought to look there.

**Somebody else's typo.** A syntax error in such an unrelated file brought down
**every** command of the product — including printing help. That is, a foreign
file the user has nothing to do with rendered the tool entirely inoperable.

The third defect was about the **anchor**: project settings resolved from the
working directory while the web shell's settings resolved from a supplied path.
One launch read two different places and behaved inconsistently.

The fix: the search area is bounded by the project root (the nearest directory
upwards with a marker), the anchor is shared across all surfaces, and a broken or
unreadable file produces **a warning with the path and the reason** without
interrupting the work.

## Why

An upward search is a heuristic, and a heuristic must have a boundary. Without
one the search area includes other people's projects, the home directory and
system paths; the probability of picking the wrong file grows with depth while
diagnosability falls: the cause lies where nobody looks.

Second: **somebody else's file must not break our launch**. Anything found by a
heuristic is by definition not guaranteed — so it is treated as unreliable input:
a warning and continuation, not an exception. Otherwise the product inherits the
quality of files that do not belong to it.

Third, on the anchor: settings form **one** state. Two surfaces with different
reference points give two states under one name, and the divergence shows up as
"one thing in the interface, another in the terminal" — the hardest class of
complaint to diagnose.

## In practice

- the search boundary is a project marker, not a number of levels up;
- the file found is named in the output: the user must see **what exactly** was
  read;
- a broken or unreadable file gives a warning with the path and the reason, and
  work continues on defaults;
- there is one anchor, set explicitly at launch; **everything** resolves from it,
  not part of it;
- a fallback path (relative to the package's own location, for instance) is
  applied last and only if the others produced nothing.

## Where it applies

**Works** for settings files, local overrides, caches and working directories
searched for up the tree.

**Does not work** for settings supplied only by an explicit path — there is no
search there.

**Sign of trouble:** behaviour changes depending on which folder you launched
from, and nobody can explain why.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/use/configuration.md` § why the search is
bounded, § the settings root; ArtVsMark/Stepik-Python-Grader#993,
ArtVsMark/Stepik-Python-Grader#984. Related:
[100](100-two-deadlines-start-and-work.md).