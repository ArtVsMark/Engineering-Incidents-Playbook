# A rule held by nothing asks the neighbours first

**Area.** process

**Tier.** 3 — gates and processes

**The rule.** Before building a mechanism for a rule that has none, look at
**what holds that rule in the projects answering to the same rulebook** — and
if the technique carries over, repeat it. A neighbour's answer is not an order:
it names whoever has already paid for that mechanism. The "solved next door"
list is assembled by machine from answers you already have, not by walking
other people's repositories.

**Portable beyond Claude Code.** yes — the subject belongs to any shared
rulebook several projects answer to: a dependency policy, a set of security
controls, a family standard.

## The incident

**On 31 August, in one window, the "held by nothing" queue was worked twice —
and both times the technique arrived from outside, carried by a person rather
than by a mechanism.**

First the owner said it out loud: look at how other projects handle this. The
window went to the profile showcase, found `audit_voice`/`audit_harness` there
— a metric raised into a refusal — and ported the technique in a single pass.
Here the same metric had been printing numbers for weeks and leading nowhere;
two gates stood with no rejected subject at all.

Later the same day it turned out **the answer was in our own tree**. Measured
on the spot: of the 31 rules the catalogue holds by nothing, **29 are held at
the grader** — by a gate, a pipeline step or a document, with a named address.
Among them 021 (splitting documents by reader: it has
`scripts/check_docs_guardrails.py`), 040 (a skipped test: `skip_inventory.py`),
124 (rerunning a check: `rerun_flaky_checks.py`). The `export/where.json`
summary had been assembled nightly all along; nobody ever read it in that
direction.

Worse: **the reverse direction had been built that very day.** The catalogue
puts a "solved next door" section into the CONSUMER's inbox. It never put one
into its own.

## Why

"Held by nothing" is a queue, and a queue needs an order. The cheapest item is
the one somebody has already solved: a neighbour's mechanism comes with its
price, its boundary and the edge cases that made it look the way it does. The
rule's own text carries none of that — the rule says **what** to hold, the
neighbour shows **with what**.

And the data was there, saying nothing. The consumer's answer sits in the
shared summary, is assembled by a run and asks nobody anything: a question not
asked is indistinguishable from data that does not exist. The mechanism here
does not produce knowledge — it **puts the question at the moment the work is
chosen**.

Hence the shape: a metric with addresses, not a refusal. Someone else's
technique need not fit — stacks differ, and a rule closed by a gate next door
may be inapplicable here entirely. Going red on "they have it and you don't"
would train people to skip red
([051](051-warn-on-likely-block-on-certain.md)), while the knowledge is needed
by whoever picks the work, not by whoever submits it.

## In practice

- ask **before** building: afterwards it is already a second implementation of
  one algorithm ([090](090-shared-helpers-move-up-not-sideways.md));
- carry over the **technique, not the file**: their script calls their paths,
  and a copy drifts from the original silently;
- "held by nothing there either" is an answer too: the subject is hard, and
  building costs more than it looks;
- only answers with a **resolvable address** count: a paraphrase of a
  neighbour helps no more than its absence.

## Where it applies

**Works** where more than one project answers to a single rulebook: a registry
of consumers of a shared catalogue, a monorepo with shared policies, a family
of services under one standard.

**Does not work** for a lone project: there is nobody to ask, and the
requirement turns into ceremony. It also does not work for a rule whose
subject the neighbour does not have: a mechanism built for agent sessions is
useless to someone who has none — and that answer must be told apart from an
applicable one, or the list turns into noise.

**Sign of violation:** a mechanism built from scratch while a neighbour's was
already there, dissected and named by address — and you learned it afterwards,
from a person.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#148

Related: [002](002-rule-without-mechanism.md) — a rule without a mechanism is a
promise; 162 answers the next question, where to get that mechanism most
cheaply; [090](090-shared-helpers-move-up-not-sideways.md) — a shared technique
moves up instead of being written twice, and here the same economy is applied
across project boundaries; [153](153-foreign-why-is-a-link-not-a-copy.md) —
someone else's "why" is taken as a link, not a copy, which is also why the
technique travels and the file does not;
[105](105-an-outside-audit-needs-outside-eyes.md) — an outside view sees what
the author cannot; here it arrives not as an audit but as a neighbour's ready
answer.
