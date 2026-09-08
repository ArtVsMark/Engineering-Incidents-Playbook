# A placeholder with a brake is filled in the same pass as the work that created it

**Area.** pipeline, process

**Tier.** 2 — the pipeline and CI

**The rule.** A placeholder that a mechanism creates in place of a human and
holds with a brake until it is filled gets filled in the SAME pass as the work
that produced it. Otherwise the brake engages exactly as designed, and that looks
like a broken pipeline — so people go investigating the mechanism instead of the
unfilled text. A second requirement for anyone editing such a placeholder
mechanically: read what is in it before writing back.

**Portable beyond Claude Code.** yes — the subject exists for any held
placeholder: an issue template, a draft with a mandatory field, an approval form.

## The incident

A profile showcase, 7 September 2026. The run that opens a change puts a
placeholder in the body carrying the marker `<!-- hold: body not filled -->`; the
brake releases automatically as soon as the marker disappears.

In one day the window pushed a branch three times, waited for the change to open,
and moved on to the next task without filling the body: changes #137, #138 and
#141 stood still. The owner asked "what are we waiting for", and later "merge
them in order since the pipeline won't" — that is, a mechanism working CORRECTLY
was taken for a broken one.

The second pass went worse. The window was appending attribution trailers to
bodies with a script: it read the body through the API and wrote it back —
together with the marker it never noticed. Its own edit reaffirmed the
placeholder, and the brake stayed engaged through the fault of the very party
releasing it.

## Why

A brake on a placeholder is a deferred refusal: it fires not where the omission
happened but where someone looks. Time sits between the omission and the
observation, and in that gap the symptom loses its author: you see the change is
stuck, and not why.

Hence the requirement to fill it in the same pass. It is not about tidiness but
about addressing: while the work is at hand, filling takes a minute; an hour
later it is an investigation of an unrelated incident, and usually by someone
other than whoever left the gap.

The second half concerns mechanical edits to such text. A tool that reads the
whole text and writes it back carries the holding marker along, because it does
not know about it. The edit looks successful: the write went through, the text is
there. So whoever edits a placeholder mechanically must READ it, not merely
append.

## In practice

- the placeholder is filled in the same pass as the work that produced it;
- a tool editing a body mechanically first reads it for holding markers, and
  only then writes;
- the brake's message names WHAT is unfilled and where — otherwise it is
  indistinguishable from a broken mechanism;
- a placeholder nobody holds is exempt: there the omission is visible at once.

## Where it applies

**Works** where a mechanism creates text in place of a human and holds it until
filled: a change body, an issue created from a template, a draft with a mandatory
field.

**Does not work** for placeholders without a hold — their omission is visible
immediately and costs one glance. Nor does it apply where the same mechanism
fills them: if the text is assembled entirely by machine, a human has nothing to
add.

**Sign of violation:** a change is stuck, the brake was never released, and the
investigation goes to the mechanism rather than to the text.

## Trace

ArtVsMark/ArtVsMark#137 — and changes ArtVsMark/ArtVsMark#138, ArtVsMark/ArtVsMark#141; the conclusion is recorded in
`HISTORY.md` and in the window's charter

Related: [002](002-rule-without-mechanism.md) — a rule without a mechanism is not
followed; here the mechanism exists and works, and what gets skipped is the step
BEFORE it; [018](018-cloud-checks-nodes-local-checks-chain.md) — a check has an
environment where it is meaningful, and "in the same pass" is exactly that;
[142](142-a-scheduled-red-needs-an-addressee.md) — a deferred signal needs an
addressee; here it has one, but the signal reads as a malfunction.
