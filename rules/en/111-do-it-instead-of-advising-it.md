# If the tool can do it itself, it does it rather than advising

**Area.** interface

**The rule.** A hint saying "type this command" is appropriate only when the tool
genuinely cannot execute it itself. And you check whether the user has a
**channel** for that hint to arrive through.

## The incident

A windowed launch in an environment with no graphical subsystem printed advice:
type the same command in a terminal.

The advice was useless twice over. First, the tool **could have done it itself**
— the same action is available to it directly. Second, on one platform a windowed
launch runs through an interpreter with no console: there is nowhere to print, and
the advice went literally nowhere — the user saw nothing happen.

The fix: in such an environment no window is created, but **the work is done** —
the required mode is started automatically. The exit code comes from what actually
ran rather than being set to one.

## Why

Advice shifts the work onto a person at the moment they are least ready for it:
something did not work, they do not understand why, and they are handed an
instruction. If the tool knows **what** must be done, it also knows how to do it —
otherwise it could not have phrased the advice.

The second half is about the channel. A message exists only if there is somewhere
to deliver it. A windowed launch without a console, a background service, a call
from a script — in all three, printing to standard output equals silence. Before
advising, answer **where** the user will see it.

Hence the order: do it yourself → if you cannot, show it in an available channel →
if there is no channel, fail in a way visible in the result (exit code, file,
error window).

## In practice

- advice is acceptable when the action requires **permissions or a decision** from
  a human: installing a dependency, entering credentials, confirming a deletion;
- before emitting a message, check that the channel exists: a console, an
  interactive session, an available window;
- if the action was performed instead of advised, **say so**: "no graphics, opened
  in the browser" — not silently;
- the result comes from what actually happened rather than being set to a
  constant.

## Where it applies

**Works** for launches, installations, recoveries, migrations — anything where
the tool knows the next step.

**Does not work** when the step requires authority or a user's choice: there
advice is the correct behaviour.

**Sign of trouble:** the help text contains "in that case, do it manually", and
the command in it is available to the tool itself.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/launcher.py`,
ArtVsMark/Stepik-Python-Grader#1134. Related:
[076](076-messages-point-at-what-the-user-actually-has.md).