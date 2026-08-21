# A tool's own artefacts stay outside its input mask

**The rule.** Files the tool creates are named so that they **do not fall under
its own input selection rule**. Otherwise it starts processing its own output.

## The incident

The tool selects solution files by a name pattern. Separately it saves a history
of submissions: the code of each attempt alongside a description of the outcome.

The history file names are **deliberately outside** the selection pattern. Not for
style but for consequence: had they fallen under the pattern, old attempts would
have entered the comparison modes as full-fledged competitors. Comparing solutions
would have turned into the user competing with their own past — with the
difference that they would not know it.

The same technique next door: the side-effect guard excludes from its check the
files written by the run's own tooling — otherwise it blames the tests for what
the measurement rig did.

## Why

A tool whose output falls into its own input closes a loop on itself. The result
does not look like an error: it looks **plausible**, it simply describes something
other than what the user thinks. It is discovered through oddities in the numbers,
not through a failure.

The selection rule, meanwhile, was usually written before the output existed — and
there was no conflict until the tool started saving something. So the defect
appears **when a feature is added**, while what breaks is something else entirely,
long since working.

Hence a check for every new artefact: **will it fall under any existing selection
rules** — ours and other people's: build, search, indexing, backup.

## In practice

- service files differ from user files **at the level of name or directory**, not
  only by extension;
- the separation is documented with its reason: without it the next person brings
  the names "into line";
- if names cannot separate them, selection runs from an explicit list rather than
  a pattern;
- when adding an artefact, check other people's selection rules too: ignore lists,
  build patterns, backup masks.

## Where it applies

**Works** for tools that both read and write in one directory: builders,
checkers, converters, indexers.

**Does not work** if the output becomes the next run's input by design — there you
need an explicit generation marker rather than name separation.

**Sign of trouble:** the number of processed units grows from run to run with no
external changes.

## Trace

ArtVsMark/Stepik-Python-Grader — `core/submission_archive.py` (names outside
`_SOLUTION_FILE_RE`), `tests/conftest.py` (excluding run artefacts). Related:
[103](103-a-side-effect-guard-blames-the-wrong-suspect.md).
