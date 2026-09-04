# A rule no machine can check is named explicitly

**Area.** process

**Tier.** 3 — gates and processes

**The rule.** If no mechanism exists for a rule, it is neither discarded nor
treated as obvious — it is written into its own section, marked as having no
gate and saying why.

## The incident

A review of one session left three breakages, none of which any automatic check
catches:

- **pushing into somebody else's branch** — the gate sees a matching branch
  name, not an intention;
- **code with escapes written through inline shell text** — a newline escape
  turned into a real newline twice, and the file broke before it ever ran;
- **"the test goes red without the fix", proved by reverting the whole source
  tree** — the tests failed on an import error, so all that was proved was "the
  test references the new code".

The temptation: if it cannot be checked, why write it down — "it is obvious
anyway". Each of those three breakages happened to people to whom it was obvious
anyway.

So they were gathered into a section with an honest heading: **what the gates
miss — and why this is written here**.

## Why

A rulebook containing only machine-checkable rules teaches the wrong thing: the
reader concludes that a green build equals compliance. Everything outside a gate
quietly becomes optional.

Second: "obvious anyway" is not a property of the rule but a property of somebody
who has already been burned. A new contributor and a new session have no such
experience, and they are the ones who break it most often.

Third: an explicit "no mechanism" note is **a request for a mechanism**. The
list of such rules shows where the next gate should be spent, and stops them
masquerading as checked.

## In practice

- the section is named plainly rather than dissolved among other advice;
- every rule carries **an incident**, not just a statement: without the story it
  becomes "obvious anyway" again;
- it says **why** a mechanism is impossible: the gate cannot see intent, the
  breakage appears only in a specific combination, the signal cannot be
  expressed;
- when a mechanism appears, the rule moves over to the checkable ones and the
  section shortens — a measurable sign of progress.

## Where it applies

**Works** for rules about intent, order of actions, and manner of proof.

**Does not work** as an excuse: "no mechanism is possible" is established by
trying, not by declaring.

**Sign of trouble:** the rulebook consists entirely of what the build already
checks.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § what the gates
miss. Related: [002](002-rule-without-mechanism.md) — the other side: a rule for
which a mechanism is possible must get one.