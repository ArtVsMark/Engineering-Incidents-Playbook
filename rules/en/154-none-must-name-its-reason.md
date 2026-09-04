# "Held by nothing" must name its reason, or it is silence rather than a state

**Area.** process

**Tier.** 3 — gates and processes

**The rule.** A rule declared unbacked by any mechanism must say **why** there is
none: it takes judgement · the subject belongs to someone else · the check costs
more than the violation · nobody got to it yet. Without a reason, `none` means
two different things at once — "we tried and it cannot be mechanised" and
"nobody tried" — and there is no way to tell them apart, though they cost very
differently.

## The incident

Measured on the catalogue's own answer: **41 records are active and held by
nothing; 5 of them name a reason, 36 stay silent.**

On the same day, three things happened that the silence hides — and each time
the requirement **was already written down**:

| requirement | where it was written | what happened |
|---|---|---|
| "the old record is marked superseded" | [043](043-decisions-are-superseded-not-edited.md), [120](120-how-to-run-a-rule-catalogue.md) **and** a hard prohibition in the charter | record 143 was **deleted**, leaving a gap in the numbering |
| "labels are attached" | [064](064-labels-are-machine-input-not-decoration.md) **and** the pre-PR checklist | ten pull requests in a row carried none |
| "every workflow has a manual button" | [126](126-a-freeze-needs-a-thaw-path.md) | `.github/workflows/agent-pr.yml` lived without one |

In all three the requirement was in a document — in two of the three, in two
documents at once. The obvious remedy, "if there is no mechanism, write it into
the rulebook", had been applied in advance and held not once.

A second measurement from the same day: of four rules that declared themselves
gate-backed and turned out not to be, **three got a real gate within hours**.
"A mechanism is impossible" usually means "nobody attempted one", and only a
named reason can tell the two apart.

## Why

The failure mode is not forgetfulness but **two states that look identical**.

`none` reads the same on a record for which no mechanism can be built and on a
record nobody has got to. The first is not a backlog — there is nothing to build;
the second is precisely the backlog. While they are merged, the metric "backed by
nothing" reports a sum no decision can be made from: 41 is either a lot, or five
legitimate cases and thirty-six debts, and you cannot tell which.

A reason works not by reminding but because **it cannot be written without
thinking**. "It takes judgement" has to be defended; "nobody got to it" has to be
admitted. A line in the rulebook demands neither — it can be written without
deciding anything, which is why it failed three times.

Separately, a reason makes `none` **falsifiable by reading**. "Cannot be
mechanised" next to a subject whose gate takes an hour is a finding you can see.
Before the reason, the only finding was green silence.

## Where it applies

**Does not work** as a replacement for a mechanism. A named reason does not make a rule backed:
154 demands an honest answer, it does not turn `none` into a sufficient state. A
rule with a stated reason is still held by nothing, and the gate backlog is
measured exactly as before.

**Does not work** where the answer comes from someone who does not build the
mechanism. A consumer answers about their own repository, and demanding a
reason from them means demanding they defend someone else's priorities. At home
the catalogue rejects such an answer before merge; at a consumer it is a finding
with an addressee, not a refusal
([051](051-warn-on-likely-block-on-certain.md), [053](053-queue-order-is-a-rule-not-arrival.md)).

**Does not work** on statuses where a reason is already required. `rejected`
and `not-applicable` have carried `why` since the contract began; 154 extends the
same requirement to `active` + `none` rather than inventing a second one.

**Does not work** if the reason is accepted as a four-word menu. A closed
vocabulary of reasons would suit the machine and be useless to a person: "takes
judgement" without naming the judgement is the same silence with a label. The
reason stays prose, and the gate checks that it exists and is not a restatement
of the rule itself.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#197 — the issue about marking a record superseded,
which shows the same mechanism: three documents demanded the mark, the mark did
not exist, and record 143 was deleted. The measurement across 41 records and the
analysis of the three cases live in the catalogue's `.rules/bindings.json` and in
`scripts/check_bindings.py`, where the check itself sits.

Related: [002](002-rule-without-mechanism.md) — a rule without a mechanism stays
an intention; here the point is not that there is no mechanism but that this is
left **unsaid**. [026](026-rejected-findings-must-be-recorded.md) — a rejected
finding is recorded with its reason; 154 asks the same of an unbacked one.
