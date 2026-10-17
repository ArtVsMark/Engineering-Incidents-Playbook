# What is published for others is applied by the publisher at home by the same mechanism

**Area.** contracts, process

**Tier.** 1 — rules and roles

**The rule.** Anything published for somebody else's use — a template, a form,
a requirement, a number — is applied and checked at the publisher **by the
same mechanism** it is offered to the consumer with, or it is stated why home
is different. A check that "it runs" does not count as that boundary: it
answers a different question. Anything published and not used by its
publisher drifts from practice silently: everything is green on the
publisher's side because there is nothing there to check, and the consumer is
the first to notice.

**Portable beyond Claude Code.** yes — the subject is the relationship between
a publisher and a consumer, not the workings of an agent session: a library
with a schema, a service with an API contract, the owner of a shared pipeline
and a project handing out templates all have it.

## The incident

**A template the catalogue did not use, 31 August** (the catalogue,
ArtVsMark/Engineering-Incidents-Playbook#213). The catalogue hands out
`templates/preflight.py`. Its first line promises "one run instead of a
checklist in the documentation", and its header names the rule it
implements — 002.

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

Then three cases in two weeks, all at the publisher of a rules catalogue, and
none of them found by its own gates.

**The signature under a re-read, 8 September** (the catalogue,
`scripts/check_reread.py`). The catalogue requires of its five consumers: the
`answers_to` number goes in last, as a signature under re-reading the answers,
never instead of it. Its own commit bumped two contracts and stamped itself the
new number while touching **exactly one** answer record — and that one only to
describe a mechanism. A requirement sent to five was applied to itself zero
times.

**Asymmetric strictness, 10 September** (the catalogue). The `where` field in a
consumer's answer must carry a **resolvable address**: "a gate whose address
cannot be named usually is not a gate". The neighbouring `trail` field — a
rule's own trace at the publisher — was only checked for being non-empty. The
price: **12 records out of 195** reached consumers with an empty `trails` while
eleven of them named an address in the text. Seven were created by the
publisher's own record generator, whose refusal promised "a named artefact,
prose does not count" — and let prose through.

**Numbers published for comparison, 10 September** (the catalogue,
`scripts/sync_inbox.py`, `scripts/build_rules_index.py`). The catalogue
publishes **six** contract numbers in the file consumers download, precisely so
they can compare them against their own. **One of the six** was compared. A
bump of `proposals` to 1.1 reached nobody: the consumer's file declares 1.0,
and there was no one to say so. In the same document the `contracts` example
was typed by hand and drifted so far it became a **physically impossible
moment**: `proposals: 1.1` alongside `export: 1.4`, when the former happened
while the latter was 1.7.

**Where the merge came from.** This rule merges
[155](155-a-template-you-dont-use-drifts.md) and
[197](197-a-publisher-uses-what-it-publishes.md) on the proposal
ArtVsMark/Engineering-Pipeline-Mechanisms:merge/what-is-published-is-used-by-the-publisher
(ArtVsMark/Engineering-Incidents-Playbook#645, review #744). The signal: in the
export 155 refined 197; the "one whole" card answered yes to all four
questions — one cause, one breakage, one claim, one boundary.

## Why

**A publisher gets no feedback from its own publication.** The consumer
receives the file and runs into it: a wrong form breaks their run, a stale
number breaks their answer. The publisher receives nothing — its build is green
because the subject of the check sits on somebody else's side. Your own
practice is edited by every change and goes red on the first run; what is
published is never executed at home, so nothing checks whether it is still
true — it changes only when somebody remembers it. The divergence exists from
day one and has no observer.

**The drift is one-directional, and that is what separates it from two copies
of the same knowledge** ([022](022-one-canonical-document.md)). Two copies
inside a project both drift, and both are visible. What is published drifts
one way and stays invisible: the consumer would be the one to notice, and the
consumer says nothing — they do not know how the publisher works, and they took
the publication as a model precisely because they do not. A template is a
special case: the same breakage on a narrow subject, which is why 155 and 197
are one rule, not two.

**A requirement placed on others is a claim that it is both feasible and
useful.** Not applying it at home verifies neither. Both times the catalogue
turned its own requirement on itself, it immediately found a defect: an overdue
signature the first time, twelve records the second.

**Symmetry is cheaper than an audit.** A separate "do we do what we demand"
check is one more mechanism to remember, and it will go stale itself. One
predicate serving both directions cannot go stale by construction: it either
works for everyone or for nobody, and that shows at once.

The asymmetry of cost: drifted practice at home costs one red run. A drifted
publication costs somebody else's time in somebody else's repository, where
nobody will compare it against the original.

## Practical boundaries

- what is published is used at home **the same way** it is offered: not "we do
  the same by hand", but the same executable step;
- one predicate for both directions, not "an equivalent one": two copies of a
  judgement diverge silently ([022](022-one-canonical-document.md));
- at home the requirement is held by **the same class of mechanism**:
  promising a gate and keeping a document for yourself restores the asymmetry
  under another name;
- "the template starts" is not a check of use and does not stand in for one;
- a number published for comparison is **derived** at the publisher, never
  typed ([005](005-hand-written-numbers-rot.md)): otherwise it drifts first;
- "we do it differently because…" is a legitimate answer, but it is **written
  down**: a silent exception is indistinguishable from an oversight, and "we
  differ" from "we forgot";
- the check of a requirement against your own practice hangs off
  **publication**, not off the calendar: contracts move rarely, and a monthly
  check goes stale between bumps.

## Where it applies

**Works** for anyone publishing a template, a form, a requirement or a number
for others to compare against: a rules catalogue, a library with a schema, a
service with an API contract, the owner of a shared pipeline, a project handing
out templates and config samples — and especially where a template names the
rule it implements: such a template claims more about itself than "here is an
example".

**Does not work** where the published subject is not reproducible at the
publisher: a requirement about an environment it does not have, a scale it
never reaches, a role its project does not contain — including a template
whose subject is physically absent at home: a sample for another language or
another platform. Symmetry is impossible there, and the honest answer is to say
so rather than fake a check against a forgery: an invented subject is worse
than a missing one — it looks like experience.

**Does not work** for requirements that have no machine form at all either:
"the code must be readable" cannot be applied at home by the same mechanism,
because nobody has one ([057](057-unmechanizable-rules-are-named-explicitly.md)).

**Sign of a violation:** the requirement placed on a consumer is stricter than
the check of the same subject at home; a special case — the project's own
documentation contains exactly what its template offers to replace. A quick
probe: take your most recent contract and ask what happens if the publisher
breaks it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Engineering-Incidents-Playbook#213

ArtVsMark/Engineering-Incidents-Playbook — `scripts/check_reread.py`
§ Издатель освободил себя от требования.
ArtVsMark/Engineering-Incidents-Playbook — `scripts/sync_inbox.py`
§ СВОИ_КОНТРАКТЫ, the comparison of all three numbers describing consumer files.
ArtVsMark/Engineering-Incidents-Playbook — `scripts/build_rules_index.py`
§ CONTRACTS_MARKER_RE, contract numbers in the document rewritten by the build.

Replaces: [155](155-a-template-you-dont-use-drifts.md),
[197](197-a-publisher-uses-what-it-publishes.md) — 155 refined 197 for
templates, and the boundary of 155 "the subject is physically absent at home"
turned out to be a special case of the boundary of 197 "the published subject
is not reproducible at the publisher".

Related: [153](153-foreign-why-is-a-link-not-a-copy.md) — the same adjacency
with the sign reversed: it forbids copying somebody else's rationale in, this
one requires running your own published material at home;
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — "the template starts" is
a gate with nothing it must reject, but 140 speaks about checks and this one
about an artefact that is never executed; [002](002-rule-without-mechanism.md)
— the template is what the checklist is replaced with;
[022](022-one-canonical-document.md) — two statements of one territory both
drift and both are visible, and this is the same mechanism running one way;
[021](021-split-docs-by-reader.md) — a publication's reader is outside, and
their corrections never come back; [005](005-hand-written-numbers-rot.md) —
numbers in documentation; [142](142-a-scheduled-red-needs-an-addressee.md) — a
finding about somebody else's file has an addressee, and it is not the
publisher; [220](220-a-mechanism-is-also-subject-to-the-rules-on-mechanisms.md)
— a mechanism obeys the rules on mechanisms even if it is given to no one.
