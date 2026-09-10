# A name is no proof of ownership: an external resource is verified by a back-link

**Area.** data, showcases

**Tier.** 3 — gates and processes

**The rule.** The claim "this external resource belongs to such-and-such
project" is not proved by a matching name. A name in someone else's registry — a
package, an image, an account — is taken by whoever arrived first. Ownership is
verified by a BACK-LINK: the resource declares a repository in its own metadata,
and that must match the project in question. Compare a SEGMENT of the address,
not a substring.

**Portable beyond Claude Code.** yes — the subject exists wherever a foreign
resource is called "ours": registries of packages, images, domains, service
accounts.

## The incident

A profile showcase spent a month showing a neighbour "release/pypi 2.0.0", taking
the version from the package `claude-code-usage` on PyPI: the name had been typed
into the project's answer by hand and looked obviously right.

The package is someone else's — `Maex-z9/CC_Usage`, by Max, a tray monitor for
token spend. The neighbour has its own release v0.2.0 and its own version badge
`0.2.0`.

The error never looked like an error: a plausible number beside a plausible name.
On the same image, right next to it, sat a badge reading "version 0.2.0" — **the
contradiction was in a single frame** and was read by neither the author nor five
outside reviews. It was found not by reading: while fixing neighbouring metrics,
the build printed both badges one after the other.

The gate took ten minutes to write: PyPI serves `project_urls`, and the back-link
is either there or not. Its first version searched for a SUBSTRING and accepted
`github.com/o/r-fork-by-someone` as its own — found by a forgery in the
self-check suite, not by life.

## Why

A name in someone else's registry is a claimed slot, not evidence. Whoever
arrived first claims it, and matching the project's name means nothing: it is
just as likely for a namesake, a fork, or an unrelated project on the same topic.

The one-way link "we named the name" proves only that the name is taken. The
two-way one — "the resource itself names the repository" — proves ownership,
because the second half is written by the resource's owner rather than by whoever
is talking about it.

Separately, on comparison. `github.com/o/r` is contained in `github.com/o/r-fork`
as a substring, and a substring check accepts precisely the class of foreign
resource it was written to reject. Compare segments — whole and bounded.

The asymmetry of cost explains why reading never catches it: a wrong number looks
more plausible than an empty space. An empty badge raises a question; someone
else's version does not.

## In practice

- ownership of an external resource is confirmed by the resource's own metadata;
- addresses are compared by segment, not by substring;
- no back-link means the resource is not ours, and must not be displayed even
  when the name matches;
- a name typed by hand is a hypothesis until first verified, not a given.

## Where it applies

**Works** for any external registry where the first arrival claims a name and
where the resource carries metadata linking back to its source.

**Does not work** where the registry itself attests ownership — a private
organisation registry, a namespace with ownership verification. Nor does it apply
where the resource publishes no metadata at all: then the answer is "ownership is
not verifiable", not "it belongs".

**Sign of violation:** your own file holds a hand-typed name of a foreign
resource, and a number taken from it is displayed beside it.

## Trace

ArtVsMark/ArtVsMark — `scripts/build_metrics.py` § owns_package, package
ownership is verified by a back-link, and the neighbour's answer now points at
its own release

Related: [049](049-derive-state-from-live-artifacts.md) — state from a live
artefact; here the live artefact is the resource's metadata, not our record of
it; [170](170-green-on-a-forgery-is-a-hypothesis-too.md) — a forgery must name
its source, and here a forgery in the suite found a defect life did not;
[153](153-foreign-why-is-a-link-not-a-copy.md) — someone else's "why" is a link,
not a copy; the same thought about someone else's facts.
