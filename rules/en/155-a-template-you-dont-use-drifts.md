# A template you do not use yourself drifts from practice in silence

**Area.** process, documentation

**The rule.** A template a project hands out — a gate skeleton, a config sample, a
process outline — is used at home the same way it is offered to the consumer, or
it says why home is different. "It runs" is not that check: it answers a
different question.

**Portable beyond Claude Code.** yes — the subject is what a project publishes
for others, and it has nothing to do with agent sessions.

## The incident

The catalogue hands out `templates/preflight.py`. Its first line promises "one
run instead of a checklist in the documentation", and its header names the rule
it implements — 002.

At home the catalogue kept a seven-line "Before PR" checklist. Six lines listed
what a gate already prints. The seventh — "labels are set" — demanded work from
the reader that the pipeline does from the touched paths: it became false the
day labelling moved to the machine, and nobody read it after that.

The template was under check the whole time. The pipeline had a
`templates/preflight.py --list` step, it was green, and it meant exactly what it
said: the template starts. That does not separate a working template from one
that has drifted — both start.

The cost was measured on the next session. Restarted on 31 August with the
checklist in front of it, it assembled the list of gates for a local run from
memory and named 16 of 19: it simply forgot the three steps that need the
context of a pull request.

## Why

Your own practice is edited by every change and goes red on the first run. A
template is never executed at home, so nothing checks whether it is still true;
it changes only when somebody remembers it.

The drift here is one-directional, and that is what separates it from two copies
of the same knowledge (022). Two copies inside a project both drift, and both
are visible. A template drifts one way and stays invisible: the consumer would
be the one to notice, and the consumer says nothing — they do not know how your
project works, and they took the template as a model precisely because they do
not.

The asymmetry of cost follows. Drifted practice at home costs one red run.
A drifted template costs somebody else's time in somebody else's repository,
where nobody will compare it against the original.

## Practical boundaries

- the template is used at home **the same way** it is offered: not "we do the
  same by hand", but the same executable step;
- when the subject does not exist at home, that is **stated** — otherwise "we
  differ" is indistinguishable from "we forgot";
- "the template starts" is not a check of use and does not stand in for one.

## Where it applies

**Works** wherever a project publishes templates, boilerplate or config samples
— and especially where a template names the rule it implements: such a template
claims more about itself than "here is an example".

**Does not work** for a template whose subject is physically absent at home: a
sample for another language, another platform, or a role the project does not
have. Demanding it be used at home would demand inventing the subject, and an
invented subject is worse than a missing one — it looks like experience.

**Sign of violation:** the project's own documentation contains exactly what its
template offers to replace.

## Trace

ArtVsMark/claude-code-playbook#213

Related: [153](153-foreign-why-is-a-link-not-a-copy.md) — the same adjacency
with the sign reversed: it forbids copying somebody else's rationale in, this
one requires running your own published template at home;
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — "the template starts" is
a gate with nothing it must reject, but 140 speaks about checks and 155 about an
artefact that is never executed; [002](002-rule-without-mechanism.md) — the
template is what the checklist is replaced with;
[022](022-one-canonical-document.md) — two statements of one territory both
drift and both are visible, and this is the same mechanism running one way;
[021](021-split-docs-by-reader.md) — a template's reader is outside, and their
corrections never come back.
