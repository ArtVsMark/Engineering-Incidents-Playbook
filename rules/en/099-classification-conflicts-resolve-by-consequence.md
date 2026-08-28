# A classification conflict is resolved by consequence, not by correctness

**Area.** taxonomy

**The rule.** When an entity fits two sections at once, the winner is the one
whose absence would leave a section empty or meaningless. An argument about the
"correct" place has no solution; an argument about consequence does.

## The incident

Two generations of filling the reference described three dozen concepts twice:
one entry in a thematic section, another in a catalogue organised by module. The
pairs had to be merged, and that meant deciding where the contested ones go.

An argument about "which is more correct in essence" had no solution: a built-in
function belongs equally legitimately to the section about its data type and to
the flat catalogue of all built-ins.

The **consequence** decided it. The rule came out asymmetric and was recorded
plainly: a module member lives in its module's section; a built-in function stays
in the thematic section and receives an additional label. The reason is named:
otherwise the "data types" section would be left without the basic types, and the
section on objects without its key constructs, while the flat catalogue of
built-ins does not empty — it is flat by construction and complete by definition.

## Why

Classification serves **navigation**, not truth. The question "where does this
belong more correctly" assumes an entity has a true place — and most entities do
not, they honestly belong to several slices.

Replacing the question with "what happens to the sections under each option"
yields a solvable argument with a verifiable answer: an empty section is an
observable quantity.

Second: an asymmetric rule is **better than a symmetric one** if the slices are
built differently. A flat catalogue does not suffer from a removal; a thematic
section does. A rule treating both identically is bound to rob the weaker.

Third: a contested entity need not exist in a single copy. A label, an alias, a
cross-reference give presence in both slices with one canonical place — and that
is cheaper than a duplicate that will diverge.

## In practice

- the rule is recorded together with its reason: "otherwise the section is left
  without X";
- the canonical place has one address; the second presence is a label or a link,
  not a copy;
- check after merging: did any section empty out — that is a sign the rule was
  applied the wrong way round;
- duplicates from different generations are merged keeping the base address,
  with only the unique content poured over from the second.

## Where it applies

**Works** for taxonomies with overlapping slices: catalogues, labels,
documentation sections, menus.

**Does not work** if the slices are independent and the entity honestly belongs
to one — there is no conflict there.

**Sign of trouble:** the discussion of placement lasts longer than filling both
sections would have taken.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/glossary.md` § duplicates from two
generations of import. Related:
[098](098-the-unit-of-splitting-follows-usage.md),
[021](021-split-docs-by-reader.md).