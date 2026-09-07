# A trail is an address in someone else's tree: never translate it, and its owner maintains it

**Area.** catalogue, documentation

**Tier.** 1 — rules and roles

**The rule.** An entry's trail points at a place in another repository: an issue
`owner/repository#number`, or a document with a section. That is an **address**,
not prose: it is not translated along with the entry text and not paraphrased.
When the named document is edited, the trail is fixed by **the side that owns the
document** — only they know about the edit at the moment it happens. The
catalogue must publish its trails machine-readably, or there is nobody able to
fix them.

**Portable beyond Claude Code.** yes — the subject exists wherever one document
points at a section of another repository: standard conformance, a requirements
map, links from an ADR into external documentation.

## The incident

7 September 2026, measured against the live tree of `Stepik-Python-Grader`:

| catalogue tree | trail resolved | did not resolve |
|---|---|---|
| Russian | 69 | 2 |
| **English** | **3** | **68** |

The English cause is single and systemic: **the section name was translated
along with the entry text**. `§ Формат коммитов` became `§ commit format`,
`§ Окно-наблюдатель` became `§ the watcher session`. The grader's documents are
written in Russian, and no such sections exist there or can exist: what was
translated was a pointer, not text.

The two Russian mismatches are the second, slower failure: the section
`Диагностика первым` was renamed in the grader to
`Диагностика — первым шагом, а не после часа догадок`, and the trail stayed as
it was. Another trail broke off mid-phrase — `§ Что прощается / §`.

Why this stood for so long: **the catalogue's export did not expose document
trails at all**. Only the "issue" form was parsed, and 89 entries out of 183
looked "without a trail" while every one of them had a non-empty section. A
consumer could not learn which of its documents were named — and therefore could
not fix a trail when editing the document, even if it wanted to.

## Why

The trail is the only thing separating a rule from an opinion: you walk it and
see the incident. A broken trail does not look any worse — the entry reads
exactly the same — but stops being verifiable, and that is discovered only by
trying to walk it.

Hence two asymmetries.

**Translation.** Translating the entry text is required; translating the address
is forbidden — and by eye the two acts are indistinguishable: the translator sees
a line and translates a line. The mistake is cheap to make and expensive later,
and it strikes the whole corpus at once rather than one entry.

**Ownership.** The side editing a document knows about the edit that instant; the
side pointing at it never learns until it walks the trail. So the duty to fix
belongs to the document's owner, not to the author of the link — and that is
exactly why addresses must be published rather than kept to oneself.

## Practical boundaries

- in a trail, the section name is written as in the **foreign** document,
  letter for letter, in its language;
- translating an entry does not touch the trail section — those are addresses;
- when a document is renamed or a section disappears, the trail is fixed by the
  tree's owner, in the same change as the document;
- the catalogue publishes trails machine-readably (`export.rules[].trails`), or
  the duty above cannot be carried out;
- revisit if documents gain stable anchors: the address then points at an anchor,
  and renaming a heading stops breaking it.

## Where it applies

**Works** where you point at a foreign repository that lives its own life: a
rules catalogue and its consumers, conformance to an external standard.

**Does not work** within a single tree: there a link is fixed by the link gate in
the same change, and there is nobody to share the duty with.

**Sign of violation:** a trail points at a document and the named section is not
there — or the section names differ between the catalogue's two language trees.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#355

Related: 044 (an address is a claim about the tree and is verified), 183 (a claim
about a mechanism is checked by a mechanism), 157 (a contract bump is a re-read),
049 (state is derived from live artefacts).
