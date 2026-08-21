# Never link from the original to its copy

**Area.** documentation

**The rule.** The relationship between a source and its showcase is
one-directional. A link from the original to the copy sends the reader to
something knowingly older, and the completeness of the source is measured against
the primary source, not against somebody else's reference.

## The incident

The knowledge base has an external showcase — a separate repository the content
is exported into. Two temptations follow, and both destroy the direction of the
relationship.

**First: linking from an entry to the showcase.** It looks like a service to the
reader while in fact it leads away from where the content is updated to where it
arrives with a delay. The rarer the export, the worse: the link looks most useful
exactly when the copy has gone longest without an update.

**Second: measuring completeness against somebody else's reference.** Since an
external source with similar content exists, it is tempting to check against it.
But somebody else's reference is also somebody's selection, with its own gaps and
its own agenda. Completeness is measured against **the language's official
documentation**, not against whoever happens to be nearby.

Hence the rule is fixed in three places at once: do not link to the showcase from
the data, from the code, or from the interface. An item's address is its own
identifier within its own section; outwards there is only a link to the official
primary source.

## Why

A copy is **always** behind — the only question is by how much. A link from
original to copy is therefore not "convenient navigation" but a guaranteed
dispatch of the reader into the past, from the very place where the present is
kept.

Second: a two-way relationship creates a **loop of authority**. The original
links to the copy, the copy looks like an independent source, somebody edits the
copy, and the divergence can no longer be resolved — each side points at the
other.

Third, on the reference standard: "let us check against the neighbour" replaces
the question. Completeness is a relation to the subject domain, not to somebody
else's product. Taking a neighbour as the standard means inheriting their gaps
and their errors, silently.

## In practice

- the direction is declared explicitly: which one is the source and which the
  showcase;
- the ban applies to **all** surfaces: data, code, interface, documentation — or
  it will seep through the least visible one;
- an item has its own address within its own section, so the temptation to link
  outwards does not arise;
- outward links point at the domain's primary source, not at a copy.

## Where it applies

**Works** for mirrors, exports, showcases, documentation caches, translations.

**Does not work** if by agreement the copy outranks the original — but then it
should be named the source and the direction reversed, rather than having two.

**Sign of trouble:** the reader gets a stale version of something that sits
openly nearby in fresh form.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § architectural invariants (the
glossary's source of truth), `docs/dev/glossary.md` § sources of truth. Related:
[022](022-one-canonical-document.md).
