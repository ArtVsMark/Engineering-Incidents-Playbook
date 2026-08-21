# A contract states the rules of its own evolution

**The rule.** Listing the fields is not enough. A contract must say **what in it
is stable, what is extensible and how new things are added** — otherwise every
change becomes a negotiation from scratch and the consumers diverge.

## The incident

The check result is delivered three ways: through the command line, through the
web shell, and through a future network interface. While there were no evolution
rules, every change of shape was argued afresh, and the three consumers diverged
the more they were edited.

The rules are recorded as five points, each closing its own class of argument:

1. **the names and meanings of the listed fields are stable** — renaming is
   breaking and is permitted only together with migrating every consumer and an
   entry in the changelog;
2. **extension is additive** — new fields are optional, and the consumer **must
   ignore unknown keys**;
3. **one branching point** — a new outcome is added to the enumeration rather than
   redefining the meaning of an existing one;
4. **knowledge of transport lives in the adapters** — the core returns data, not
   the format, codes or version;
5. **the contract is versioned**, not individual endpoints.

## Why

A contract without evolution rules describes **today** and lives for years. The
very first extension raises a question with no answer: may a field be added, must
an old consumer understand it, what to do with an unknown key. Everyone decides
differently, and the divergence comes not from carelessness but from the absence
of a rule.

The point about **ignoring the unknown** is the most underrated. It turns adding a
field from a breaking change into a safe one, and it does so **in advance**: a
consumer written today survives an extension tomorrow. Unwritten, it is not
observed, and the first new field breaks somebody else's parsing.

The point about **one branching point** protects against silent substitution: it
is tempting to broaden the meaning of an existing outcome instead of introducing a
new one — the old consumers keep working, but they start working **incorrectly**.
A new outcome they would at least fail to recognise explicitly.

## In practice

- the "how this changes" section lives in the contract itself, not in
  correspondence;
- stable fields say that changing them is breaking, and what that requires;
- the requirement to ignore the unknown is addressed to the consumer and verified
  by a test on their side;
- transport (serialisation, codes, version) is separated from data, or the
  contract version and the protocol version start getting confused;
- the static shape and the runtime shape may differ, and that is said plainly —
  otherwise the types are read as a promise.

## Where it applies

**Works** for exchange formats, public responses, event schemas, configuration
files.

**Does not work** for internal structures with a single consumer — there evolution
rules cost more than the freedom to change.

**Sign that it is needed:** the question "can we just add a field?" has been asked
a second time.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/result-contract.md` § stability
expectations. Related: [056](056-a-signal-states-what-it-does-not-mean.md),
[078](078-cancelled-is-not-an-error.md).
