# An agent window finishes its own open work before opening new

**Area.** process, agent sessions

**Tier.** 3 — gates and processes

**The rule.** An agent window does not open a new change when it already has
as many open as the set limit allows: its own open work — findings, a
conflict, red — is brought home before new work. The limit is held by a
mechanism before the push, not by the window's memory: the number open is the
platform's answer, not a guess. A push to the branch of an already open change
does not add to the limit — that is repairing one's own.

**Portable beyond Claude Code.** partly — a limit is needed by any executor
that opens changes faster than the queue merges them; identifying the window
by the `Claude-Session` trailer is agent-window mechanics.

## The incident

The mechanisms project, an agent window with auto-merge and an outside review.
On 03.10.2026 the window opened **17** changes, **10** were merged; from
**10:40 to 16:10 UTC** — not a single merge. The review's first pass found
findings in **11 of 12** changes, the queue rightfully waited for them to be
fixed, and meanwhile the window kept opening new ones: each new change is a
full ci and a paid review, while findings on the old ones piled up.

A measurement over the platform's whole history on 04.10.2026
(`scripts/check_open_limit.py --measure`, the window — by the `Claude-Session`
trailer in the squash body): of **908** changes the window is known for
**880**, and **97** of them were opened when the same window already had three
or more open.

The order of work sources
([091](091-work-sources-are-ordered-first-non-empty-wins.md)) said "your own
before the new", but it was held by reading, and reading lost. The owner's
decision of 03.10.2026 (ArtVsMark/Engineering-Pipeline-Mechanisms#1085): the
limit is three open changes per window, held by a gate before the push
(`preflight.py --push`).

## Why

**An order without a mechanism loses to new work.** The window sees the next
line of the plan in front of it, not the queue of its own changes: findings on
the old ones wait until it remembers them. The rule "your own before the new"
was written down and still broken — 97 times in one project's history.

**Every new change gets more expensive while the old ones stand.** A new
change is a full ci and a paid review, while merging does not advance: the
queue rightfully waits for the findings on the old ones to be fixed. Spending
grows, the result does not.

## In practice

- the limit is named as a number and held by a gate before the push; the
  number open is taken from the platform's answer;
- a push to the branch of an already open change does not add to the limit —
  that is repairing one's own;
- the gate does not catch: a push bypassing preflight; "there are unresolved
  findings on one's own" — the platform does not return their number in one
  answer; a run without a platform token and in a shallow clone — the limit is
  called unchecked there, and the push goes through; a branch whose commits do
  not carry the `Claude-Session` trailer — its window is unknown, and the limit
  does not apply to it.

## Where it applies

**Works** in a project where an agent window opens changes itself and a queue
with checks and an outside review merges them.

**Does not work** where the window cannot ask the platform for the number open
(no token, a shallow clone) or is not identified by its commits: the limit is
unchecked there. Nor for unresolved findings on one's own changes — the gate
before the push does not see their number.

**Sign of a violation:** a window opens a new change when it already has as
many open as the limit allows, and there are no merges over the same time.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Engineering-Pipeline-Mechanisms#1085 — `scripts/check_open_limit.py`.

See also: [091](091-work-sources-are-ordered-first-non-empty-wins.md) — the
order of work sources; here the same order "your own before the new" gets a
numeric limit and a mechanism. [177](177-unfinished-rule-work-comes-first.md) —
unfinished rule work comes before new; there the subject is the project's debt
to the catalogue, here — one window's open changes.
[031](031-waves-not-salvos.md) — waves of parallel executors; that is about
launching, this is about unfinished work.
