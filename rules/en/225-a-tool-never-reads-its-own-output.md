# A tool never reads its own output — neither through its input mask nor as a store

**Area.** code, data

**Tier.** 1 — rules and roles

**The rule.** A tool's input is sources only: it does not read its own output,
neither through its input selection mask nor as a data store. Its own
artefacts differ from inputs by name or directory, with the reason written
down, and data lives in the source the derived file is built from; a missing
mandatory value fails the build instead of leaving an empty spot.

**Portable beyond Claude Code.** yes — the "a tool reads its own output" loop
works the same in a builder, a checker, a converter, an indexer and an index
generator; the agent window plays no part in any of the incidents.

## The incident

**Submission history outside the selection mask**
(ArtVsMark/Stepik-Python-Grader, `core/submission_archive.py`). The tool
selects solution files by a name pattern. Separately it saves a history of
submissions: the code of each attempt alongside a description of the outcome.

The history file names are **deliberately outside** the selection pattern.
Not for style but for consequence: had they fallen under the pattern, old
attempts would have entered the comparison modes as full-fledged competitors.
Comparing solutions would have turned into the user competing with their own
past — with the difference that they would not know it.

**The side-effect guard and the run's artefacts**
(ArtVsMark/Stepik-Python-Grader, `tests/conftest.py`). The same technique next
door: the side-effect guard excludes from its check the files written by the
run's own tooling — otherwise it blames the tests for what the measurement rig
did.

**The "Area" column wiped by a rebuild** (the catalogue,
ArtVsMark/Engineering-Incidents-Playbook#2). The catalogue index carried an
"Area" column — a subject classification: 124 rules, two languages, 51 areas.
The value came from an `old_areas()` function that parsed **the previous index
and the generator's own output** — derived files, both of them.

While the row format held still, this worked. Then the index was rewritten:
two single-language indexes were merged into one bilingual index, and the
table row went from `| [001](001-transport-rest-not-graphql.md) | … | quotas, API |`
to `| 001 | … |`. The regular expression expected the number in square
brackets and stopped matching.

The whole classification disappeared in a single rebuild. It was not spotted
quickly, and not from the inside: the owner reported the empty column after
seeing it in the finished index.

The gate stayed green throughout, and that is the heart of the incident. The
`build_rules_index.py --check` run compares the generated text against the one
in the repository — but the empty column was in both, and they matched. The
check truthfully reported "index up to date", 124 rules. It was comparing
output against output, and the data was in neither.

Recovery was possible only because the deleted file survived in history:
`git show 5f429e0^:rules/ru/README.md`. Without that commit, 51 areas would
have had to be assigned again by hand across 124 rules — that is, invented
again, because the original classification existed nowhere else.

**Where the merge came from.** This rule merges
[119](119-tool-artefacts-stay-outside-the-input-mask.md) and
[125](125-a-generated-file-is-not-a-store.md) on the proposal
ArtVsMark/ArtVsMark:merge/a-tool-never-reads-its-own-output
(ArtVsMark/Engineering-Incidents-Playbook#645, review #744). The signal: at
the storefront both rules are held by one function,
`scripts/check_mechanisms.py::own_output_readers`; the "one whole" card
answered yes to all four questions — one cause, the tool reads its own output;
one breakage, a plausible result found through oddities in the numbers rather
than through a failure; one claim; and the boundary of one is a branch of the
other.

## Why

**A tool whose output falls into its own input closes a loop on itself.** Two
doors lead into the loop. Through the selection mask: its own files match its
own input selection rule, and the tool processes its own past as fresh data
(119). Through the store: data lives only in the derived file, and the sole
source of a value is its own previous copy (125). Closing one door leaves the
other open — which is why the rule is one.

**The result does not look like an error.** It looks **plausible**, it simply
describes something other than what the user thinks: old attempts among the
competitors, an empty column among filled ones. The column is there, the rows
are there, the rule count is right — one field simply is not filled in. It is
discovered through oddities in the numbers, not through a failure, and no gate
comparing output against output catches it: there is nothing to diverge.

**The defect appears when a feature is added, and something else breaks.** The
selection rule was usually written before the output existed — and there was
no conflict until the tool started saving something. Data in a derived file
survives on inertia until the format changes: then it is not an error but a
silent reset. What breaks is something long since working, and it breaks away
from the moment of the edit.

**A derived file has no author.** The data in it exists exactly until the next
rebuild. The asymmetry of cost is what gives the rule its shape. Reading a
source and finding no data is a **loud** failure: the file is missing, the
field is missing, parsing fails. Reading your own output and finding no data is
a **quiet** result: an empty field, zero records, "just not filled in". The
first is fixed within the hour; the second lives until somebody happens to look
from outside.

Hence a fix in two parts, and one part is not enough. Move the data into the
source. And **make a missing mandatory value fail the build** rather than
render an empty cell ([075](075-a-guard-that-finds-nothing-must-fail.md)): as
long as an empty value is acceptable, it will return at the next change of
format.

## Practical boundaries

- service files differ from user files **at the level of name or directory**,
  not only by extension;
- the separation is documented with its reason: without it the next person
  brings the names "into line";
- if names cannot separate them, selection runs from an explicit list rather
  than a pattern;
- when adding an artefact, check whether it falls under existing selection
  rules — ours and other people's: build, search, indexing, ignore lists,
  backup masks;
- data is stored in the file it describes, not in a summary about it;
- the generator reads sources and takes **nothing** from its own output,
  including earlier versions of that output;
- a missing mandatory field fails the build and names the file, instead of
  rendering an empty cell;
- a field that genuinely is optional is declared optional explicitly —
  otherwise an empty value passes for data;
- "what was generated matches what is on disk" does not replace checking the
  content: it compares output against output.

## Where it applies

**Works** for tools that both read and write in one directory — builders,
checkers, converters, indexers — and anywhere there is a generator and a
derived artefact: indexes, tables of contents, summary tables, storefronts,
aggregated reports.

**Does not work** if the output becomes the next run's input by design — there
you need an explicit generation marker rather than name separation. Nor for a
cache fully computable from its source: there the derived file legitimately
holds everything, because a rebuild restores it. This rule is about data that
is **available nowhere else**.

**Sign of a violation:** the number of processed units grows from run to run
with no external changes; or answering "where does this value come from"
requires opening a generated file.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Stepik-Python-Grader — `core/submission_archive.py` (names outside
`_SOLUTION_FILE_RE`), `tests/conftest.py` (excluding run artefacts).

This catalogue; ArtVsMark/Engineering-Incidents-Playbook#2 — the "Area" column
and its recovery from history.

Replaces: [119](119-tool-artefacts-stay-outside-the-input-mask.md),
[125](125-a-generated-file-is-not-a-store.md) — two doors of one loop: 119
closed the way in through the selection mask, 125 the way in through a store
in a derived file; the boundary of 119 "the output is the next run's input by
design" and the boundary of 125 "a cache computable from its source" are
branches of one "the input is sources only".

Related: [103](103-a-side-effect-guard-blames-the-wrong-suspect.md) — a guard
blaming the wrong suspect, the second incident of 119;
[118](118-keep-the-source-next-to-the-derived.md) — the source next to the
derived; [049](049-derive-state-from-live-artifacts.md) — state is derived
from live artefacts; [075](075-a-guard-that-finds-nothing-must-fail.md) — a
guard that finds nothing must fail;
[005](005-hand-written-numbers-rot.md) — hand-written numbers rot;
[120](120-how-to-run-a-rule-catalogue.md) — how to run a rule catalogue.
