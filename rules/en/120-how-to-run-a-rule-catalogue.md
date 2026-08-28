# A rule catalogue runs by its own rules, and its index is generated

**Area.** catalogue, process

**The rule.** The catalogue has a unit (a file), a number, mandatory sections, and
**a two-way link to the project through the Trace field**. The reverse index —
"which rules apply here" — is **built from the traces**, not maintained by hand.

## The incident

Rules accumulated wherever they were born: a line in the project's rulebook, a
paragraph in a working document, a comment next to the code, an analysis inside an
audit report. Each was appropriate where it sat.

Gathering them into a catalogue meant going through eight documents, a dozen
decision records, comments in the sources and an archive of reports — and some
were only found by exhaustive search. In other words, **the project's own author
could not enumerate their own rules**, although all of them were written down.

The first obvious answer — create a folder of links inside the project —
reproduces a defect already known: a **third source** appears that nobody updates.
The wording lives in the rulebook, the history in the catalogue, and the list of
links starts falling behind with the very first new rule, silently.

## Why

A rule exists in two forms, and they are not interchangeable. **The wording** is a
short instruction where people act on it. **The record** is the incident, the
reasoning, the limits of applicability; without it the wording cannot be defended
a month later.

The link between them must be **single and one-directional**: the record knows
which part of the project it concerns (the Trace field), and the project knows
about the catalogue through one link. Everything else — including the list of
"which rules apply here" — is **derived** from that link.

Hence the key point: the reverse index is not written, it is **assembled** from
the Trace fields. Then it cannot fall behind: a new rule with a trace appears in
the index by itself, and a rule with no trace does not enter the index — which is
correct, because a rule with no trace applies nowhere.

That also answers the question of accounting. A rule counts as **adopted in the
project** if it has a trace in that project. Not a list of adopted rules, not tick
boxes — the presence of a trace is the criterion.

## How the catalogue is built

- **one file, one rule**, a three-digit number, numbers never reused even after a
  deletion;
- **mandatory sections**: the rule (two or three sentences) · a specific incident
  · why · where it applies (including where it does **not**) · trace;
- **the file name** is the number plus a short Latin slug, so the link reads;
- **the catalogue index** is a table reassembled from the files rather than edited
  by hand: otherwise a broken ordering and a missing row are inevitable;
- **revision** means a new record while the old one is marked superseded; editing
  after the fact erases the reason for the transition;
- **related rules** are listed as links: a rule connected to nothing is usually
  either a duplicate or too general.

## How the project connects

- the project's rulebook holds **the wording and a link**, not a retelling;
- the catalogue holds **the trace**: a file, an issue or a document where the
  breakage is visible;
- the reverse index ("which rules apply here") is **generated** from the traces
  and lives beside the project's working documentation;
- the generator has a test and it fails when a trace points nowhere: a rule
  referring to a deleted file is a signal that the subject changed.

## So that rules are followed, not merely present

The index answers "which rules exist". Separately you need an answer to "what
**holds** each one", or the catalogue becomes a library of good intentions. Three
levels, assigned to every rule:

- **a gate** — it fails automatically, compliance does not depend on memory;
- **a process step** — a human checks it at a named moment: before submitting,
  when raising a task, after a wave;
- **nothing** — there is no mechanism, and that is admitted out loud.

The third level is no disgrace but a **queue for automation**, yet it must be
visible **as a number**: "this many rules are held by nothing" is a metric, and it
must go down. Dissolved in prose, that level looks as though it does not exist.

And last, the most practical point: the index is for review, while **in the work**
a rule takes effect only if it reached the place where people act on it — the
project's rulebook as a compact trigger, the opening message of a new executor,
and the text of the brief. The catalogue by itself makes nobody do anything.

## Where it applies

**Works** when there are more than a couple of dozen rules and more than one
project.

**Does not work** for a dozen rules in one repository: there the catalogue costs
more than the rulebook.

**Sign that it is needed:** nobody can answer "what rules do we have" without
searching the repository.

## Trace

This catalogue; ArtVsMark/Stepik-Python-Grader#1342. Related:
[080](080-every-new-rule-goes-into-the-catalogue.md),
[049](049-derive-state-from-live-artifacts.md),
[005](005-hand-written-numbers-rot.md),
[125](125-a-generated-file-is-not-a-store.md),
[129](129-a-catalogue-needs-a-consumption-contract.md) — this rule continued
into consumption: "no trail" no longer means "not in force".