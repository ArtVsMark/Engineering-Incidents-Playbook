# Put the diagnostic trail where the one who fixes it can reach

**Area.** diagnostics, agent sessions

**The rule.** The trail of a failed run — the test name, the reason, the stack —
must live in a channel available to **whoever performs the fix**, not only to the
human at the console. The carrier is chosen by the reader's permissions: if they
have no access to logs and artifacts, a report inside an artifact is the same as
no report.

## The incident

A red matrix job left no trail at all: artifacts were uploaded only on success.
The fix looked obvious — always write a junit report and upload it with
`if: always()`.

The report appeared, and the question stayed unanswered. The one doing the fixing
worked from a cloud session, and job logs, run artifacts and the step summary all
live in a single permission scope that the proxy answers with **403**. The only
thing that reached them was the annotation `Process completed with exit code 1`.

The cause of three red jobs on one platform had to be found empirically: run the
whole suite locally, tuning conditions until the failure reproduced. The answer
came on the third run — the test turned out to be stricter than the gate
([150](150-a-test-asks-the-mechanism-not-its-condition.md)) — but it cost three
times more than one look at the report that had been sitting there the whole
time, out of reach.

A working carrier was found among the open channels: a comment on the change
itself. A separate step parses the reports and keeps one updated summary there —
job name, test name, first line of the error.

## Why

**Observability is a property of the pair "trail and reader", not of the trail.**
A report reachable only through permissions the reader lacks is not
observability. While the fixing was done by a human with full access, the
difference never showed: they opened the artifact and never noticed the channel
was privileged.

**The performer's permissions are part of the requirement.** An automated
performer works through an intermediary with reduced rights, and the reduction is
not accidental. So "where to put the trail" is settled not by where it is
convenient to write, but by where it can be read from.

**The workaround costs an order of magnitude.** Reproducing blind means full runs
instead of reading a line — and it is not always possible: the platform where it
fails may be unavailable entirely.

## In practice

- pick the channel by the **reader's permissions**, not the writer's
  convenience: can they reach the API they will read from;
- the summary needs a size limit and **one** place (an updated record, not a new
  one per run) — otherwise the channel stops being read;
- "no trail" and "an empty trail" get different wording: a red run with no failed
  tests means death before the test bodies, and that is its own answer;
- the privileged carrier stays: the full log goes nowhere, this is about the
  minimum that shows where to look;
- revisit once the performer gains the permissions: then the duplicate channel
  becomes noise.

## Where it applies

**Works** where the one fixing is not the one running: automated performers,
sandboxed sessions, outside contributors without access to internal logs,
pipeline bots.

**Does not work** where reader and runner are the same person with full access: a
duplicate channel costs attention and adds nothing. Nor for a trail that must not
appear in an open channel (secrets, personal data, internal addresses) — there
what goes out is a pointer, not the content.

**Sign of trouble:** the investigation of a red run starts with "let me try to
reproduce it", even though the report exists.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/report_failed_tests.py` and the
`report-failures` job in `.github/workflows/ci.yml`: the matrix junit reports are
parsed and the summary lives as one updated comment on the change itself.

Related: [142](142-a-scheduled-red-needs-an-addressee.md) — a scheduled red needs
an addressee; [139](139-a-mechanism-is-confirmed-by-a-run.md) — a mechanism is
confirmed by a run.
