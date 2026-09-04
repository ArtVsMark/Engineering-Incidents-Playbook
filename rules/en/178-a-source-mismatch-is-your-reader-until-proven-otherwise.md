# A source mismatch is your reader until proven otherwise

**Area.** diagnostics, data

**Tier.** 4 — code and tests

**The rule.** When two sources give different numbers about the same thing,
"they measure different quantities" is the **most expensive** explanation
available and is therefore tested **last**. Two hypotheses about **your own**
reading must fall first: "we are counting the same quantity more than once" —
the source repeats it across several records, and summing multiplies it — and
"one snapshot is older than the other" — the aggregate refreshes less often than
the record it sits in. Both are cheaper to test than the nature of the data: the
first by recounting per entity identifier instead of per row, the second by two
queries back to back.

**Portable beyond Claude Code.** yes — the subject belongs to any reconciliation
of two sources reporting one quantity: a log and a metric, a database and its
cache, two APIs.

## The incident

Measured 2 September in `Claude-Code_Usage-Token`: the transcript and the
session registry disagreed about one window **in both directions** — `output`
5.5× larger in the transcript, `cache_read` 3.6×, `input` 5.0× larger in the
registry. The conclusion "the two sources measure different quantities" made it
into the project's specification and blocked building a scale: you may not add
them, you may not complete one from the other, and deduplicating by session does
not help.

**What overturned the conclusion.** A measurement on 3 September, on a
**different** window, produced **different** ratios — 3.03× and 2.96× instead of
5.5× and 3.6×. For genuinely different quantities the ratio would have held.

**Checking your own reading, first hypothesis.** 267 rows carrying spend mapped
to **132 unique** `message.id` values, 1–4 rows per response: the transcript
writes one row per **content block** — text, reasoning, each tool call — and the
`usage` in them is the same one, the full spend of the response. Summing rows
multiplied it by the number of blocks; the `usage` of rows belonging to one
response matched byte for byte — **0 discrepancies across 267 rows**. Counting
per response dropped the ratio from 3.0× to 1.35–1.5×.

**The second hypothesis explained the remainder.** Two queries to the registry
80 seconds apart returned a moved `updated_at` and an **unchanged** `usage`: the
aggregate lags the record it lives in.

Result: of a 3–5.5× discrepancy, "different quantities" explained **nothing** —
and that explanation cost a day of blocked work and a wrong paragraph in the
specification.

## Why

The asymmetry here is not in likelihood but in the **price of the verdict**.
"Different quantities" is terminal: it forbids adding, forbids completing one
from the other, and devalues everything built on those numbers — that is, it
stops the work entirely. An error in that direction costs the whole line of
work. An error in the other direction costs one recount.

Worse, a terminal verdict **seals itself**: once in the specification it stops
being a hypothesis and becomes background — nobody re-measures what is already
explained. So the order of testing matters more than the tests: the cheap
hypotheses fall first not to save effort, but so the expensive one gets
contested at all.

The applicability marker deserves its own attention because it is free: **the
discrepancy is not constant and shifts from measurement to measurement**. For
different quantities the ratio would hold — so the instability of the ratio by
itself refutes the expensive hypothesis, and it comes out of the second
measurement you were going to take anyway.

## Practical boundaries

- before writing "the sources measure different things" anywhere long-lived — a
  specification, a decision record, a report — recount per entity identifier
  rather than per row, and take two snapshots back to back;
- easy to miss: the expensive hypothesis enters the text not by decision but **in
  passing**, as an explanation inside a paragraph rather than a conclusion with
  numbers beside it;
- revisit the decision when the ratio **holds** across measurements and both
  cheap hypotheses have been refuted with numbers: then "different quantities"
  is the right answer, and it is written down together with those numbers.

## Where it applies

**Works** wherever two sides report one quantity: a transcript and a registry, a
log and a metric, a database and its cache, two answers from one API.

**Does not work** where the sources measure different things by construction and
this is **declared in the contract**: the question does not arise there. Nor
does it work for a single source — there is nothing to reconcile, and a lone
anomaly is a different subject.

**Sign of violation:** a specification or decision says "the sources measure
different quantities" and no recount-per-identifier number stands next to it.

## Trace

ArtVsMark/Claude-Code_Usage-Token — `src/claude_code_usage/transcripts.py`
(deduplication per response), `docs/spec.md`, issue
ArtVsMark/Claude-Code_Usage-Token#52; measurements of 2 and 3 September.

Related: [037](037-finding-status-depends-on-window.md) — a finding taken off
the wrong surface is a hypothesis; here the hypothesis is a conclusion taken
from **one** measurement. [170](170-green-on-a-forgery-is-a-hypothesis-too.md) —
there confidence is bought cheaply, here a refusal is bought expensively.
[174](174-facts-about-a-project-are-published-by-it.md) — the same collision of
two numbers from the other side: who is entitled to compute it.
