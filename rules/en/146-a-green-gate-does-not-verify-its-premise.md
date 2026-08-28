# A green gate confirms itself, not the claim it was built around

**Area.** gates, audit

**The rule.** A gate with a two-sided suite that has survived mutation confirms
one thing: the mechanism behaves as declared. **It does not confirm that the
claim it was built for is true.** The claim is verified separately and against a
live subject — by measurement, not by reasoning. Otherwise a flawless mechanism
holds the wrong thing, and all the accumulated green reads as proof it is not.

## The incident

**The first.** A record claimed that on a squash merge the author is taken from
the branch's commits. A gate was written for that claim. The gate got a fixture
suite on both sides. The suite was checked by mutation: on a broken gate the
fixture goes red, on a repaired one it is green.

All of it worked. The claim was false. A measurement over six changes:

| changes | who opened them | author on the main branch |
|---|---|---|
| two | a human | a human |
| four | the agent app | the agent app |

On one of the four, the branch commits had been re-signed by the human
**deliberately**, as the repair. The merge author did not change. What decides is
the account that **opened** the change. The record was deleted as reopening what
had already been said.

**The second, the same day and on the same question.** A gate was being built to
ask the catalogue about a new record's neighbours. Similarity over the rule
statement suggested itself: that is the part which describes the subject. A
measurement on a live subject — the deleted record against the whole corpus —
overturned three designs in a row:

| design | what overturned it |
|---|---|
| similarity over the statement | the real neighbours fall to 6th and 13th; only full text catches them |
| a threshold for rejection | the live duplicate scores 0.243, a **legitimate** pair scores 0.296 |
| "cite your nearest neighbour" | 92 records out of 143 fail it — and the duplicate passed it |

Each of the three would have been implemented flawlessly, covered by a two-sided
suite, and green. Each would have held the wrong thing.

## Why

Verifying the mechanism and verifying the claim are **different subjects** that
look identical: both show a green run. Worse: the more thoroughly the mechanism
is checked, the more convincing the false sense that the claim was checked too. A
two-sided suite, mutations, a live run — all of it accrues to the mechanism and
touches its foundation by **not a single bit**.

Neighbouring rules cover other places:

- [044](044-check-the-premise-before-fixing.md) — about a **finding**: its premise
  is checked before planning. Here the premise is not forgotten but verified the
  wrong way: by a mechanism instead of a measurement;
- [055](055-your-own-expectations-are-a-hypothesis.md) — about a **baseline** in
  tests: an expectation written by your own hand proves nothing. Here the
  baseline is right and the gate checks it exactly; what is wrong is the reason
  the whole thing exists;
- [139](139-a-mechanism-is-confirmed-by-a-run.md) and
  [140](140-a-gate-is-tested-by-what-it-must-reject.md) — about exercising the
  mechanism. Following them is precisely what produces the green that is so easy
  to mistake for confirmation of the foundation.

## In practice

- the claim and the mechanism are verified by **different actions**: a measurement
  on a live subject versus a run against fixtures;
- the live subject usually already exists — past history, a deleted record, someone
  else's run; it rarely has to be invented, only remembered;
- the measurement is recorded next to the mechanism, not in a chat: whoever fixes
  the mechanism next must see what it stands on;
- a design overturned by measurement is recorded too
  ([026](026-rejected-findings-must-be-recorded.md)) — otherwise it returns, and
  it returns convincing.

## Where it applies

**Works** where a mechanism is built around a claim about how the world is: platform
behaviour, the shape of foreign data, the cause of a failure, a property of a metric.

**Does not work** where there is no claim — the mechanism expresses an agreement
rather than a fact. "A commit carries a trailer" is true because it was decided;
there is nothing to measure, and demanding one degenerates into ritual.

**Symptom of the violation:** the answer to "how do we know this is so" is a link
to a green run.

## Trace

ArtVsMark/claude-code-playbook#88