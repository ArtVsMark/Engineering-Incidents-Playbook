# The role line-up covers every layer of the product, not just development

**Area.** roles

**The rule.** There are as many directions as the product has layers. Every layer
has an owner; a layer without one is not a detail but a blind spot. At the same
time, coverage **does not equal** a separate role: a direction may be a profile
of an existing one.

## The incident

A role line-up grows "outward from development": first who writes, then who
checks, then who releases. Layers with no obvious executor never appear at all —
and they stay silent right up until somebody examines them for the first time.

The figures for what accumulates in an uncovered layer. A browser pass produced
**33 findings visible only to the eye**, where reading the same code gave 2.
Locales and user-facing strings gave **12 findings** across files. Both surfaces
had been considered covered: the code had been read, after all.

Checking our own role matrix exposed the same thing from inside. It has rows for
code, tests, design, documentation, security, release and audit — and **no rows**
for accessibility, performance, platform compatibility, resource spending or
presenting the product. Not because we decided not to do them: the question was
simply never asked.

## Why

A role is not a job title and not a set of skills but **a question somebody is
obliged to ask**. An unasked question leaves no trace: no task, no finding, not
even an empty section in a report. That is exactly why gaps in the line-up are
not found by reading the list of roles — the list looks impressive exactly in
proportion to the roles that are already in it.

Hence the mechanism: **completeness is checked by walking the artefacts, not by
enumerating job titles**. A directory, a format, a surface, a channel — each is
asked for its owner. An artefact with no owner names the missing direction
itself, and there is nothing to argue with.

The second method, for what does not exist in the repository yet, is a walk of
questions: who uses this · who will break it · who pays for the run · who fixes
it at night · who arrives tomorrow and does not understand · what becomes of it
in a year · in what language is it read · how does it look to somebody who sees
differently. A question nobody answers is a direction without an owner.

## The map of directions

The name states **the question**, not the profession: job titles change,
questions do not.

**Building**

| Direction | Question | Owns |
|---|---|---|
| Architect | which boundary we hold and what we pay for it | layer boundaries, decision records |
| Application developer | how to do this in our stack | the main code |
| Domain developer | is this correct by the rules of the language or platform itself | a narrow layer: language, idioms, standard |
| Client side | what happens on the user's side | interface code, markup, styles |
| Platform engineer | does this reproduce in somebody else's environment | pipeline, environments, build |
| Release and supply chain | what exactly ships to the user and what it is built from | release, versions, dependencies |
| AI in the product | what verifies the generated output and what goes into the model | model integration, prompts, grounding, consent |
| Model training | on what data, and has the quality drifted | dataset, quality measurement, drift |

**Checking**

| Direction | Question | Owns |
|---|---|---|
| Testing | how do I break this | tests, coverage, reproductions |
| Auditor | what is here that we never asked about | the audit document, findings with location and repro |
| Reviser | does the declared match the actual | front-page numbers, statuses, counters, gate budgets |
| Verifier | prove it — and what is the real severity | verdicts, confirmed severity |
| Method critic | what the phase did not check and where the method was imaginary | the phase's trace: commands, environments, share of new findings |
| Security | what will a bad actor do | threat model, isolation, permissions |
| Data and privacy | what goes outside and with whose consent | consents, collection volume, storage |
| Performance and resources | has it become dearer and slower | measurements, baselines, limits |
| Compatibility | where does this not work, and is that stated | platform matrix, asymmetry table |
| Legitimacy | are we entitled to do this, and on what terms | our licence and our dependencies', external service terms, third-party content |

**Understanding and steering**

| Direction | Question | Owns |
|---|---|---|
| Product analyst | what does the data say about usage | metrics, reports |
| Product owner | what we do now and what we do not | plan, priorities, refusals |
| Direction | where is this going in a year | roadmap, major forks |
| External practice | what has appeared outside and is it applicable here | review, justification for adopting |
| Methodology | does the product teach the right thing | didactics, feedback to the user |
| Economics of the work | what does this cost and in what units | spending, quotas, pace |
| Researcher | what is the quantity, if nobody measured it | a measurement with method, number and limits |
| Scholarly work | is this reproducible and what do we cite | dataset, protocol, publication, citation |

**Explaining**

| Direction | Question | Owns |
|---|---|---|
| Technical writer | is this accurate against the code | documentation for developers |
| Editor | will they read to the end | front page, onboarding, error text |
| Localisation | is this the same in another language | string catalogues, the second front page |
| Design | is this clear to the eye | mock-ups, tokens, interface states |
| Accessibility | is this reachable for those who see and move differently | contrast, keyboard, markup |
| Presentation | what stays in the head five minutes later | demonstration, announcement, release notes |
| Acquisition and onboarding | how does a new person get here and what stops them | first contribution, newcomer labels |
| Community and support | what do those who already arrived say | contact channel, complaint triage |

**About the work itself**

| Direction | Question | Owns |
|---|---|---|
| Executor dispatcher | who is busy with what and what is left ownerless | allocation, walks, handovers |
| Agent process | what proves a result obtained non-deterministically | session rules, waves, prompts, debriefs |

## Coverage is not the same as headcount

Every role costs context in **every** broad answer, so the list must not be
inflated into the map. A direction must be covered; it becomes a separate role
only if it passes admission: its own question, its own artefact, its own
objection to a specific existing role —
[062](062-a-role-must-be-able-to-object.md).

Three typical outcomes when working through the map:

- **the direction exists, the role does not** — nobody is asking the question;
  that is a gap and must be closed;
- **the direction exists but the project has no artefact for it** — no role is
  created, and the direction is marked "no such layer yet"; when an artefact
  appears, come back;
- **two directions, one role** — fine, if the second has no objection of its own.
  Then it is recorded as a **profile**: the same role, a different quality
  criterion.

**There are four checking roles, and they differ by their input, not by
strictness.** The auditor enters from the product's surfaces and looks for the
unknown. The reviser enters from the list of declarations — numbers, statuses,
promises — and looks for divergence from fact. The verifier enters from **one**
finding and tries to refute it. The method critic enters from the phase's trace
and checks not the product but the way it was checked.

They cannot be merged into one, not because of volume but because the finder
cannot prove things to themselves, and the executor of a phase cannot see whether
they were asked the right question. What merging costs —
[086](086-the-finder-does-not-grade-the-finding.md),
[088](088-the-critic-checks-the-method-not-the-subject.md).

**Two directions that are most often confused.** "AI in the product" and "agent
process" sound like one thing, but they are different layers with different
artefacts: the first is the model as **a product feature** (what goes outside,
what grounds the answer, who consented), the second is the model as **a way of
doing the work** (how the executors are arranged, what verifies their output,
what it costs). Usually the first is covered and the second forgotten, though the
second often has more documentation.

"Model training" separates from "AI in the product" by artefact: if the model is
somebody else's, there is one direction, and the questions about datasets and
drift have nobody to address. Your own trained model is its own layer: data,
quality measurement, degradation over time.

**The researcher is neither a trend-watcher nor a tester.** The trend-watcher
answers "what has appeared outside and is it applicable"; the tester answers "how
do I break this". The researcher answers a third question: **what is the
quantity, if nobody measured it**. They do not read surveys and do not break the
product; they run a measurement and bring back a number with a method.

Checking that this is a separate direction is easy from the trace: the cost of an
operation over the expensive transport versus the cheap one (300 against 1), the
cost of a session by age, the density of findings by method (8 confirmed out of
489 against 33 where reading gave 2), the share of a five-hour window taken by
one wave (9–10%). None of those numbers came from usage analytics, from tests, or
from a survey of other people's practice — they were measured deliberately in
order to make a decision. Half the rules in this catalogue were obtained that
way.

The direction's objection is its own and addressed: to the product analyst — "you
have usage data, and the question was about the cost of our own work, which
nobody measured"; to the product owner — "the decision is being made on a feeling,
the quantity was never measured".

**Legitimacy separates from security by its question.** Security asks "what will
a bad actor do", privacy asks "with whose consent". Legitimacy asks "are we
entitled to do this at all": a dependency's licence permitting or forbidding our
way of distributing; an external service's terms; third-party content ending up
in our artefacts; the licence on what we hand out. Its objection to the release
engineer: "this dependency is copyleft, the distribution cannot ship under our
licence" — that one is about the build, this one about the right.

**"Scholarly work" is a conditional direction, like model training.** While there
is no artefact (a protocol, a dataset, a publication), no role is created and the
direction is marked "no such layer yet". Once there is an academic output, its
questions arrive too: is the run reproducible from the description, what
validates the method, what do we cite and how are we cited, and what about
research ethics if people take part.

A special case is directions people are tempted to split along the wrong axis.
Splitting the explaining roles by **audience and quality criterion** works:
accuracy against the code and holding the reader argue substantively, and both
objections are sometimes right. Splitting the same roles along "structure versus
prose" does not work: both halves answer one question and immediately start
repeating each other.

## In practice

- completeness is checked by **walking the artefacts**: a directory with no owner
  names the missing direction;
- every role in the matrix has a "when to engage" line — otherwise the role
  exists only on paper;
- a missing direction is recorded as missing rather than skipped in silence: an
  uncovered layer is a blind spot, not "we do not have that";
- the map is revisited when a new artefact appears, not on a schedule;
- a role's name states the question: job titles age, questions remain.

## Where it applies

**Works** for products with several surfaces and for line-ups of role-playing
executors.

**Does not work** for a one-off utility with a single surface: there the map is
longer than the product.

**Sign of a gap:** a surface is examined for the first time and yields several
times more findings than its neighbours.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/roles.md` § the role matrix; #1007
(33 findings from the browser pass), #1005 (12 findings on locales). Related:
[062](062-a-role-must-be-able-to-object.md) — the other side;
[019](019-audit-from-surfaces-not-files.md) — the same technique for audits;
[032](032-role-must-run-the-product.md).
