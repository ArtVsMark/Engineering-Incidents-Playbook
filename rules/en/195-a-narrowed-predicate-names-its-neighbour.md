# A repair names the neighbouring cases, or it fixes one and breaks another

**Area.** code, quality

**Tier.** 4 — code and tests

**The rule.** A repair made for a named case must name the NEIGHBOURING cases —
the ones decided by the same predicate — and answer for each: did it work
before, and does it work now. "There are no neighbours" is a legitimate answer,
but it is said out loud, not assumed. A neighbour that was already broken is
still a neighbour: the repair either closes it or names it.

**Portable beyond Claude Code.** yes — the subject exists for any edit to a
condition, a regular expression, a set of flags or a branch: they all decide
more than one case, and they are repaired one case at a time.

## The incident

On 8 September 2026 an outside reading of this catalogue produced **ten distinct
findings** (counted by fingerprint), all of them correct. Four were "the claim is
wider than the code" — that is 183 and 044. **Three turned out to be one class**,
and that class was written down nowhere.

**The first.** Review-finding extraction strips markup from the headline that the
fingerprint is computed over. The repair in `#413` named its case — bold
`**FINDING: …**` — and stripped the frame with `.strip("*_")`. A neighbour broke:
`**kwargs` and `id_` lost meaningful characters from their edges. The previous
code had not touched them at all, and the damage is irreversible — a different
fingerprint means a dismissed finding comes back as a new one.

**The second repair broke a third neighbour.** `#415` replaced the strip with a
paired unwrap: since `*` was now needed by the pair, it was taken out of the
prefix class. The named case became correct again. The list marker
`* FINDING: …` stopped parsing altogether, and `* **FINDING: …**` yielded
`**FINDING: …*` with a dangling character — precisely the corruption the repair
had been written to remove. The reviewer named the regression outright: "the
prefix used to include `*` and strip the bullet whole".

**The third was not broken by a repair — it stayed broken.** The rule shares in
`facts.json` did not add up to the whole because the `rejected` status was not
counted. The repair added `rejected`. The `unreviewed` status would diverge the
same way at the first unreviewed rule, and nobody asked about it.

The suite was green all three times, the required checks passed, and the
neighbour was found neither by the author nor by a gate.

**What was tried first.** Both times: name the case more precisely — first "bold
is unwrapped as a pair, not shaved off the edges", then "an asterisk stays a
bullet if a space follows it". Both statements are true and neither helped: they
sharpen the NAMED case, and what is lost is always the unnamed one. Only the
third approach worked — enumerate the forms the predicate decides, and close each
with a case.

## Why

The suite is written from the named case, because the case is named by the
repair. A two-sided suite
([140](140-a-gate-is-tested-by-what-it-must-reject.md)) demands that a gate
reject what it must **and** accept what it must — but what it must accept is
enumerated by the author, and the neighbour misses that list for exactly the
reason it missed the repair: nobody asked. The predicate changes, and a list of
what that predicate used to decide appears nowhere.

Hence the shape of the rule: the question is not "is the repair correct" but
"what else does this predicate decide". Authors ask themselves the first question
and answer yes; the second is not asked at all unless something outside requires
it.

**The asymmetry of cost is the same as in
[193](193-repair-acceptance-stronger-than-defect.md).** A repair that does not
work comes back from the suite within the hour. A repair that works and drops a
neighbour passes everything: the gates are green, the review is busy with the
named case, and the broken neighbour surfaces when the link to this edit can no
longer be reconstructed. The incident shows it literally — a lost finding
disappears in silence, and there is nowhere to learn of the loss.

## In practice

- before the repair, name the PREDICATE being changed and enumerate what else it
  decided: markup forms, status values, command flags, branches of a condition;
- add one case per named neighbour, including the ones that "stayed the same" —
  a case about what did not break is not redundant here, it is the check;
- "no neighbours" is written down in words: unwritten is indistinguishable from
  unasked ([026](026-rejected-findings-must-be-recorded.md));
- a neighbour broken BEFORE the repair is either closed by it or filed as a task;
  "it did not work anyway" is not an answer.

## Where it applies

**Works** where an edit changes a predicate that decides more than one case: a
condition, a regular expression, a set of flags, a branch on status, a list of
exemptions.

**Does not work** where the place being repaired decides exactly one case and
that is verifiable — a constant, a misspelled name, a one-off substitution. It
also does not work for a new mechanism: it has no previous behaviour, therefore
no neighbour to drop — the subject there is different and 140 holds it.

**Sign of violation:** the cases added by a repair name only what its own
headline names; an outside reading finds a form the previous code handled.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#418

See also: [140](140-a-gate-is-tested-by-what-it-must-reject.md) — a two-sided
suite answers HOW to check; this one answers what enters the check at all, and
the list is drawn up before it;
[146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate does not
verify its premise, and a repair's premise is that it has only one case;
[193](193-repair-acceptance-stronger-than-defect.md) — acceptance stricter than
the defect: strictness over one case there, coverage over many here;
[044](044-check-the-premise-before-fixing.md) — the premise is checked before the
repair, and "this predicate decides only this" is that premise.
