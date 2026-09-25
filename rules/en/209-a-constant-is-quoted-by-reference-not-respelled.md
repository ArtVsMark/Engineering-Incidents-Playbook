# Text a mechanism prints or recognises is quoted by reference to the constant, not respelled by hand

**Area.** code, gates

**Tier.** 4 — code and tests

**The rule.** Text that a mechanism prints or recognises by a constant — a live
issue's marker, a record's tail, a refusal phrase, a template placeholder — is
taken **from the constant itself** wherever it is quoted: by import in a
neighbouring module, by escaping in a regular expression, by the same function
in a registry body. A hand-typed copy of the letters drifts from the constant
silently on the constant's first edit, and a test that checks against that same
copy will not see it.

**Portable beyond Claude Code.** yes — the subject exists in any code where one
part prints a string and another recognises it: log parsing, tracker markers,
headers in exchange files.

## The incident

**THE NEIGHBOUR'S MEASUREMENT, WHICH THE PROPOSAL CAME FROM** (the mechanisms
project, 21–24.09.2026): five occurrences in three days, all five found by the
outside review.

1. #700 — the registry quoted "review annotations were not read" while the
   mechanism printed "review annotations for #N were not read": searching the
   log by the literal quote found nothing.
2. #711 — a run-refusal phrase was typed by hand into the registry body instead
   of being taken from the constant that prints it.
3. #718 — a regular expression recognised a record's tail by its letters rather
   than by escaping the constant: editing the constant silently broke parsing.
4. #718 — the same tail was typed by hand into the registry body next to code
   that writes it from the constant.
5. #730 — a plan marker was typed by hand although declared as a constant
   nearby.

**On the day each was found, all five copies matched the constant** — nothing
was red anywhere. The drift arrives with the first edit and surfaces where
nobody looks.

**HERE THE PRACTICE WAS ALREADY FOLLOWED — UNDER ANOTHER NUMBER.** Since 11.09
(#486) `scripts/review_findings.py` takes the "Разобрано:" line expression by
import from `scripts/pr_body.py`, and the comment there names the reason: "two
parses of one line would drift silently". The citation was
[022](022-one-canonical-document.md) — whose applicability is documentation and
which explicitly allows repeating "a one-line invariant". So for exactly the
short string 022 answered "allowed", while the working answer was "not
allowed" ([204](204-a-citation-is-checked-by-applicability.md)).

**A FRESH CASE THE SAME DAY.** On 25.09 the rule generator typed the changelog
fragment placeholder by hand, and the changelog gate did not know it at all.
When the gate learned it (#586), the placeholder moved into the gate's constant
and the generator takes it by import. On its very first run that gate rejected
the changelog fragment about the fix itself: the prose quoted the placeholder
verbatim and so became a copy the gate recognised.

## Why

**A copy matches on the day it is made — which is why it is invisible.** Code,
tests and a read of the diff agree: the letters are the same. The drift is born
when the constant is edited, and the editor does not know a second spelling
lives elsewhere.

**Tests do not save it.** Each checks against the constant or against the same
copy, not against the quote in the neighbouring module: each side has its own
green suite, and nobody stands between them.

**This is not 022.** There the subject is a paraphrase between documents, and a
machine does not catch the drift. Here the subject is a literal the machine
prints or recognises letter by letter, and a reference to it is an import or an
escape, not a link between documents. And where 022 allows repeating a short
string, here the short string is exactly what must not be repeated.

**This is not [071](071-deliberate-duplication-is-signed.md).** There the copy
was chosen deliberately for the price of merging and is cured by a signature.
Here nobody chose the copy, and it is cured by removal.

## In practice

- in a neighbouring module — by import; in a regular expression — by escaping
  the constant; in a registry body or a message — by substitution from it;
- the constant lives with the side that **recognises** the text — the gate, the
  parser — and the printing side takes it from there: the recogniser cannot
  drift from its own pattern;
- in prose for a human — a docstring, a comment, a changelog fragment — the
  constant's text is **described, not quoted**, or the prose itself becomes a
  copy and the recognising gate rightly turns red on it;
- there is no general gate and there will not be one: telling a quote of a
  constant from text that merely matches it takes a comparison with the
  constant, and which constants get quoted is a question of meaning. A gate is
  built over a closed set where "recognises" is declared: live issue markers.

## Where it applies

**Works** for text that one part of a mechanism prints and another recognises
letter by letter: markers, record tails, refusal phrases, template placeholders,
headers of lines meant for a machine.

**Does not work** for text only a human reads: there the drift is one of
meaning, and that is the subject of [022](022-one-canonical-document.md). **Does
not work** either for a copy kept deliberately to guard a layer boundary or a
dependency direction: that is [071](071-deliberate-duplication-is-signed.md),
and such a copy is signed, not removed.

**Sign of a violation:** one and the same string sits in two working files, and
one of them prints it while the other recognises it.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/finding-kinds.json`

See also: [022](022-one-canonical-document.md) — an ancestor in spirit and not a
duplicate: it is about paraphrase between documents and explicitly allows
repeating a short string, while here a short string must not be repeated because
a machine recognises it; [071](071-deliberate-duplication-is-signed.md) — a
deliberate copy is signed, an accidental one is removed;
[183](183-a-claim-about-the-mechanism-is-checked-against-it.md) — a claim about
a mechanism is checked against the mechanism; here there is nothing to check
while the copy matches, and so there should be no copy at all.
