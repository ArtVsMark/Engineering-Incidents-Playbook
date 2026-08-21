# An agent session lives three to five days

**Area.** agent sessions

**The rule.** A long-lived session grows expensive and preserves obsolete rules.
Past that span, restart it and hand over the baton.

## The incident

A measurement across the live sessions of one project:

| Session | Days | Cache reads per output token | Cost |
|---|---:|---:|---:|
| oldest | 7 | **764** | $392 |
| middle | 4 | 650 | $106 |
| freshly created | 1 | **81** | $6 |

**One week-old session consumed more than the other five combined** — $392
against $335.

The same session was the source of a second problem: it was burning the GitHub
API quota by calling over the expensive transport. The cause turned out to be a
matter of dates: the session had started on the 13th, while the cheap-transport
tool reached full coverage on the 19th. The session was working to instructions
that were current **at the moment it launched**.

The project's updated rules never reached it: context is read once, at startup.

## Why

Every turn re-reads the whole accumulated context, so **the price of the same
result grows with the age of the session**. Context only accumulates; it does
not shrink on its own.

The second effect is subtler and more dangerous: **editing documentation after
the fact does not affect sessions already running**. A long-lived session lives
by the rules of the era it was born into, and nothing about that is visible
from outside.

## How to hand over

The opening message of a new session: how we work → where we stopped → decisions
that are not being reopened → links to the tasks.

**Context is handed over as links, not as retelling.** Retelling the details in
the opening message means carrying the problem across with the baton: the new
session starts with a bloated context immediately.

## Where it applies

**Works** for any long-lived agent session that accumulates context.

**Does not work** where context does not grow: one-shot tasks, sessions with
forced compaction.

**Caveat:** age is not the only factor. A session working on code reads more
than a session spent discussing. But context never shrinks by itself, so an old
session becomes expensive inevitably.

## Trace

ArtVsMark/Stepik-Python-Grader#1283. For the event-driven reason to restart,
unrelated to age, see [047](047-rule-change-restarts-the-windows.md).
