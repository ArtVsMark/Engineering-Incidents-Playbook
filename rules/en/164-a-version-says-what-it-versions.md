# A version number says what it versions

**Area.** contracts, documentation

**Tier.** 1 — rules and roles

**The rule.** A project publishing several independently versioned artefacts
must make every number say **what** it is the version of — in the field name or
next to it, **at the point of reading**. The same key on different subjects
means a consumer will eventually write one number into another's field, and
both sides will still look valid.

**Portable beyond Claude Code.** yes — the subject belongs to any project that
publishes more than one format.

## The incident

The catalogue has four independently moving numbers, and **three of them were
called by the same key** `schema`: the rules export format (1.2), the consumer
answer format (1.1), the consumer summary format (1.0), and the catalogue
release itself (tag `v1.1.0`).

The owner asked first: "why 1.2 if the version is 1.1 — we never released
1.2?" A fair question: in the consumption contract `"schema": "1.2"` sits in
the publisher's block and `"schema": "1.1"` in the consumer's field table, with
no line saying these are different things.

The second case came **from someone else's file and was sharper than the
confusion**. A connected project's `.rules/bindings.json` declared
`"schema": "1.2"` — the EXPORT format number in the ANSWER format field, where
the contract requires 1.1. The file is valid, the consumer's own gate is green,
and the summary column shows what they wrote, not what the catalogue computed.
It was found by a neighbouring project's window reading the contract, not by
the publisher's machinery.

Third, for completeness: another consumer's same key had fallen behind at 1.0.
Of three connected answers exactly one matched the contract.

## Why

A version number is **an assertion about one subject**. While the subject is
identified only by where the number sits, the reader infers it from the
neighbourhood: seeing `schema` next to `@v1.1.0`, they read it as the project's
version.

The mistake **does not break**. A swapped number stays syntactically valid,
passes any shape check and keeps being read — it just means something else now.
Neither side sees the cause until someone asks out loud
([157](157-a-contract-version-bump-is-a-re-read.md)).

Collapsing all numbers into one does not cure this, it trades it: a format may
change between releases, and a release may not touch the format at all. One
shared number gives either false alarms or missed breakage
([041](041-two-honest-numbers-beat-one-averaged.md)).

So the cure is **a name at the point of reading**, not discipline: in the field
name (`export_schema` rather than `schema`), in a comment beside it, in a table
listing every number and what each versions.

## In practice

- **the point of reading is where the number sits**, not where it is explained:
  a note in another document does not help whoever copies the line;
- a publisher shipping one format has no subject here — the rule starts at the
  second independently versioned artefact;
- **version drift must be reported on every change**, not in a nightly run:
  what is collected and delivered to no one has no addressee
  ([142](142-a-scheduled-red-needs-an-addressee.md));
- drift on the CONSUMER's side is not fixed from here — the file is theirs; the
  finding lives in the "fixed elsewhere" section and the publisher's run does
  not go red for it.

## Where it applies

**Works** for a project with an outward contract: an export, a consumer answer,
a summary, an event schema — anything read by machine.

**Does not work** inside a single project with no external readers: there the
format version and the code version coincide by construction, and a second name
only gets in the way.

**Sign of trouble:** two numbers of the same kind sit next to each other in one
document, and telling which is which requires opening a third file.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#148. The formulation arrived from a
connected project reading our contract: one key for four subjects. Related:
[157](157-a-contract-version-bump-is-a-re-read.md),
[041](041-two-honest-numbers-beat-one-averaged.md),
[022](022-one-canonical-document.md).
