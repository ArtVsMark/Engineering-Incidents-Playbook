# Derive state from live artefacts, not from a register kept by hand

**Area.** pipeline, process

**The rule.** Who took what, what is queued, what is ready — all of it is
**computed** from things that already exist (branches, tasks, API responses),
not stored in a separate file somebody has to remember to update.

## The incident

Two lines of work ran from two sessions, and they could not see each other. The
cost was measured: within one session a task was picked up twice when part of it
had already been done next door and was waiting to merge, while shared files
diverged into conflicts noticed only at merge time.

The obvious answer is a "who took what" file. It was rejected, for two reasons
at once.

**First:** such a file would have to live in the repository — meaning it would
itself become the source of exactly the conflicts it was created to prevent. Two
sessions editing a register conflict over the register.

**Second:** it would require staleness rules that nobody is left to apply. The
session closed; the entry remained. Nobody knows whether it is alive or dead.

Instead of a register, computation: live branches on the shared server answer
both questions more precisely. A task does not exist without a branch, and a
diff between branches gives not "what somebody wrote in the register" but the
actual list of files. There is nothing to clear: the branch merged and the
overlap disappeared by itself.

The same technique applies to the merge queue: the queue is stored neither in
labels nor on a board but printed from API state — who is at the head, who has
waited how long, who overlaps with whom.

## Why

Stored state has a life of its own: it has to be created, updated and cleaned,
and each of those three is skipped exactly when you are busy. In multi-session
work that is not an exception but the norm — a session closes abruptly.

Computed state **cannot go stale**: it is the current fact, not a story about
it. The question of trust disappears too — not "is the register truthful" but
"what is actually there".

The price is honest: computation costs requests and works only where artefacts
genuinely reflect the work. A branch never pushed is invisible — but that is a
different rule, about making work visible.

## In practice

- do not create a register if the answer follows from artefacts that are created
  anyway;
- the computation is a command with tests, not a note in the documentation;
- the answer includes **time**: who has waited how long, what has not moved —
  otherwise computed state answers "what exists" but not "what is stuck";
- whatever the artefacts cannot express (for instance "this change fixes a red
  build") is stated on a separate line and left to a human: lying by computation
  is worse than admitting a gap.

## Where it applies

**Works** when work leaves a mandatory trace: a branch, a task, an API record.

**Does not work** for intentions: "I am about to take this on" leaves no trace —
there you need either a register or an early draft as a way of turning the
intention into an artefact.

**Sign of trouble:** there is a file listing who is doing what, and its last edit
is a week old.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § two lines of work (§ why
there is no register file); `CLAUDE.md` § merge queue ("computed, not stored").
