# Green on a forgery is a hypothesis too, and a forgery needs a source

**Area.** tests, quality

**Tier.** 4 — code and tests

**The rule.** [037](037-finding-status-depends-on-window.md) says: a defect found
on a forgery is a hypothesis until confirmed on the real surface. The converse
holds just as firmly: **green** on a forgery is a hypothesis too. A suite run
against values the author invented proves the code agrees with the author's own
idea of the other side, and says nothing about that side. Hence the practical
requirement: a forgery of someone else's interface must have a **source** — a
captured response from the real side, not an invented one; a forgery's drift from
it is discovered only once it has been checked against it.

**Portable beyond Claude Code.** yes — the subject belongs to any suite with
forgeries of external interfaces: an HTTP client, a CLI wrapper, a database
driver.

## The incident

The catalogue ships consumers an "inbox" mechanism: it looks for its own task in
the tracker and creates it if it finds none. At one consumer the mechanism failed
**four runs in a row** from 29 August to 1 September — all red, and the task
never appeared.

The cause: the lookup used an expression of the form
`[…][0] | "\(.number) \(.state)"`, and indexing an empty set prints a **word** —
`null null`. The string "null" is non-empty, therefore truthy: the "create the
task" branch never ran, and instead an edit call went out for a task numbered
`null`.

The tests did not see this, because when no task existed the forgery returned an
**empty string** — a value the platform never returns. Four "no task" tests were
green for two weeks over a broken mechanism.

The fix in the script is one operator. The fix this record exists for is in the
forgery: it now returns `null null`, and the old parsing goes red on it. Verified
by mutation: both go red only against the corrected forgery.

## Why

A forgery is a **model** of the other side, and a test over it checks that the
code agrees with the model. An error in the model itself is invisible from inside
the suite by construction: code and test proceed from one and the same wrong
idea, so the more thorough the suite, the more confidently it confirms the error.

The asymmetry here is the reverse of the usual one. A false red on a forgery is
cheap: someone investigates and finds either a defect or an inaccuracy in the
model. A false **green** costs two weeks of silence and four red runs at a
neighbour's — that is, the failure surfaces on the live side and through someone
else's eyes.

Hence the only remedy available from inside: the model must have a source. Not
"I think the platform returns empty", but a captured response kept with the
suite. That does not make the model correct forever — the other side changes
([157](157-a-contract-version-bump-is-a-re-read.md)) — but it makes it
**checkable**.

## In practice

- the real side's response is captured and kept next to the forgery as a sample;
- the forgery returns what the platform returns, awkward shapes such as
  `null null` included;
- mutation: the test must go red against the corrected forgery — otherwise it is
  checking something else;
- when the other side's version changes, the sample is recaptured rather than
  edited from memory;
- a live run of the mechanism
  ([139](139-a-mechanism-is-confirmed-by-a-run.md)) neither replaces the forgery
  nor is replaced by it: they are two different checks.

## Where it applies

**Works** for forgeries of **external** interfaces: a platform, a payment
gateway, an outside command.

**Does not work** for forgeries of your own interface: the source lives in the
same tree, an ordinary test catches the drift, and demanding a sample becomes
ceremony. Nor does it work where a live response cannot be captured — a closed
platform, a paid call; the honest answer there is to mark the forgery as
unverified rather than pretend a source exists.

**Sign of violation:** the suite contains a forgery of an external interface and
not a single captured response from that side.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#250 — scripts/sync_inbox.py and
tests/test_sync_inbox.py

Related: [037](037-finding-status-depends-on-window.md) — a finding on a forgery
is a hypothesis; 170 is its other half, about green.
[146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate confirms
itself; the same holds here for a test suite.
[145](145-every-declared-outcome-is-run.md) — every declared outcome is run.
[157](157-a-contract-version-bump-is-a-re-read.md) — a contract version bump
means re-reading the answers, not just the format.
