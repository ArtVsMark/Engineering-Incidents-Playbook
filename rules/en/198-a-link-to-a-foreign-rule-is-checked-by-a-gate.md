# A link to a foreign rule is checked against its export, not written from memory

**Area.** documentation, gates

**Tier.** 3 — gates and processes

**The rule.** A link to a rule in somebody else's catalogue is checked by a gate
against **that catalogue's export**, not against the author's memory. The number
and the address are checked **separately**: "no such rule" and "the rule exists,
the address is wrong" are different findings, different fixes and different
costs.

**Portable beyond Claude Code.** yes — the subject is a link to a foreign
document identified by a stable id. The same holds for links into somebody
else's specification sections, standard clauses, or decision records.

## The incident

The mechanisms project justifies nearly every mechanism with a link to a rule:
there are **300** of them in its tree. A check on 10 September found **29
broken**.

In all twenty-nine the **number was correct** while the filename had been
written from memory, close in meaning: `046-a-red-must-name-its-cause.md`
instead of the real `046-name-the-gaps-do-not-level-them.md`. The guess about
the rule's content was nearly right — which is exactly why the error did not
stand out.

The platform answers such an address with a 404, and no run ever said so. An
external reviewer found the first one; **a mechanism found the other
twenty-eight in a single pass** — a ratio that shows the subject was never
attentiveness.

**Two more cases happened while this record was being written, back to back.**
Linking from here to 185, the author wrote
`185-a-trail-is-an-address-in-a-foreign-tree.md` — by the sense of the rule —
while the file is called
`185-a-trail-is-an-address-and-its-owner-keeps-it-alive.md`. Minutes later, in a
neighbouring record of the same pass:
`127-numbers-in-prose-need-a-marker.md` instead of
`127-a-number-in-prose-needs-a-guarded-marker.md`. Both times the guess was
close in meaning and wrong in address; both times the own-tree link walk caught
it on the very first build, not care.

That is a measurement of the method rather than a slip: thirty-one cases, two of
them by the author of the rule about them, who knew the subject at that very
minute.

## Why

**A broken link devalues the argument twice.** The reader can neither verify the
claim nor tell "the author cited something that does not exist" from "the author
cited correctly and the address went stale". The second is repairable and does
not discredit the argument; the first means there was no argument. Being
indistinguishable, both read as the first.

**The number is stable, the address is not.** A foreign catalogue neither reuses
nor changes a rule's number — that is its own commitment. The filename contains
a slug, and the slug belongs to the owner of the tree
([185](185-a-trail-is-an-address-and-its-owner-keeps-it-alive.md)): they may rewrite it
without asking, and your link breaks from somebody else's edit. The two halves
of the link therefore have different natures, and checking them with one check
mixes a foreign commitment with a foreign freedom.

**Memory lies especially readily here.** A slug is meaningful, and meaningful
things get reconstructed "by sense" rather than recalled: the author writes what
the rule is about, not what the file is called. Twenty-nine out of twenty-nine
is not spread, it is a signature of the method.

## In practice

- the **export** is what gets checked, not a clone of the foreign repository:
  cloning to verify a link is a price nobody pays, and the check gets turned off;
- the two findings are printed **separately**, each with its own action: no such
  number — the link is removed or replaced; wrong address — the address is taken
  from the export;
- the check names its **coverage**: how many links were examined. Zero examined
  and zero broken are different answers
  ([075](075-a-guard-that-finds-nothing-must-fail.md));
- the export **could not be read** is a third outcome, not "clean": somebody
  else's unavailability does not make your links correct
  ([039](039-three-outcomes-not-two.md));
- the address comes from a field of the export, never assembled from the number
  and a slug in code: an assembled address is the same memory, only compiled.

## Where it applies

**Works** wherever the foreign catalogue publishes a machine-readable export
carrying the numbers and addresses of its records.

**Does not work** when there is no export: then only the address's existence can
be probed by a request, which puts the network inside a gate — a different price,
decided separately. **Does not work** for links inside your own tree either:
there an ordinary link walk covers the subject, and a second answer to the same
question is not needed ([022](022-one-canonical-document.md)).

**Sign of violation:** the tree contains a link to a foreign rule and no run
answers the question "does it lead anywhere".

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `scripts/check_rule_links.py`

Related: [166](166-check-the-link-not-the-path.md) — when checking a link, look
for a link rather than a path in the text: this record says WHAT to check,
that one says HOW; [185](185-a-trail-is-an-address-and-its-owner-keeps-it-alive.md) — an
address in a foreign tree belongs to its owner, which is why the number and the
slug differ in nature;
[190](190-a-consumers-answer-about-a-neighbour-is-asked-not-remembered.md) —
the same device on a neighbouring subject: a neighbour's answer format is asked
for, not remembered.
