# A language version move is done when the code is written for it and everything runs on it, not when the tests pass

**Area.** migrations, code, gates

**Tier.** 3 — gates and processes

**The rule.** A move to a new language version is closed by two proofs, not by
a green suite: the code is written in that version's style — held by a gate
that derives its requirements from the `requires-python` floor — and
everything that executes the code executes it with the floor's interpreter.
"The suite passed on the new version with no changes" is not the result of the
move but its starting point: a formal move looks exactly the same.

**Portable beyond Claude Code.** partly — the style and pipeline links exist
in any Python project with CI; the window link (hooks running in the process
environment rather than in the commands' PATH) is a property of the agent
platform.

## The incident

**The move to 3.14.7 was announced three times before it happened**
(ArtVsMark/Engineering-Incidents-Playbook#670, #671, #672). Three links of one
formal move, all measured on 2 October:

- **Style.** Release v1.5.0 recorded "no code changed, the suite passed on
  3.14.7 untouched" as a success. Measured: `from __future__ import
  annotations` in 132 files out of 132, `except (A, B):` without `as` in 21
  places, ruff `UP` rules targeting `py314` — 5 findings. The code was
  declared for 3.14 and written in the style of the previous 3.12
  floor.
- **The window's `python3`.** `/usr/local/bin/python3 → /usr/bin/python3.11`
  while `python3.14` was already installed next to it. Platform hooks run in
  the window process's environment, which the PATH from `CLAUDE_ENV_FILE`
  never reaches. The `push_guard.py` rewritten in 3.14 style hit a
  `SyntaxError` on 3.11 and exited with 1, and the platform treats any
  non-zero code other than 2 as non-blocking: **the push guard was silently
  off**. Reproduced in the window.
- **The pipeline.** `agent-pr.yml:open`, `automerge.yml:arm` and
  `task-state.yml:check` called `python3` without `setup-python` — the
  runner's system python. The version gate did not see them: those jobs carry
  no version number, so there was nothing to compare.

**What did not work first.** "Tests are green, so we moved": the suite checks
that old code works on the new version, not that it is written for it. "Keep
the bootstrap files on 3.11" — the same formal move hidden in an exception.
"Write `py314` into the linter config" — it freezes at the next floor bump
([005](005-hand-written-numbers-rot.md)). Three links were closed in #670–#672: the
`scripts/check_py_style.py` gate derives its target from `requires-python`;
`check_python_version.py` flags a job that calls python before `setup-python`;
the start hook reads the floor without Python and switches the window's
`python3`; the push guard is invoked with the floor's interpreter and, without
it, blocks `git push` with code 2. The move becomes complete only together with
the next window's leftovers: a search for any other execution that names no
version and a check of the window at start.

**Speed before and after** — taken on 2 October in a fresh window after the
restart, one machine, three interleaved rounds, medians. The suite is only the
1447 tests that existed BEFORE the move: the 84 new ones are left out, or the
measurement would track the suite's growth rather than the version. Code before
the formal floor bump (`19d10f6`) on 3.12 — 28.2 s, the same code on 3.14.7 —
29.6 s, code after #672 on 3.14.7 — 29.6 s; the spread within one
configuration (26.5–33.1 s) is wider than the gap between them. Importing
`scripts/*`: 0.233 → 0.208 → 0.243 s with the same overlap. Neither the
interpreter nor the rewritten code gave the suite any speed. The measurement's limit
is a small codebase that mostly waits on processes and files; a project that
computes inside the interpreter may respond differently, and that is checked by
its own measurement, not carried over from here.

**The gain of the move is in pipeline width, not interpreter speed.** The
catalogue's pipeline ran a single version before the move as well, so there
was nothing to drop. The grader's matrix on 2 October is 3 OSes × (3.12,
3.13, 3.14) plus 3 OSes × prerelease 3.15, 12 jobs per run; a full move to a
3.14 floor leaves 3 OSes × (3.14, 3.15), 6 jobs — half as many on every
change, while the versions the project actually runs on are still checked.
This is arithmetic on the tree, not a measurement: measuring run duration
before and after is an item in the grader's issue. A dropped version costs the
pipeline as many jobs as there are OSes, not one, so a multi-OS project
recoups the move faster than the catalogue does.

**Second incident: the number was there, but the gate did not read it**
(#678). A sweep for "any old calls left" after the three links found a
fourth. The root `action.yml` — the composite action for CONSUMERS — set up
Python 3.12: the floor bump (#647, 1 October 13:49 UTC) moved the actions in
`.github/actions/` to 3.14 and missed the root one. The version gate read only
`.github/workflows/` and saw none of the actions, although they carry the
number. After the style move (#670, 2 October 10:31 UTC)
`scripts/sync_inbox.py` on 3.12 is a `SyntaxError` with exit code 1, and the
action treats only code 2 as red: the consumer's rule sync would have gone
silently off, by the same mechanism as the push guard. Impact — zero: the
released v1.6.0 does not carry the style move and imports on 3.12, and
consumers pin tags. The check is one command: `d=$(mktemp -d); git archive
v1.6.0 scripts | tar -x -C "$d"; PYTHONPATH="$d/scripts" python3.12 -c
'import sync_inbox'` — no error on v1.6.0, `SyntaxError` on `main` before
#678. The window of breakage was `main` from 10:31 to 12:11
UTC, and the very next release would have shipped it to everyone. The review
of the fix (#678) found two more holes of the same kind in the new parsing: the
setup step was searched for as a word in text including comments, and a
`setup-python` step without a number passed silently; both were closed by
#680. The review of #680 found a third, the opposite one: a number in single
quotes was not parsed, and a correct step became a "no number" finding —
closed by #684. So the search criterion
is not "a job without `setup-python`" but **every file that executes code —
job and composite action — and a setup step that names its version as a
number**.

## Why

**A green suite on the new version is common to both outcomes.** A new
language version rarely breaks old code: rewritten and untouched code both
pass on it. So the suite cannot tell "we moved" from "we put a new interpreter
under old code", and the first sign that suggests itself is exactly the one
that cannot tell them apart.

**The declared version and the executing one are different numbers, and the
second is not in the tree.** `requires-python` and the pipeline matrix name
the version out loud. A window hook, a job without `setup-python` and the
system `python3` take the interpreter from the environment and carry no number
— the gate has nothing to compare them with. They keep running the code on the
old version until the code starts using the new one. Then they fail, and the
failure does not look like a refusal.

**The cost is asymmetric.** An extra style-gate run costs seconds. A formal
move cost a guard switched off without a single red signal: an interpreter
error on a non-blocking exit code reads to the platform as "check passed".
That is why a guard without the floor's interpreter must block, not let
through.

## In practice

- measure speed before and after the move on one machine, in interleaved
  rounds, on the suite that existed BEFORE the move; name the gain as a number
  or record that there is none;
- count the pipeline matrix width before and after separately: a dropped
  version removes as many jobs as the matrix has OSes, and this gain does not
  show up in a suite speed measurement;
- the style gate takes its target from `requires-python`, not from a written
  string: at the next bump it demands the new style without a config change;
- search for everything that does NOT run on the floor's interpreter: window
  hooks, pipeline jobs without `setup-python`, the system `python3`, scripts
  with `#!/usr/bin/env python3`. The search criterion is a missing version
  number, not a mismatched one;
- a guard that needs the floor's interpreter blocks the guarded action when
  it is absent (code 2) instead of silently allowing it;
- the linter version is pinned: an unpinned one changes the style rule set
  without a change to the tree;
- windows are restarted after the merge: hooks and the rulebook are read at
  start ([047](047-rule-change-restarts-the-windows.md)), and a live window
  keeps running the code on the old interpreter.

## Where it applies

**Works** for raising the floor of the language or runtime version inside a
project that decides for itself what its code runs on: its own CI, its own
hooks, its own window.

**Does not work** for a contract handed outside: the consumer of a template or
action has an environment of their own, and raising the floor there is a
change to someone else's contract under
[157](157-a-contract-version-bump-is-a-re-read.md), not a move. Does not work
for a bump where the new version breaks old code: the suite turns red on its
own, and the move cannot stay formal. Does not work for dependencies rather
than the language: a gate driven by `requires-python` cannot derive a
library's style.

**Sign of a violation:** the move is closed with "the suite passed without
changes", while the tree has execution that names no version — a job without
`setup-python`, a hook calling bare `python3` — or the code style has not
shifted in a single file.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#670

ArtVsMark/Engineering-Incidents-Playbook#672

ArtVsMark/Engineering-Incidents-Playbook#678

See also: [157](157-a-contract-version-bump-is-a-re-read.md) — a version bump
of SOMEONE ELSE's contract; here the floor is our own, and there are no
answers to re-read; [044](044-check-the-premise-before-fixing.md) — "no code
changed" was a premise nobody measured; [005](005-hand-written-numbers-rot.md)
— why the linter target is derived, not written in;
[037](037-finding-status-depends-on-window.md) — green taken on the wrong
interpreter stays a hypothesis; [047](047-rule-change-restarts-the-windows.md)
— why windows are restarted after the merge. Issue
ArtVsMark/Engineering-Incidents-Playbook#351 — the speed measurement above
confirms its "newer does not mean faster" part.
