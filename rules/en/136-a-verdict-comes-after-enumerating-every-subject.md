# A verdict on a rule comes after enumerating every subject of it, not the first one

**Area.** catalogue, contracts

**The rule.** A project answering an external rule first enumerates **all** of
its own subjects of that rule, and only then writes a verdict. A rejection
argued from the first example that came to mind rejects that example, not the
rule — and hides the place where the rule is broken.

## The incident

A profile showcase was answering a rule catalogue about rule
[004](004-conflict-is-normal-not-outage.md) — "a conflict is normal traffic; the
traversal skips the object and carries on". The recorded answer read:

> `rejected` — the showcase build fails as a whole on purpose: the elements are
> linked, the page is rewritten in one piece, and skipping a metric would leave
> yesterday's number on it.

The verdict is correct for exactly the subject it names. More than that, rule 004
carves that case out itself — "does not work when the elements are linked". So it
was not a rejection at all: it was a pointer to the rule's own boundary, filed
under "rejected".

There were **two** subjects. The second was the traversal over open changes in
auto-merge — precisely the machinery rule 004 grew out of: a queue stalled on one
conflicting change. It was never examined.

A run against a stubbed API, two green ready changes, the first merge refused
with `405 Method Not Allowed`:

```
RESULT: the traversal DIED WHOLE on the very first change
        the second (green, ready) was never examined
```

The rule was broken in the exact place it was written for — while the answer
against it said "rejected".

## Why

**A verdict on someone else's rule is a claim about a set**, not about an
example: "in every place where we have a subject of this rule, it holds, fails to
hold, or there is no subject". It gets written after a single case, because a
single case is enough to make the sentence sound convincing.

**The error is one-sided, and that is what it costs.** The subject found first is
usually the one with a convenient answer: where the rule holds, or where it has
an exception. The place where the rule is broken is not looked for, because the
verdict is already written and already looks justified. So the error is not
scattered in both directions — it systematically hides violations.

**Hence the shape of the field, not merely the advice.** For an active rule,
"what holds it" is plural, and an empty second slot is a question rather than a
formatting matter. For "rejected" and "not applicable" the reason must name
**what was enumerated**: without that, no enumeration happened, and there is
nothing to check the verdict against.

## In practice

- enumerate **before** wording the verdict, never after: a written verdict picks
  its examples to fit;
- name the subjects explicitly — a file, a function, a pipeline step, not
  "the project in general";
- "no subject" is the most deceptive status: it needs enumeration more than the
  others, because it asserts an absence;
- pointing at the rule's own exception is **not** a rejection: the rule has a
  "does not work" section, and landing in it is recorded there, not as a refusal.

## Where it applies

**Works** wherever a project answers an external body of rules: a catalogue's
consumption contract, a compliance checklist, a reply to an audit.

**Does not work** with a single surface: a one-file utility has nothing to
enumerate, and the sweep degenerates into the same single example.

**Sign of a violation:** the reason for rejection describes one concrete
mechanism, and the word "all" does not appear in it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#39 — the analysis and the run; the verdict on 004
in the profile showcase's answer file, ArtVsMark/ArtVsMark.

See also: [044](044-check-the-premise-before-fixing.md) — the same for a finding
rather than a verdict: the premise is checked first;
[129](129-a-catalogue-needs-a-consumption-contract.md) — the contract this field
lives in; [026](026-rejected-findings-must-be-recorded.md) — a refusal is a
decision, and it is recorded with its reason.