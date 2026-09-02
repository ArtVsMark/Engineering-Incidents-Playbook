# A generated file cannot be a store

**Area.** catalogue, data

**The rule.** Data lives in the source the derived file is built from. A
generator reads **sources only**, never its own output: otherwise the sole
source of a value is its own previous copy.

## The incident

The catalogue index carried an "Area" column — a subject classification: 124
rules, two languages, 51 areas. The value came from an `old_areas()` function
that parsed **the previous index and the generator's own output** — derived
files, both of them.

While the row format held still, this worked. Then the index was rewritten: two
single-language indexes were merged into one bilingual index, and the table row
went from `| [001](001-transport-rest-not-graphql.md) | … | quotas, API |` to
`| 001 | … |`. The regular expression expected the number in square brackets and
stopped matching.

The whole classification disappeared in a single rebuild. It was not spotted
quickly, and not from the inside: the owner reported the empty column after
seeing it in the finished index.

The gate stayed green throughout, and that is the heart of the incident. The
`build_rules_index.py --check` run compares the generated text against the one
in the repository — but the empty column was in both, and they matched. The
check truthfully reported "index up to date", 124 rules. It was comparing output
against output, and the data was in neither.

Recovery was possible only because the deleted file survived in history:
`git show 5f429e0^:rules/ru/README.md`. Without that commit, 51 areas would have
had to be assigned again by hand across 124 rules — that is, invented again,
because the original classification existed nowhere else.

## Why

**A derived file has no author.** The data in it exists exactly until the next
rebuild. When a generator reads its own output, the loop closes: the only source
of a value is its own previous copy. The data survives on inertia, and any
change of format is not an error but a silent reset.

**Emptiness looks like a value.** Hence the indistinguishability: the column is
there, the rows are there, the rule count is right — one field simply is not
filled in. No existing gate could catch it, because there was nothing to diverge.

The asymmetry of cost is what gives the rule its shape. Reading a source and
finding no data is a **loud** failure: the file is missing, the field is missing,
parsing fails. Reading your own output and finding no data is a **quiet** result:
an empty field, zero records, "just not filled in". The first is fixed within the
hour; the second lives until somebody happens to look from outside.

Hence a fix in two parts, and one part is not enough. Move the data into the
source — into the rules themselves. And **make a missing field fail the build**
rather than render an empty cell
([075](075-a-guard-that-finds-nothing-must-fail.md)): as long as an empty value
is acceptable, it will return at the next change of format.

## In practice

- data is stored in the file it describes, not in a summary about it;
- the generator reads sources and takes **nothing** from its own output,
  including earlier versions of that output;
- a missing mandatory field fails the build and names the file, instead of
  rendering an empty cell;
- a field that genuinely is optional is declared optional explicitly — otherwise
  an empty value passes for data;
- "what was generated matches what is on disk" does not replace checking the
  content: it compares output against output.

## Where it applies

**Works** anywhere there is a generator and a derived artefact: indexes, tables
of contents, summary tables, storefronts, aggregated reports.

**Does not work** for a cache fully computable from its source: there the derived
file legitimately holds everything, because a rebuild restores it. This rule is
about data that is **available nowhere else**.

**Sign of a violation:** answering "where does this value come from" requires
opening a generated file.

## Trace

This catalogue; ArtVsMark/Engineering-Incidents-Playbook#2 — the "Area" column and its
recovery from history. See also:
[118](118-keep-the-source-next-to-the-derived.md),
[049](049-derive-state-from-live-artifacts.md),
[075](075-a-guard-that-finds-nothing-must-fail.md),
[005](005-hand-written-numbers-rot.md),
[120](120-how-to-run-a-rule-catalogue.md).