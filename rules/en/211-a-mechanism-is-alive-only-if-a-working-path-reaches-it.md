# A mechanism is alive while a working path reaches it, and a green suite does not prove that

**Area.** code, tests

**Tier.** 4 — code and tests

**The rule.** A mechanism counts as working when a **working path** reaches it:
an entry point the platform or a person executes — a workflow, a hook, a
command from the rulebook — and on to whoever reads the verdict. A green suite
does not prove this: it calls the mechanism directly and stays green when the
working path to the mechanism has broken. The predicate "declared in working
code and not reached by working code" names its legitimate neighbours: closed
rosters kept for the suite and limits addressed to a human are, by
construction, not reached by a working path.

**Portable beyond Claude Code.** yes — the subject exists in any code with a
test suite: a function called only by its own test looks sound in any project.

## The incident

**THE NEIGHBOUR'S MEASUREMENT, WHICH THE PROPOSAL CAME FROM** (the mechanisms
project, 21–22.09.2026): six cases in two days. Reading found none of them, and
neither did a green suite.

1. #607 — a constant listing service steps was declared with a docstring and a
   measurement and called from nowhere. The distinction "did our step fail or
   the platform's", which the whole report existed for, never happened.
2. #611 — the fix for the first case added a count across the whole series and
   called it neither from the report nor from the pass. The number was computed
   and never reached a reader.
3. #616 — a warning about a silenced outside review was called from the push
   path and stayed silent on an ordinary preflight pass.
4. #618 — the acceptance test for the second case called the warning directly
   and stayed green when the call from the pass was removed.
5. and 6. A measurement over the whole tree: the predicate gave seven names in
   66 modules. Five were legitimate neighbours: closed rosters for the suite
   and a limit addressed to a human. Two were real orphans, and both were
   orphaned **by a neighbour being built** that did the same and more. Both
   were covered by the suite, and neither ever turned red.

**HERE THE SAME MEASUREMENT GAVE TWELVE NAMES IN 62 MODULES** (25.09; working
code is `scripts/` and `.claude/hooks/`, a name counts as read by parsing
imports and references, not by a textual match):

- **two real orphans, both left by a neighbour being built.**
  `sync_inbox.contract_gap` was added on 04.09 (#329) to check the answer's
  contract number. On 10.09 (#462) `contract_gaps` arrived, checking every
  number, and since then no working path calls the first one; four assertions
  in the suite do. `sync_labels.NO_GH` was left behind on 27.08 (#149), when
  the `gh` call moved into a shared module; a single check in the suite, which
  compares its value, is all that calls it;
- **seven dead constants.** Five paths in `new_rule.py` have been dead since
  birth (#153): in that same edit the code started computing paths from
  `--root`, and a comment there explains why the constants will not do. Two are
  `ROOT` in `check_task_state.py` and `review_findings.py`;
- **a knob that turns nothing** — `consumers_picture.NAME_LINES = 2`. Two lines
  per name are set by the structure of `wrap_name`, not by the constant. Set it
  to 3 and nothing changes;
- **legitimate neighbours** — `check_prose.БЕЗ_ПОТОЛКА`, a named boundary with
  the explicit note "a named boundary, not a mechanism", and
  `sync_inbox.ЧУЖОМУ_НЕ_НУЖНЫ`, a closed roster whose completeness the suite
  holds.

The first measurement, by a textual name match, gave six. Same-named constants
in neighbouring modules — `ROOT`, `BINDINGS`, `NO_GH` — counted as calls, and
half the orphans hid behind someone else's name. The measurement is still one
level deep: a name called only by an orphan does not show up in it. Twelve is
a lower bound, not a count.

## Why

**The break is not in the mechanism but between it and its caller.** Reading
the diff sees sound code, the suite confirms it, the gates are green. Nothing
can turn red: what is broken is not code but a missing call, and an absence
appears in no diff.

**The suite makes it worse, not better.** An orphan with a green run looks
healthier than a live mechanism without one: it has a check, and the eye
slides past. For fifteen days `contract_gap` carried four green assertions
about code that never ran. And the coverage measurement the catalogue takes
from the suite (`source = ["scripts"]`) counts every one of its lines as
covered: coverage measures whether the suite reached a line, not whether a
working path did.

**An orphan is most often born of a neighbour.** A new mechanism does the same
and more, the call moves to it, and the old one stays behind together with its
suite. The edit that orphaned it does not touch its lines, so it is not in that
edit's diff.

**This is not [145](145-every-declared-outcome-is-run.md).** 145 requires
running every declared outcome of a mechanism. Here every outcome can be run by
name and the defect survives: no working path reaches the mechanism.

**This is not [139](139-a-mechanism-is-confirmed-by-a-run.md).** 139 requires
confirming a mechanism by a run on a live subject and explicitly does not apply
to pure functions. Here the subject is exactly pure functions and constants:
their run in the suite is sound, and there is no working call.

## In practice

- a **working path** is what runs without the suite: a platform workflow, a
  hook, a command from the rulebook, and everything they call. The suite is not
  a working path;
- when a mechanism appears that does the same and more, the old one is either
  moved onto the new one or removed **together with its suite** in the same
  edit;
- a legitimate neighbour is named, with its reason: a closed roster for the
  suite, a limit for a human. The reason sits by the name itself rather than
  being implied;
- a knob constant the code does not read either starts being read or becomes a
  comment: a knob that turns nothing lies to whoever turns it.

## Where it applies

**Works** for working code with a test suite: scripts, hooks, actions, library
modules that workflows call.

**Does not work** for closed rosters kept for the suite — lists of classes,
states, paths whose completeness the suite checks — nor for limits addressed to
a human. A working path does not reach them by construction, and that is said
by the name. **Does not work** either for a public API called from outside the
tree: there the working path lives with the consumer, and measuring one's own
tree says nothing.

**Sign of a violation:** a name in working code is called only by the suite,
and nothing by the name says why no working path reaches it.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `scripts/runs_series.py`

See also: [145](145-every-declared-outcome-is-run.md) — every outcome is run,
while here no path reaches the mechanism;
[139](139-a-mechanism-is-confirmed-by-a-run.md) — a live subject for a
mechanism that depends on the platform, while here it is pure functions with no
working call; [209](209-a-constant-is-quoted-by-reference-not-respelled.md) — a
dead path constant and its literal copy in the code are one case for both
rules.
