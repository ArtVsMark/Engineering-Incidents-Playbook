# Introduce the seam early, generalise on the third case

**Area.** architecture

**The rule.** A known future fork gets a **seam** immediately: a minimal
reversible refactor that fixes the contract. A shared abstraction over similar
implementations is created only when a **third** appears.

## The incident

Two decisions look opposite and in fact complement each other.

**The seam was introduced in advance.** The direction towards a remote mode was
adopted **without implementation**: instead of a product, an execution
abstraction — a minimal reversible refactor fixing the contracts and the security
requirements. The decision's wording is direct: "prepares the ground without
creating a product or its risks ahead of time". Implementation was deferred for
years, while the extension point exists and stops the code fusing together.

**The generalisation was rejected.** Two similar content providers were proposed
for merging under a common interface. Refused **until a third appears**, and the
refusal was recorded so the proposal would not return: merging two
implementations produces an abstraction derived from a sample of two — and it
almost certainly will not fit the third.

## Why

Seams and generalisations answer different questions, which is why their rules
differ.

**A seam** is about **the cost of a future change**. It is introduced when the
fork is already known: we know execution will move, storage will change, a second
channel will appear. A seam does not guess the shape of the future — it merely
stops the code fusing where a cut will certainly be needed. The cost of a seam is
small and **reversible**: not needed, so removed.

**A generalisation** is about the **shape** of the future, and that is exactly
what cannot be guessed. An abstraction from two examples encodes the accidental
similarities of those two: the third arrives with a different shape, and the
abstraction is either broken or stretched. The cost of error here is high and
**irreversible**: the generalisation is already used by everyone.

Hence the test that separates the two cases: **do I know what will change, or do
I merely see that things look alike?** Knowledge of a future change justifies a
seam. Observing similarity justifies nothing until there are three cases.

## In practice

- the seam is minimal and reversible: a contract and a substitution point, with
  no second implementation "for symmetry";
- the decision about the seam is recorded together with the fork it exists for —
  otherwise it will be removed as a redundant layer;
- the refusal to generalise is recorded too: an unrecorded refusal returns as the
  next proposal;
- the third case is a reason to revisit, not an obligation to generalise:
  sometimes three different things beat one stretched abstraction.

## Where it applies

**Works** for extension points: execution, storage, transport, providers.

**Does not work** if the fork is not known but merely imaginable: then a seam is
as much guesswork as a generalisation.

**Sign of error in either direction:** either rewriting half the code for a
predictable change, or an abstraction with a single implementation.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0001 (the seam in advance), ADR-0006 (a
protocol, not a hierarchy), ADR-0010 (generalisation refused until a third
case). Related: [042](042-decision-records-its-alternatives.md).