# A form the gate cannot see becomes a bypass

**Area.** gates

**Tier.** 3 — gates and processes

**The rule.** A gate that looks for its subject by the **form it is written in**
must read EVERY form that subject is written in across its tree, and the set of
forms is obtained by **measurement**, not by listing from memory. A form the gate
cannot see becomes a bypass — and not a malicious one: that is simply how people
write out of habit, which is why the invisible form most often turns out to be
the commonest. If some form is ambiguous and cannot be read without false
positives, that is stated out loud together with the fact that the gate checks
**not everything**.

**Portable beyond Claude Code.** yes — the subject exists for any check whose
subject is written freehand by a person: a pattern-based linter, a secret
scanner, a command guard, prose parsing.

## The incident

**Ours, live and expensive (2026-09-17).** The hook
`.claude/hooks/push_guard.py` holds rule 202 — "a merged branch is resurrected by
any push". In a single shift it **did not fire once out of three**: branches were
resurrected by a push after merge, the pipeline honestly opened changes onto work
already in the shared branch, and #529 and #531 had to be closed as duplicates.

The cause is not the resurrection check — that one is sound and simply never gets
called. The command is parsed as `re.split(r"&&|\|\||;|\||\n", …)`, and the
segment must **begin** with `git`. Measured by form:

```
SEES  | git push
SEES  | cd X && git push
SEES  | git push; echo
blind | for i in 1 2; do git push; done
blind | while true; do git push; done
blind | if true; then git push; fi
blind | ( git push )
```

Inside any shell construct the segment begins with `do`, `then` or a bracket.

**AND THE COSTLIEST PART: THE LOOP HERE IS A PRESCRIBED FORM, BUT IT IS NOT THE
TREE THAT PRESCRIBES IT.** Pushing with retries and backoff is required by the
WINDOW's own instructions — the ones delivered by the platform when the window
opens — and the catalogue's tree holds no such requirement at all: `grep` across
`AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `templates/` and `docs/`
returns ZERO mentions of a push retry. The first draft of this record attributed
the prescription to the tree, and an outside look showed it could not be checked
by a command — the record demanded of other people's claims exactly what it had
not done itself.

The correction makes the argument stronger, not weaker: the form came from
somewhere the guard's author never looks. A tree can be re-read; a window's
instruction cannot, and so a set of forms gathered from the tree is incomplete BY
CONSTRUCTION here. That is why the miss is not a rare case but the norm. The
repair is tracked as #533.

**Ours, before building rather than after breaking.** Citation forms measured
across the whole tree: **775** mentions written as a link `rules/en/NNN-…`,
**2052** written as a bare number — the invisible form is **2.6× more common**.
We have no citation gate at all: rule 204 is held by a document. So this is a
warning measurement — a gate written for links would see twenty-seven per cent of
its subject and stay green over the rest.

**The neighbour's measurement, from which the proposal came** (the mechanisms
project): their citation-applicability gate read one form, the link. A bare number
in brackets did not count as a citation. The claim written as a link was found and
fixed; its twin, written as a number, lived another six days saying the opposite.
Measured across their tree: **1007** mentions by link against **1744** by bare
number, and **23** rules named ONLY by a bare number. Widening the form found five
live citations of inapplicable rules: one genuine defect, one leftover from a fix
the same day, and three legitimate mentions of a boundary. Verified by rollback:
the old gate is green while the defect is live.

## Why

**The invisible form is the commonest, and that is no coincidence.** A gate is
written for the form its author holds in mind while writing it. The tree is
written differently: whichever way is shorter and more habitual. Two measurements
out of three gave the invisible form a 2.6× lead; the third put the prescribed
form in the blind spot.

**Whoever bypasses does not know they are bypassing.** That is what separates this
subject from a malicious bypass: there is nobody to teach and nothing to forbid.
The only cures are widening the coverage or naming the boundary.

**Green over a live defect is indistinguishable from green over a clean tree.** A
gate with a two-sided suite confirms the mechanism works as declared (146) — but
it was declared for one form. A mutation suite does not catch this: it is written
in the same forms as the gate.

**A list of forms kept from memory goes stale in silence.** It is handwritten
knowledge about the tree and it lives until a neighbour's first edit. The
measurement is the source, not the packaging: it belongs beside the gate and gets
retaken when the coverage widens.

## Practical limits

- the set of forms comes from a MEASUREMENT over the tree, and the measurement
  sits beside the gate as a number, not as the words "all known forms";
- a form that cannot be read without false positives is stated out loud along
  with the coverage — "the gate checks not everything, and here is what it does
  not see"; a silent boundary known only to the gate's author is the defect;
- ambiguity is removed by NARROWING the form, not by dropping it: at the
  neighbour a bare number became readable only when not glued to a name and only
  from their own registry — otherwise platform status codes became citations;
- when the form is widened the gate is checked by rollback: the old one must be
  green over a live defect, otherwise the widening changed nothing;
- "reads every form" does not mean "reads any text": a string argument meant for
  another program is not a form, and a guard watches the action, not the
  occurrence of a word.

## Where it applies

**Works** for gates whose subject is written freehand by a person: a shell
command, a citation, a link, a marker in prose, a pattern in code.

**Does not work** where the subject is given by a NAME in a namespace — there it
must be resolved through imports, and that is
[180](180-a-gate-resolves-the-call-not-the-last-name-segment.md), not a list of
forms. Nor does it work where there is exactly one form by construction: a
machine-generated file, a strict schema, a registry field. There the list of forms
degenerates to one and the measurement becomes a ritual.

**Sign of violation:** the list of forms in the gate is written by hand, and there
is no number beside it saying how much of each form the tree holds.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `tests/test_citation_applicability.py`
ArtVsMark/Engineering-Incidents-Playbook#533

Related: [180](180-a-gate-resolves-the-call-not-the-last-name-segment.md) — there
the subject is a name resolved through imports; here it is a form, and 180 hands
this territory over in its own boundary;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a gate that finds NO subject
at all must fail; here it does find the subject, just not all of it, and so stays
green legitimately;
[146](146-a-green-gate-does-not-verify-its-premise.md) — green confirms itself: a
mutation suite is written in the same forms as the gate;
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — the two-sided suite: a
widened form is checked by rollback over a live defect.
