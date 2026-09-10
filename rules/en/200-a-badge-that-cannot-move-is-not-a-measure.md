# A badge that cannot move is not a measure

**Area.** showcases, metrics

**Tier.** 5 — everything else

**The rule.** A showcase badge displays a quantity that **can change**. A number
equal to its denominator by construction is decoration standing in a measure's
place: it says neither where the project is nor that it moved. Before hanging a
badge, name **the event after which it will show something else**.

**Portable beyond Claude Code.** yes — the subject is a figure on a showcase,
not the workings of a pipeline. The same holds for a metrics dashboard, a line
in a report, a number on a slide.

## The incident

A project's badge was captioned "catalogue rules held by mechanisms" and showed
**195 / 195**.

It could never have been anything else. The project answers for EVERY rule in
the catalogue — by construction of the consumption contract: an answer is
mandatory, "unreviewed" is also an answer, and the denominator always equals the
numerator. The caption promised the share held by mechanisms; the figure counted
the share answered.

For **six weeks** the badge stood on the showcase as a measure and was not one.
Neither a mechanism nor a review noticed: the owner did, asking why the
statistics were not being collected in full.

After the fix — **123 / 164**, and the number moves: it grew by six during that
same shift.

## Why

**A motionless number looks like a measure and therefore closes the question.**
A showcase exists to be looked at instead of read; seeing "195 of 195" the
reader draws a conclusion and leaves. A missing badge would have raised the
question; a wrong badge answers it, and in that it is worse than empty space.

**Coverage and support are different quantities, and the first is always 100%.**
Coverage of the answer is held by the contract: not answering is impossible.
Support is held by work: a mechanism has to be built. Putting the first under
the caption of the second, the showcase displays a fulfilled obligation in place
of unfinished work — precisely when there is most of it.

**Reading cannot detect this, but one question can.** Motionlessness is
invisible in the number itself: "195 of 195" and "194 of 195" look equally
meaningful. It becomes visible in the answer to "what event would put a
different number here" — and if there is no answer, there is no measure either.

## In practice

- every badge names its **subject of movement**: the event after which the
  number will differ. Named in words, beside the place where the badge is built;
- the **denominator is shown**: "123 of 164" rather than "75%" — a percentage
  hides exactly what broke here, because 100% and 195/195 read differently;
- the caption and the computation are **checked against each other**: the gap
  between them is the subject, and it is machine-checkable when both sides live
  in one place;
- a badge whose movement could not be named is **removed**, not re-captioned:
  rewording the caption over a motionless number leaves the decoration, merely
  honestly labelled.

## Where it applies

**Works** for progress and coverage figures: the share of rules with a
mechanism, the share of code covered, the share of findings resolved.

**Does not work** for **state** badges, where motionlessness is the good news:
"build passing", "no vulnerabilities", "MIT licence". Their subject is a fact,
not movement, and demanding motion from them is demanding breakage.

**Does not work** for a counter that grows by construction and is useful for
that: the number of rules in a catalogue only ever moves one way, and that is an
honest measure of growth rather than a share.

**Sign of violation:** the badge has no answer to "what event would make this
number different" — or the answer sounds like "that will not happen".

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `scripts/build_facts.py`

Related: [127](127-a-number-in-prose-needs-a-guarded-marker.md) — a number in
text lives only with a marker and a build: that record is about who writes the
number, this one about whether it measures anything;
[174](174-facts-about-a-project-are-published-by-it.md) — facts about a project
are published by the project itself, so a badge is such a publication and the
cost of an error in it falls on somebody else;
[146](146-a-green-gate-does-not-verify-its-premise.md) — green confirms itself,
not the claim around it; the same thing on a showcase.
