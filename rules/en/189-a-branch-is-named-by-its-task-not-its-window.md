# A branch is named by its task, not its window, and lives exactly as long as the task

**Area.** process, agent sessions

**Tier.** 1 — rules and roles

**The rule.** A working branch carries the name of the TASK and closes with it.
A name taken from the executor — the window, the session, the machine —
outlives the task and thereby invites the next one into the same branch. Only
the PREFIX is machine-checkable: whether the slug names a task rather than a
window cannot be told apart by parsing, and that half stays discipline, stated
plainly.

**Portable beyond Claude Code.** yes — the subject exists wherever a branch is
opened by the executor rather than the task: long-lived developer branches,
build-machine branches.

## The incident

A profile showcase ran every window on a branch shaped `claude/<window
name>-<session tail>` — the name arrived from the executor's start-up
instruction. Three of the four neighbouring projects worked on
`agent/<task slug>`.

Measured: change #129 arrived with FIVE commits about five different subjects —
a facts contract for neighbours, answers about metrics, a foreign package on
PyPI, two gate fixes. The charter's caveat "file overlap beats topic" covered
this after the fact, though the overlap was a consequence, not a cause: the files
overlapped because the topics travelled together.

TRYING TO JUDGE THE SLUG FAILED TWICE, both times on the very first run of the
branch introducing the rule itself:

- banning the words `window` / `session` rejected a slug that was ABOUT the
  subject: `agent/branch-names-a-task-not-a-window` is legitimate;
- the pattern "a session tail is six to eight characters at the end" took the
  word `window` for a tail. Real tails look like `c1vnxz`, `beg7bm`, `dthzio` —
  the third has neither a digit nor any other trait distinguishing it from a
  word of the same length.

Both guesses were removed rather than patched: a gate you get around by renaming
a legitimate branch teaches people not to trust gates.

## Why

A branch is the technical boundary of a topic. As long as it is opened for a
task and closed with it, "one change, one topic" holds by construction: another
topic physically travels in another branch.

A branch named after the executor removes that boundary. It lives as long as the
window does — a week — and collects everything the window managed to do. After
that, the one-topic requirement rests on goodwill alone, and goodwill under the
pressure of a task is skipped exactly like any checklist step.

The asymmetry favours the restriction: a branch named by its task constrains
nobody — a window opens as many as it needs. A branch named by its window
forbids nothing and permits everything.

ON THE HALF THE MACHINE DOES NOT HOLD. The prefix is checked literally. The slug
is not: it may legitimately speak about the window, if the task is about the
window. Two measurements on a live tree showed that attempts to judge the slug
reject the legitimate, and that costs more than letting something through.

## In practice

- the branch name is built from the task: the prefix is fixed, the slug names
  the subject;
- the prefix is held by a gate, the slug by discipline, and this is written down
  plainly;
- the branch closes with the task; the next piece of work opens a new one;
- an executor's start-up instruction that assigns a branch by session name is
  something to change, not a given.

## Where it applies

**Works** where a branch is opened by the executor for a task and merging goes
through changes.

**Does not work** for long-lived branches by design — release branches, version
support branches: their name describes a line, not a task, and they outlive any
task on purpose. Nor does it apply where change and branch always coincide by
platform construction.

**Sign of violation:** the branch name carries an executor identifier, and the
change carries commits about different subjects.

## Trace

ArtVsMark/ArtVsMark — `scripts/check_branch.py`: the prefix is held by a gate,
the uncheckable half is named in the charter

ArtVsMark/Engineering-Incidents-Playbook — `.claude/hooks/push_guard.py` and
`.github/workflows/agent-pr.yml`: the `agent/` prefix acts as a switch — without
it no change is opened at all

Related: [132](132-one-change-carries-one-topic.md) — one topic per change; here
it is named what holds that topic technically;
[003](003-branch-name-is-a-switch.md) — a branch name is already a behaviour
switch, and that is the same prefix from the other side;
[006](006-window-lifetime.md) — a window lives three to five days, and a branch
named after a window lives just as long.
