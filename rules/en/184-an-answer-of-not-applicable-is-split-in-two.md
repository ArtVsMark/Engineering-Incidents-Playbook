# An answer of "this rule does not apply to us" is split in two, like "no mechanism"

**Area.** catalogue, gates

**Tier.** 1 — rules and roles

**The rule.** Before writing down "not applicable", take the rule apart into its
letter and its generalisation. The letter is the subject named in the entry
verbatim; the generalisation is the failure mechanism the entry describes.
Answering "no" is allowed only when both are absent. If the letter is foreign
but the generalisation works for you, the rule applies — and the answer must
name what holds it.

**Portable beyond Claude Code.** yes — the subject belongs to any body of rules
adopted in part: an external standard, an industry checklist, another team's
handbook.

## The incident

7 September 2026, a measurement across the whole catalogue tree: **48 scripts
declare which rules they hold — 313 declarations. Seven** of them point at rules
whose catalogue answer is "not applicable" or "rejected". Both statements cannot
be true: a mechanism cannot hold what we say we lack.

Working through all seven gave one shape — the answer looked at the letter and
missed the generalisation the mechanism was already using:

| rule | letter — true | generalisation — working |
|---|---|---|
| 037 | a gate has no severity scale | a result off the wrong surface is not proof; cost a shift twice |
| 050 | there were no budgeted limiters | a share of the hourly quota appeared three days earlier |
| 116 | there are no parallel workers | there is a collector: 181 files → one index |
| 137 | no watchdog on an external source | raw versus derived — in three gates at once |
| 085 | we built no requests to a model | we built one the same day, and the answer went stale within hours |

The first measurement returned five cases instead of seven: the regex stopped at
the first continued line, and the explanations are multi-line. The understated
measurement looked exactly as plausible — that is part of the incident, not a
footnote to it.

## Why

"Not applicable" is the only answer that closes a question FOREVER while
requiring nothing to be built. It has no deadline, no subject to verify and no
moment at which it is re-read: the rule leaves the queue and leaves sight.

The asymmetry is the one from 182, mirrored. There, people underestimate what a
machine can do; here, what the rule says. An error one way leaves an extra
mechanism holding nothing — visible and fixable. An error the other way strikes
out the rule, and then the failure arrives.

The generalisation is usually the value of the entry: the letter describes the
case it grew from, and that case is almost always someone else's. Answering the
letter answers something you never intended to apply.

## Practical boundaries

- an answer of "not applicable" names both halves: which letter is foreign, and
  why there is no subject for the generalisation either;
- a mechanism declaring that it holds the rule outweighs the answer: if one
  exists, "not applicable" is refuted by fact, and it is the fact you must argue
  with;
- answers are revisited when the tree changes, not on a calendar: 085 became
  applicable within an hour, because a review workflow was introduced;
- if the generalisation works but no mechanism exists, that is "applies, held by
  nothing" or deferred with a named event — never "not applicable".

## Where it applies

**Works** where a body of rules is adopted in part and an answer is recorded per
rule: the catalogue and its consumers, an external standard with a conformance
map.

**Does not work** for rules with no generalisation at all — narrowly factual
ones: "language X has this syntax trap". There the letter is the whole content,
and splitting it in two yields an empty second half.

**Sign of violation:** an answer says "not applicable" while a mechanism in the
same tree names that rule as its own.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#355

Related: 182 (the same split in two, for the answer "no machine can check
this"), 177 (unfinished rule work comes first — "not applicable" removes a rule
from that queue for free), 146 (green confirms itself).
