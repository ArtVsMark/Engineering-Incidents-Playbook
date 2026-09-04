# A change closes the task in full or names what is left

**Area.** process, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** A change that answers a task has exactly **three** admissible
answers: it closes the task in full, it does **part** of it and names what is
left, or it is exempt by a line stating why. There is no fourth answer — merge
and say nothing. And the second half, without which the first rests on a
promise: after the merge the task's state is **checked, not assumed**. A closed
one must be closed; a partial one must carry a remainder that shows what is
still undone.

**Portable beyond Claude Code.** yes — the subject belongs to any project where
work is tracked as tasks and changes are merged by automation.

## The incident

The catalogue's task #186 stood from 28 August to 3 September naming two
findings at consumers. Both had been fixed in that time — over there, by other
hands, with no signal back here. For six days the task described work that no
longer existed; a human noticed and rewrote it, not a mechanism.

Half the requirement was already held by a mechanism: `pr_body.py` rejects a
change with neither a closing line nor an exemption. The measurement that gate
grew from was harsher — **twelve merges in a row**, the task named only in the
title, zero links. So the form of the link held, while **the task's fate after
the merge did not**: closing was checked by the platform, partial completion was
checked by nobody, and there was nothing to state it with.

The owner named the subject directly and wider than the catalogue: projects do
not close tasks once the work is done and do not mark partial completion — the
grader included, where it recurs most often.

## Why

A task is a **state**, a change is an event. Between them sits a translation,
and it runs one way: the platform can close a task on a word in the body and can
say nothing at all about "half of it is done". So partial completion exists only
where it is **said out loud** — otherwise it is indistinguishable from full
completion, and the difference surfaces when somebody opens the task and reads.

Hence the asymmetry that shapes the rule. An unclosed but finished task looks
cheap and costs dearly: it holds the queue, shows up in reports, and the next
session picks it up again. A falsely closed one is worse: the remainder vanishes
with it, and can be recovered only from the memory of whoever merged. That is
why "partial" must be its own answer rather than being rounded either way.

And third: a promise is not kept where it is made. A `Closes` line is checked
before the merge, and it lies afterwards — when the platform closed the wrong
thing or nothing at all. The check belongs on the far side of the merge, or it
verifies an intention rather than a result
([139](139-a-mechanism-is-confirmed-by-a-run.md)).

## In practice

- three answers, all machine-distinguishable: `Closes #N` · `Part of #N` with a
  named remainder · an exemption line with a reason;
- the remainder is named with **checkboxes**, not prose
  ([028](028-checklist-not-a-list-of-findings.md)): with prose the state has to be
  computed by reading;
- after the merge the state is asked of the tracker: is the closed one closed,
  is the partial one open, does it carry a non-empty remainder;
- the finding is addressed to the task itself, not to a job log
  ([142](142-a-scheduled-red-needs-an-addressee.md)): that is where the person
  who owns the task will see it;
- the task is closed by **a human or their change**, never by the guard: the
  mechanism says "done, yet the task is open", and no more.

## Where it applies

**Works** where tasks and changes are linked by machine: closing on a word in
the body, queue order by the link, reporting through the tracker.

**Does not work** for work that has no task and should not have one: fixing the
session's own tooling, an edit found by a live probe in the same pass. The third
answer exists for that — an exemption with a reason — and demanding a task after
the fact would breed them for form's sake. Nor does it work where the tracker is
not machine-readable: there is nowhere to ask for the state, and only the first
half survives.

**Sign of violation:** a task that merged changes point at is open and has not
been touched since they landed.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#186

Related: [064](064-labels-are-machine-input-not-decoration.md) — the link line is
mandatory and machine-checked; 173 adds the second answer ("partial") and the
check on the far side of the merge.
[028](028-checklist-not-a-list-of-findings.md) — a complex task keeps a checklist;
that checklist is the form a remainder is named in.
[142](142-a-scheduled-red-needs-an-addressee.md) — a finding needs an addressee;
here the addressee is the task itself.
