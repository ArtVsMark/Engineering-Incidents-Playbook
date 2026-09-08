# An exit code reused across modes is read together with the mode

**Area.** gates,tooling

**Tier.** 3 — gates and processes

**The rule.** A tool with more outcomes than exit codes reuses one — and in write
mode that same number means something other than it does in a dry run. The
publisher must separate them: the code says what the tool DID, not what it
found. Until that happens, the reader accepts a reused code only alongside
printed evidence of the work, and names the version that pins its meaning.

**Portable beyond Claude Code.** yes — any tool with a dry and a writing mode
has this: migrations, formatters, bulk data repairs.

## The incident

A scheduled run, `rules-inbox` in `Claude-Code_Usage-Token`, writes back-links
into issues using the catalogue's own tool — `scripts/link_trails.py`, pinned at
tag `v1.1.0`. The last line of its `main` is `return 1 if missing else 0`, where
`missing` is counted BEFORE the writes and never cleared afterwards. A tracker
failure exits with code 2 earlier, so with `--apply` that line is only reached
when every write succeeded: the 1 there means exactly "some were missing and all
of them were written".

Measured 4 September 2026: the run printed "issues with a trail: 12; missing a
back-link: 4 — 4 written" and failed. Every run had been failing this way since
the rule export started being read live — three in a row, two on 3 September and
one on 4 September. Before that the data came from a pinned tag, held no trails
here, there was nothing to write, and the code was zero. **The run was green
exactly while it did nothing**
([146](146-a-green-gate-does-not-verify-its-premise.md)).

Nothing was actually broken: the links were being written. What was red was
reading them.

A second measurement, 8 September, in the catalogue itself while reviewing this
proposal: the behaviour turned out not to be an oversight but DOCUMENTED. The
header of `link_trails.py` said "1 — issues without a back-link exist (with
--apply they have been updated)". The publisher described the reuse and
considered the matter closed; that description was of no use to the consumer,
whose run reads a number, not a docstring.

## Why

An exit code is a contract, and it has exactly three values no matter how many
outcomes there are ([039](039-three-outcomes-not-two.md),
[109](109-every-exit-from-a-transient-state-must-be-terminal.md)). Once there
are more outcomes, some code carries two meanings, and what tells them apart is
not the number but the MODE the tool ran in. The reader does not know the mode:
a scheduled run sees only the number.

The asymmetry of cost cuts both ways, and both are bad. "Non-zero is a failure"
paints success red: the work is done, the run is red, and after three such runs
red stops being read. "Not two is success" swallows a real failure: a finding
nobody addressed looks like a win.

Only the publisher can separate them. A consumer can wrap the read in evidence
of work — but that evidence is parsed out of TEXT, and text changes more freely
than a code. So the duty sits with whoever prints the number.

## In practice

- the code says what the tool DID: a dry run answers by findings, a writing run
  by what is left over after the writes;
- with more than three outcomes it is not the set of codes that grows but the
  output: evidence of the work is printed as a line, the number stays ternary;
- until the publisher does this, the reader names the version that pins the
  meaning and accepts the code only with the evidence;
- documenting the reuse is not a fix: a docstring is read by a human, an exit
  code by a pipeline.

## Where it applies

**Works** for any tool with two modes whose exit code is read by automation:
bulk data edits, migrations, formatters, back-link writers.

**Does not work** where there is only one mode: a pure check that never writes
already has an unambiguous code, and there is nothing to separate. Nor does it
apply to a tool no pipeline invokes — there the reader is a human, who sees the
whole output.

**Sign of violation:** a run prints evidence of completed work ("wrote N",
"fixed M") and exits non-zero.

## Trace

ArtVsMark/Claude-Code_Usage-Token — `.github/workflows/rules-inbox.yml`, step
"back-links to rules in issues"; tests `tests/test_rules_inbox.py`

ArtVsMark/Engineering-Incidents-Playbook — `scripts/link_trails.py`: the
leftover is counted after the writes, and the declared outcomes now match

Related: [039](039-three-outcomes-not-two.md) — there are three outcomes, and
here it shows there can be more of them than codes;
[109](109-every-exit-from-a-transient-state-must-be-terminal.md) — a terminal
status is mandatory, and this one must also mean one thing;
[145](145-every-declared-outcome-is-run.md) — there the code is lost before it
is parsed, here it survives but means the wrong thing;
[157](157-a-contract-version-bump-is-a-re-read.md) — the meaning of a code is a
contract too, and its version is the tool's.
