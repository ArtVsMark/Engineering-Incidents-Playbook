# A switch that cancels an operation needs an addressee for the cancellation

**Area.** pipeline, observation

**The rule.** A switch that cancels an operation on a non-match cancels it
**silently**: "did not match" and "matched, nothing to do" produce one observable
outcome — nothing. Whoever pushed sees their command succeed and walks away
believing the work is delivered. The cancellation therefore needs an addressee —
an issue, a message, a refusal, anything that tells it apart from inaction.

## The incident

A finished rule sat on the branch `rule/144-context-window-for-prose`. Both
language trees, the index, the export, the badges, a changelog fragment, the
catalogue's own answer, a resolvable trace into another project — the work was
complete by every requirement of the rulebook.

No change appeared. The pipeline opens one by the `agent/` prefix, the branch was
named `rule/…`, and the switch behaved exactly as declared: without the prefix a
change is not opened **at all**.

What matters next is what did **not** happen. There was no run — so no red, no
log, no exit code, no line on any tab. The window's handover said "no open
changes", and it was not lying: there genuinely were none. The work was found
only because the next window idly looked at the branch list.

More than a day passed between "the rule was written" and "the rule was noticed",
and the only reason it was noticed was chance.

## Why

A cancellation by non-match produces **no artefact at all**. That sets it apart
from everything the catalogue already knows how to catch: a failure has a code
and output, a red run has a tab, an empty check has the option of failing. Here
there is nothing to catch: a successful `push` looks identical in both cases,
because it is identical.

Hence a consequence that breaks the habitual repair: **the remedy cannot live
inside the switch**. The switch never ran. Someone third must notice — whoever
looks for work with no change attached.

Neighbouring rules cover other places:

- [075](075-a-guard-that-finds-nothing-must-fail.md) — about a **check** that
  found no subject: it must fail. Here there is nothing to fail; no run happened.
  And 075 draws its own boundary in its own words: "for any **checks**";
- [078](078-cancelled-is-not-an-error.md) — about termination **by human
  will**: it gets its own terminal status. Here there is no will, only a
  non-match;
- [003](003-branch-name-is-a-switch.md) — requires the switch to be declared in
  the first line. It was: the prefix is named in the rulebook and in the
  handover's first point. Knowing it did not help;
- [142](142-a-scheduled-red-needs-an-addressee.md) — about a failure that **did
  happen** and was printed in the wrong place. Here no failure happened at all,
  which is not a mitigation but an aggravation: silence is indistinguishable from
  "there was no work".

## In practice

- the addressee is set up **outside the switch**, next to whoever sees work with
  no change attached: the branch list, a tracker sweep, the handover report;
- "nothing was done because there was nothing" is also said out loud: two
  silences are identical, two messages are distinguishable;
- the switch cannot be charged with diagnosing what it never saw: it does not
  know that a finished piece of work sat on that branch;
- check the **subject**, not the intent: the existence of a branch touching
  guarded paths, not a guess at what the author wanted.

## Where it applies

**Works** wherever an operation runs on a condition match and the non-match
produces no artefact: a branch prefix, a path filter, a label, a trigger
condition.

**Does not work** where the non-match is visible by itself: the command printed
"skipping", the run started and exited with an explanation. There the addressee
already exists and a second one becomes noise.

**Symptom of the violation:** finished work is discovered by a chance glance
rather than by something that was supposed to announce it.

## Trace

ArtVsMark/claude-code-playbook#96
