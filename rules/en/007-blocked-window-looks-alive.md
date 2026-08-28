# A session stalled on a permission prompt looks exactly like a working one

**Area.** agent sessions

**The rule.** Before deciding that work has been abandoned, check the session
registry: the session may be waiting for permission, and then it needs a person,
not a repair.

## The incident

A session had carried a task to completion — implementation done, the full
suite passing (5043 passed, 98 skipped, 12 new tests) — and stopped at:

```
Waiting on permission: mcp__github__create_pull_request
Approve or deny mcp__github__create_pull_request
```

It stood there for **forty minutes**. It was found by chance, during a manual
walk of the session registry.

From outside everything looked fine: the session was listed as live, the branch
existed. Only the pull request was missing — and with it any build, and any
place in the queue.

## Why

Session state lives **outside the repository**. Neither the branch, nor the pull
request, nor the build knows anything about it, so no workflow can catch this by
construction.

Worse, a stalled session and abandoned work present **the same external
picture**, while the correct responses are opposite:

| Signal | Waiting for permission | Work abandoned |
|---|---|---|
| Session in the registry | present, waiting | no live session on this branch |
| Branch | unchanged | unchanged |
| Pull request | often not opened yet | open, stalled |
| **What to do** | **grant permission** | **repair** |

Getting the diagnosis wrong is expensive: an automatic repairer sent into a live
branch will trample somebody's work.

## Where it applies

**Works** anywhere an agent can ask for confirmation and stop.

**Does not work** in modes without permission prompts — there a stall means
something else.

**An honest limitation:** while the walk is done by a person or a coordinating
session, that is a single point of failure. If the watcher dies, nobody notices
the stalled sessions. An external notification would close the hole, but it
requires machinery outside the repository.

## Trace

ArtVsMark/Stepik-Python-Grader#1323, ArtVsMark/Stepik-Python-Grader#1321