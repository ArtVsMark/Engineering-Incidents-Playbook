# A second finding on one place stops the one-form-at-a-time patching

**Area.** code, quality

**Tier.** 4 — code and tests

**The rule.** When one and the same place — a predicate, a command parser, a
branch order — receives its **second** finding, patching it one form at a time
stops. The next edit of that place starts with a **list of forms**: measured,
read by name, with a check for each form. Only then is the place edited.
Otherwise the reviewer ends up writing the list of forms, one form per pass,
and each pass costs a platform cycle.

**Portable beyond Claude Code.** yes — the subject exists in any team with an
outside review of changes: a human reviewer also names one form at a time, and
the author also fixes exactly that one.

## The incident

**THE NEIGHBOUR'S MEASUREMENT, WHICH THE PROPOSAL CAME FROM** (the mechanisms
project, 21–24.09.2026). Changes #616–#743 received 187 unique outside-review
findings across 77 changes. 48 places got at least one finding and 21 places
got findings on two or more changes. Of those, 13 reached a third change and 9
a fourth or more. Five chains were read by name, 4–8 changes each. The sequence
is the same everywhere: a finding names a form → the window fixes exactly that
form and names its neighbours (195) → the review finds the next form at the new
boundary.

**HERE THE SAME HAPPENED — ON THE PUSH GUARD, THREE TIMES.** All three chains
run through one place, the command parser in `.claude/hooks/push_guard.py`:

1. **08.09, 17:40–18:48** — #412 → #419 → #423 → #424. Four fixes in 68
   minutes: the subcommand, branch deletion, `--` before paths, `--` with
   `switch`. The first three were false refusals the window hit while working.
   The fourth was a review finding on the third. Rule
   [195](195-a-narrowed-predicate-names-its-neighbour.md) was written in the
   middle of this chain, at 18:33, and #423 used it to name the neighbours of
   "the first word after checkout" — three were found. Finding #424 landed on
   that same fix.
2. **10.09, 22:50–23:52** — #475 → #476 → #477 → #479 → #480. Five changes in
   62 minutes. The first was a review finding on rule 202 (#468), and each
   later one a review finding on the one before. The body of #479 says so:
   "the third in a row on one guard". 195 was already in place.
3. **17.09–25.09** — #553 → #556 → #569, with both 195 and
   [206](206-a-form-the-gate-cannot-see-is-a-bypass.md) in place. The body of
   #556: "the first fix introduced blindness where there had been none". To the
   review findings on #556 — the second on this place — the window answered
   differently from before (#569): it measured the forms all at once, and five
   were blind instead of the one named. The finding on #569 was already about
   another place — the rollback boundary in the test suite (#573).

A finding here also includes a false refusal hit while working: it names one
form in the same way. Counting review findings alone, the first chain drops
out — review gave one there (#424). In the second, the second review finding
was closed one form at a time, and two more about the same parser followed
(#477, #479), plus one about its docstring (#480). In the third, the second was
closed with a list, and the next finding was about another place.

**AND TODAY, 25.09, IN ANOTHER PLACE.** The parser of `python` calls in
`scripts/check_workflows.py` got a finding on #583: its pattern was blind to a
platform expression with spaces. Fix #587 moved the parser to `shlex` and named
its neighbours — two other scripts with the same search — as having no subject:
measured over the workflows, 82 calls of one form and none with an option
before the path. The next review pass found two new forms on #587 itself: an
option taking a value (`-W ignore`) and an apostrophe in an unrelated argument.
The measurement was made, and it was correct. But the tree shows the forms
people write today, while a parser of a foreign language meets every form its
grammar allows. The third edit (#590) took the list from the interpreter's
reference and put a check on each form.

## Why

**A finding names one form — the one it was found on.** The window fixes
exactly that form. Even when it names neighbours, as 195 requires, it lists
them from the named case, not from the space of forms, and the boundary of the
new fix lands where the review will look next time.

**The threshold is the second finding, not the first.** One finding on a place
is ordinary work. The second shows that the model the fix followed is
incomplete: the fix went from the finding's form, not from a list. At the
neighbour's, 13 of the 21 places with two changes reached a third. Here the
second finding closed one form at a time was followed by two more on the same
place, and the one closed with a list by none. A second finding on code is
more often the start of a chain than its end, if it is closed one form at a
time.

**The costs are asymmetric.** A list costs one window pass. A chain costs a
platform cycle per form: push, run, review, merge. On 10.09 that was five
cycles in an hour, and the reviewer was the one listing the forms.

**This is not 195.** 195 requires every fix to name the neighbours of the named
case, but it does not say when to stop fixing one case at a time. Of the
guard's thirteen fixes, exactly one names neighbours under 195 explicitly, and
the next finding landed on that same fix: neighbours listed from the case did
not close the boundary.

**This is not 206.** 206 requires a gate to read every form of its subject, as
measured over the tree — a requirement on how a gate is built. 210 is about a
sequence of edits to one place, and to any place, not only a gate: a parser in
a hook, a branch order, a recogniser in a test suite. And 210 takes the list
from beyond the tree when the place parses a foreign language.

## In practice

- a **place** is one question the code decides: a predicate, a parser, a
  branch order. Not a file: a second finding in the same file about a
  different question is the first finding on a different place;
- the **list of forms** comes from what the place reads. From the tree — the
  forms people write today. From the reference — when the place parses a
  foreign language: the shell, the options of `git` or of the interpreter. The
  tree shows the habit; the reference shows the space;
- the list is **read by name**: every form is named and every form has a check.
  A form the place deliberately does not read is declared aloud, as in 206;
- the list, with its count, goes into the change body or the changelog
  fragment rather than staying in the window's head;
- the threshold is revisited by measurement. If second findings on code start
  ending at the second change, the threshold is raised.

## Where it applies

**Works** for places that decide by the form of what is written: a predicate,
a regular expression, a command parser, a branch order, a recogniser in a test
suite. That is, wherever a finding names a form.

**Does not work** for prose — changelog fragments, skill text, documentation:
there is nothing to list there. At the neighbour's, the eight places that
stopped at the second finding were mostly of this kind. **Does not work**
either for a second finding about a different question in the same file: that
is a different place.

**Sign of a violation:** a third change in a row edits one place, and its body
names one form — the finding's — with no list and no count of forms.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/finding-kinds.json`

See also: [195](195-a-narrowed-predicate-names-its-neighbour.md) — every fix
names its neighbours, while 210 says when one-form fixes stop;
[206](206-a-form-the-gate-cannot-see-is-a-bypass.md) — a list of forms as the
design of a gate, while here it is the step before the third edit of any place;
[207](207-a-reread-pass-is-ordered-and-stopped-by-measurement.md) — the order
and stopping of a re-read of a corpus of answers, a different subject.
