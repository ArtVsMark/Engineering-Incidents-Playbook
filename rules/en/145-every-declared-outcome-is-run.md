# A mechanism that declares several outcomes is run through each of them

**Area.** gates, runs

**The rule.** A mechanism with more than one declared outcome is verified by
running **every** one of them, not just the successful path. Running one path
confirms that the mechanism starts, and nothing more. Unrun branches usually do
not "work incorrectly" — they **do not exist**: code that control never reaches
reads as working and survives any amount of review.

## The incident

A step's shell declares three outcomes and inspects the return code:

```bash
set -uo pipefail
python scripts/sync_labels.py
rc=$?
if [ "$rc" -eq 2 ]; then exit 1; fi     # the mechanism failed to run
if [ "$rc" -eq 1 ]; then echo "::warning::…"; fi   # a finding for a human
exit 0
```

It reads flawlessly. It works on one outcome out of three.

The platform invokes the step as `bash -e {0}`, and `set -uo pipefail` does
**not** clear that `-e`. On a non-zero code the shell dies before `rc` is ever
assigned: the inspection sits behind a line control never passes. Outcome 1 —
"there are undeclared labels", a finding by design rather than a failure — failed
the run just like a genuine breakage.

Three places in a single day, one shape:

| place | cost |
|---|---|
| `labels-sync.yml` | its very first run was red; the mechanism never worked **a single day**; noticed on the fourth |
| the root `action.yml` | it turned **other projects'** runs red once they adopted the action |
| `main-red.yml` | two outcomes declared, **zero** runs; the first one found a genuine red |

A mutation priced it exactly:

```
script returned   before   after
0                  0        0
1                  1  ✗     0 + warning
2                  2  ✗     1
```

On outcome 1 the old shell produced a **false rejection**; on 2, not even the
right code.

## Why

The successful path runs itself: any ordinary invocation walks it. Every other
branch exists only in the author's head until it has been executed. The
difference between "this branch is wrong" and "this branch is absent" is
invisible to reading — both look like code.

The same technique catches the mirror error: a branch may **reject the
legitimate**. A one-sided suite cannot see it, because it only looks at what the
mechanism must reject ([097](097-a-checker-has-two-error-types.md)).

Two neighbouring rules are **not enough** here, and that is worth saying plainly.
[139](139-a-mechanism-is-confirmed-by-a-run.md) demands a run instead of reading —
and is satisfied by a single successful run, which is exactly what all three
cases had: `labels-sync` ran and went red, the action ran in other people's
projects. [140](140-a-gate-is-tested-by-what-it-must-reject.md) demands the
rejection path be run — but speaks of a **gate**, and a shell step, a scheduled
job or an action published to consumers is not a gate.

The new claim is the third one: a declared branch can be **unreachable**. Not
"wrong" — unreachable, and then its absence is indistinguishable from health,
by reading or by a successful run.

## In practice

- run what is **declared**, not what is imagined: take the list of outcomes from
  what the mechanism says about itself — code, comment or document;
- the "did not run" outcome is checked separately from "has findings": merging
  those two is the most common disappearance ([039](039-three-outcomes-not-two.md));
- a run against a fixture counts, but a live subject is stronger: the fixture is
  built by the same person who made the mistake
  ([139](139-a-mechanism-is-confirmed-by-a-run.md));
- if an outcome cannot be run today, that is recorded rather than silently
  postponed ([046](046-name-the-gaps-do-not-level-them.md)).

## Where it applies

**Works** wherever outcomes are more than one and are named: gates, pipeline
steps, actions published to consumers, return-code handling, failure paths.

**Does not work** where there is one outcome by construction — a command without
branching, a pure transformation with no failure mode. There is nothing to run
"each of one", and the requirement degenerates into ritual.

**Symptom of the violation:** the mechanism contains a branch, and nobody can say
when it last executed.

## Trace

ArtVsMark/claude-code-playbook#83
