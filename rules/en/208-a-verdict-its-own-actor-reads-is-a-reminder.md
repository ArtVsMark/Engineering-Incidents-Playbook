# A verdict read by the same actor who then acts is a reminder, not a mechanism

**Area.** gates, process

**Tier.** 3 — gates and processes

**The rule.** A check whose verdict is read by THE SAME actor who then performs the
action holds no more than a sticky note: between red and the action there is
nothing but intent. For the verdict to hold, the check and the action are done by
**one pass** — the same call that checks performs — and red simply never reaches
the action. The bypass must stay possible, but it becomes a **separate, named**
action rather than the default ([051](051-warn-on-likely-block-on-certain.md)).

**Portable beyond Claude Code.** yes — the subject exists wherever a check
prints a verdict and a person or script performs the action with the next
command: a deploy after a run, sending a letter after proofreading, a migration
after a schema comparison.

## The incident

**THE NEIGHBOUR'S MEASUREMENT, WHICH THE PROPOSAL CAME FROM** (the mechanisms
project, 2026-09-17). A pre-push check ran everything runnable locally and
printed a verdict: "green: 18 checks passed", or "red checks: N — too early to
push, fix it here". It had nothing to hold the push with: whoever ran it pushed
next, with their own next command. About fifteen pushes over one shift, and
**THREE of them went out on a red verdict**. All three were the same move: the
verdict printed, the eye slid down the line, the next command already typed. No
harm came of it by luck — the branches were new — and each time a human, not a
mechanism, caught it while re-reading the output afterwards. The repair: the
check gained a pass that pushes the branch itself, and only after green. Verified
by rollback from both ends: let a push through on red and the suite goes red;
push without being asked and it goes red too.

**WE HAVE THE SAME SHAPE, AND A COMMAND CONFIRMS IT:** `grep -c push
scripts/preflight.py` returns **zero**. The run prints "findings in steps: N" and
considers its job done there; `git push` is typed as a separate command by the
same window.

**BUT WE CANNOT NAME THE PRICE, AND THAT IS ITSELF A FINDING.** How many of our
pushes went out on a red verdict is recorded NOWHERE in the tree: the run leaves
no trace, and history keeps only what left. Answering "we had none" would be a
claim about the unverifiable — exactly the third outcome
([039](039-three-outcomes-not-two.md)). This is
[207](207-a-reread-pass-is-ordered-and-stopped-by-measurement.md) on a new
surface: the number the rule says to measure by is not stored here.

**THE COSTLIEST PART IS THE ASYMMETRY OVER ONE AND THE SAME ACTION.** The
catalogue ALREADY HAS this rule's medicine, applied to a neighbouring subject:
`.claude/hooks/push_guard.py` is declared in `.claude/settings.json` as a
`PreToolUse` hook on `Bash` and rejects the call with exit code 2. It stands **IN
THE PATH** of `git push` and holds the branch name and the resurrection of a
merged branch ([202](202-a-merged-branch-is-recreated-by-any-push.md)). The
run's verdict about **the very same** command stands **BESIDE THE PATH** and
holds nothing. Two guards over one action, one inside the path and one alongside
it — and the difference between them is history, not design.

## Why

**This is not about one performer's attentiveness.** Between the check and the
action there is NOTHING but intent, and any performer on the third same-shaped
task in a row will behave the same way. Fixing it with "read more carefully"
means fixing the human instead of the mechanism.

**A printed verdict LOOKS like work done.** The check ran, the line is on screen,
red was named — and that is exactly why it is easy to count as a defence
performed. It was never a defence for a second.

**One pass turns "should not" into "cannot from here".** Red never reaches the
line that acts; not "forbidden" but impossible by this route. That is the whole
difference between a rule and a mechanism
([002](002-rule-without-mechanism.md)).

**A ban you cannot lift breaks urgent work — and then it is removed for good.**
The bypass must remain; its price is that it is a SEPARATE action, visible and
named. An unnamed bypass is exactly those three times.

## Practical limits

- the pass **acts, it does not advise**: the difference shows in the exit code
  and in the absence of the action, not in a louder message;
- **no ban on the raw command is introduced**: what cannot be lifted by your own
  work gets worked around ([051](051-warn-on-likely-block-on-certain.md)), and a
  ban on an external tool does not belong to the project anyway;
- verified by **rollback from both ends**: let the action through on red and the
  suite goes red; perform the action unasked and it goes red too. One end is not
  a proof;
- where the action is performed by ANOTHER actor or another system, the rule does
  not transfer directly: one pass cannot bind them, and the subject becomes a
  handover rather than a coupling;
- "a human reads the verdict" is not itself the violation — the violation is that
  the same human then acts. A reader and a performer split across roles are a
  lawful pair.

## Where it applies

**Works** where the check and the action are both available to one program: a run
and a push, a comparison and a deploy, proofreading and sending — anything where
both halves can be called from one place.

**Does not work** where the action belongs to another side: someone else's
platform, another person, a manual operation in an interface. There the verdict
stays a verdict, and it is held by a handover with confirmation rather than by a
coupling.

**Sign of violation:** a check prints a verdict and the next line of the
instruction begins with "and now do X yourself" — the mechanism ended exactly
where the thing it was built for begins.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `scripts/preflight.py`

Related: [002](002-rule-without-mechanism.md) — the ancestor by form, but it is
about a requirement that has NO mechanism; here a mechanism exists, runs, and
still holds nothing, and that is the news;
[051](051-warn-on-likely-block-on-certain.md) — decides whether to block or to
warn; here what is decided is WHERE the check stands relative to the action, and
both halves agree that the bypass must remain;
[154](154-none-must-name-its-reason.md) — a bypass and a refusal name their
reason; here the bypass being named is the condition under which the coupling is
lawful;
[146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate confirms
itself; a printed verdict confirms that the check ran and says nothing about what
followed it.
