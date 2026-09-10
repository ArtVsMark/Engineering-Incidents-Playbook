# An export without the rule's text gets read by its title — and the error looks like an answer

**Area.** contracts, catalogue

**Tier.** 1 — rules and roles

**The rule.** A catalogue's export gives the consumer the **substance** of a
record, not only its name: at minimum the rule itself — what it requires. A
consumer holding only the title will read the rule by its name, and the error
then looks like a **conscientious answer** — the mechanism is built, the address
is named, the gates are green — with nothing to tell it from a correct one.

**Portable beyond Claude Code.** yes — the subject is whatever is published for
somebody else to act on. The same holds for a requirements register, a checklist,
a policy catalogue: an item's name is not the item.

## The incident

The export carried `id`, `slug`, `title`, `areas`, `tier`, `added`, `files`,
`trails`, `origin` — **the rule's text was not there**, only a path to the file.

Measured on 10 September at the mechanisms project: of roughly twenty rules
whose answer changed during one shift, the text was not opened for all of them,
and **the errors landed exactly where it was not opened**.

- **114** "Migration runs from the current version, not from zero" was read by
  its title as "declare a transition on an incompatible change". The rule
  requires something else — idempotence of each step: "applies only to a state
  that has not been through it". The mechanism was built for the wrong thing.
- **106** "Publicity multiplies the good and the bad — do a real run first" was
  attached by its title to the showcase as "answer the question set". The rule
  says: do not show anything until a real scenario has passed.

Both answers passed the address gate and looked alive. It surfaced **only
because the owner asked** whether the contents were being read. No mechanism
catches an error like that: there is nothing to compare an answer's meaning
against if the meaning is absent from the export.

## Why

**A title sets a direction, not a subject.** It is written short and memorable,
which means it deliberately drops the caveats — and the rule lives precisely in
them. "From the current version, not from zero" and "applies only to a state
that has not been through it" point the same way and demand different things.

**An error made from a title is externally indistinguishable from a correct
answer.** The misunderstood rule has a mechanism, the mechanism has an address,
the address resolves, the gates are green. Every observable sign of compliance is
present; only the match with the meaning is missing, and nobody observes that.

**A path to the file is no substitute for the text.** Formally the substance is
available: open the file. In practice opening costs a trip into a foreign
repository and therefore does not always happen — and it is skipped
**selectively**, wherever the title seems clear. That is exactly where the error
lives: a clear title is the very signal by which the text is left unread.

## In practice

- the **whole rule** is published, not a summary: a summary is a second document
  on the same subject and will diverge
  ([022](022-one-canonical-document.md));
- the "does not work" boundary travels **with its markup**, not as a joined
  string: two contrasted paragraphs merged into one read as a single argument,
  and that is precisely what the consumer decides by;
- the **incident is deliberately left out**: it explains the motive rather than
  the subject, and it triples the size. Whoever needs it follows the address in
  the export;
- adding a field is a **contract bump**
  ([157](157-a-contract-version-bump-is-a-re-read.md)) even when compatible:
  silence about a new field makes the number useless;
- the price is named in numbers: this catalogue's export grew from 231 to 596 KiB.

## Where it applies

**Works** for any register of requirements published for others to act on:
rules, policies, checklists, decision records.

**Does not work** where the consumer is a human who opens the source anyway: the
path is then all that is needed, and a copy of the text creates a second home for
one subject. The distinguishing sign is simple: is it a **machine or a session**
answering from the export, for which opening a file is a separate decision?

**Does not work** for records whose substance does NOT fit a paragraph: if the
rule cannot be handed over in one piece, the subject is the record, not the
export.

**Sign of violation:** a consumer answers about a rule whose text is absent from
the export, and their answer passes every check you have.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/bindings.json`
ArtVsMark/Engineering-Incidents-Playbook#454

Related: [157](157-a-contract-version-bump-is-a-re-read.md) — a contract bump
means re-reading the answers, and adding the rule text was one;
[164](164-a-version-says-what-it-versions.md) — a version says what it versions;
[190](190-a-consumers-answer-about-a-neighbour-is-asked-not-remembered.md) — the
other side of the same exchange: there the neighbour does not remember a foreign
format, here the publisher gives enough that remembering is unnecessary.
