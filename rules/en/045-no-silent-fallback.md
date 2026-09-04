# There is no silent fallback — failure is loud

**Area.** reliability

**Tier.** 4 — code and tests

**The rule.** If the requested mode is unavailable, the work **fails with a
clear error** rather than continuing quietly in a weakened mode.

## The incident

Execution isolation is switched on by an explicit flag. The isolation mechanism
differs per operating system, and a given machine may not have it: not
installed, not supported, forbidden by policy.

The temptation was there: if isolation is missing, just run normally so that it
"works for everyone". That is precisely a silent fallback, and it was **rejected
by an explicit requirement**. The reason is simple: a user who asked for
isolation would get its absence and never learn of it. Running somebody else's
code without isolation when isolation was requested is worse than refusing to
run it.

The mechanism is selected **at construction** of the execution object, not at
first use: the error arrives before anything is executed.

## Why

A silent fallback swaps a **guarantee** for an **attempt** without saying so.
From then on the whole system is described with the word "usually": usually
isolated, usually verified, usually encrypted. Checking what actually happened
in a given run is no longer possible — no trace was left.

Second: a silent fallback breaks diagnosis. A failure at the moment of the
request points at its cause. A failure smeared across a weakened mode shows up
later, elsewhere, with a different symptom.

Third, less obviously: a silent fallback **preserves the gap**. While everything
"works", nobody installs or implements the missing mechanism.

## In practice

- fail **at construction**, not midway: before anything has been done;
- the message names what exactly is missing and how to obtain it, rather than
  saying "initialisation error";
- a fallback path is acceptable only when **explicitly requested** — by its own
  flag, with a note in the output that the mode is weakened;
- gaps left deliberately are named individually in the documentation, never
  implied.

## Where it applies

**Works** for anything requested for the sake of a guarantee: isolation,
encryption, signature verification, read-only mode.

**Does not work** for decoration: if terminal colour or an animation is
unavailable, failing is silly — that is presentation, not a guarantee.

**Sign of a breach:** the log has no line showing which mode a given run
actually used.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0007 § fail-fast and fail-loud;
`SECURITY.md` § `--sandbox`.