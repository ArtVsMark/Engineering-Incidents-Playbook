# A shared helper moves up, not sideways

**Area.** architecture

**The rule.** When two independent subsystems need the same utility, it is moved
to a level **above both**. Importing from a sibling creates an edge that should
not exist.

## The incident

Two subpackages — the glossary and the rule cards — both needed atomic file
writing and a shared database connection. The utilities already existed, but they
lived inside the core.

The direct path — importing from the core — would have created a "glossary →
core" edge: a subpackage that until then depended on nothing would start dragging
in the whole core for one function. After that a cycle becomes almost inevitable,
because sooner or later the core will need the glossary.

The solution: both utilities were moved **above the core**, to the package's top
level, and declared leaves — they import nothing from the project at all. Now
both the subpackages and the core use them, and no new edge appears between them.
The subpackages' only project dependency is on such a leaf, which is effectively
the standard library.

## Why

A dependency graph is spoiled not by big decisions but by small convenient
imports. Each looks harmless: one function is needed, and there it is. A few such
steps later the graph is connected, and nothing can be extracted from it any
more.

Moving up changes the **shape** of the dependency: instead of an edge between
equals there is an edge downwards, to a common foundation. Such edges form no
cycles by construction, and their number is bounded from above.

Hence the mark of a proper leaf: **it imports nothing from the project**. That is
not a stylistic wish but a verifiable property, and it must be verified
mechanically — otherwise the first convenient import repeals it.

## In practice

- the list of leaves is written by name, and project imports are forbidden inside
  them;
- the absence of cycles is verified by a graph test, not by agreement;
- the move upwards is done **before** the second consumer appears, not after the
  third: the third arrives along an already-worn edge;
- if the utility drags context with it (settings, state), it is not a leaf — the
  pure part is separated first.

## Where it applies

**Works** for modular packages where the direction of dependencies matters.

**Does not work** in a flat structure with no layers — there is nowhere to move
up to.

**Sign of trouble:** a subsystem meant to be independent does not build without
its neighbour.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § architectural invariants (leaf
modules), ADR-0011, the import graph test. Related:
[071](071-deliberate-duplication-is-signed.md).