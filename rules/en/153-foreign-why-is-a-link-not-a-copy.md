# Someone else's "why" is a link, not a copy

**Area.** documentation, code

**The rule.** Do not copy the rationale for **someone else's** decision into your
repository — link to it. Write your own "why" in full, because whoever edits the
code edits it too. A foreign rationale goes stale the moment the other side
changes, and turns into confident falsehood that nothing checks: gates catch a
source failing, never a stale explanation sitting beside it.

**Portable outside Claude Code.** yes — the subject exists for anyone who reads
a neighbouring project and explains, at home, why it is built that way.

## The incident

A showcase repository reads neighbouring projects' figures from their badges.
The rules catalogue kept its coverage badge on the default branch, and the
showcase wrote down in its own code **why** it was there: "the version lives on
a separate branch because it is a property of history and tags, while coverage
is a property of the tree and changes with the same change as the code."

The rationale was **correct**, and it belonged to the catalogue, not to the
showcase.

A day later the catalogue moved its badges to a separate branch for good. The
showcase build failed with `HTTP 404` on
`contents/.github/badges/coverage.json` — a gate caught that. The explanation
beside it went on standing confidently, and would have kept standing had nobody
gone back to read it: it references nothing checkable. Fixing the data took one
word; fixing the explanation took a human re-reading it.

## Why

Two lifetimes diverge here. A neighbour's **data** is verified on every access:
the source either answers or it does not, and the failure arrives on its own. An
**explanation** accesses nothing — it is text, and text cannot fail. So a copy
of someone else's "why" has no moment at which it would ever be checked.

Hence the form: a link keeps **one** source and one editor. A copy creates a
second source with a foreign editor we cannot reach — exactly the divergence
[022](022-one-canonical-document.md) promises always, except here it is also
invisible, because the other side does not know the copy exists.

**Asymmetry of cost.** A missing explanation gets noticed and asked about. A
stale one does not: it looks like knowledge, reads confidently, and is
corroborated by the working code sitting next to it.

## In practice

- someone else's "why" — a link to where it lives and gets edited;
- your own "why" — in full: the same person edits it and the code;
- easy to miss: a rationale that is **correct when written**. The rule is not
  about error, it is about shelf life;
- revisit the decision if the foreign rationale becomes yours — that is, you
  have taken on both the subject and the right to change it.

## Where it applies

**Works** wherever you explain how a neighbouring project is built: their
pipeline, their exchange format, their badges and artifacts.

**Does not work** for a foreign rationale **fixed by a version**: a quote from a
pinned tag, a release, or a record marked superseded does not go stale — the
source no longer moves, and the copy stays true. Nor does it work where there is
nothing to link to: if the other side explained the decision only in a
conversation, a dated copy marked "as of such-and-such" is more honest than a
link to nowhere.

**Symptom of need:** next to a call to a foreign artifact stands a paragraph
about why that artifact is built the way it is, and the paragraph carries no
link to the other side.

## Trace

`ArtVsMark/ArtVsMark` — `scripts/build_metrics.py`: the rationale for where the
catalogue's badge lives was replaced with a link to the catalogue.

Related: [022](022-one-canonical-document.md) — duplicated description always
diverges; here the second editor is out of reach, so collapsing to one document
is impossible and a link is what remains.
[118](118-keep-the-source-next-to-the-derived.md) — source next to derived: for a foreign
rationale we hold no source at all.
