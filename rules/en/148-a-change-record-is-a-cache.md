# A change record is a cache, not the state

**Area.** pipeline, data

**The rule.** Read a change's state from its **head** (the checks on the commit)
and from the **main branch** (does it carry that commit). The change record is a
cached projection, and it lags behind events that reached the head. The lag has a
checkable symptom: the record's timestamp is **older** than the last check on its
own head. The cure is a new head, not a re-run of the check.

## The incident

**The first.** A change sat unmerged for four days. Auto-merge was on, there were
no conflicts, the required check was green — on the head and from the same app.
The platform answered with a refusal:

```
405 Repository rule violations found
Required status check "PR check" is expected.
```

Checked and ruled **out** as the cause: the job name matched; cancelled runs with
the same name also existed on a neighbouring change, which merged; the branch
ruleset had not changed; approvals were not required.

The real symptom was in plain sight and looked like plumbing: **the record's
`updated_at` had not moved since before the green checks appeared**. The record
was not being recomputed. Re-running the check added runs to the commit and left
the aggregate untouched. What helped was updating the branch from its base: the
head changed, the state was recomputed from scratch, and the change merged in a
minute.

**The second, four days later, from the opposite side.** The record returned
`merged: false | state: open`, while the main branch already carried this
change's commit and the check on its head had finished **three minutes after**
the record's timestamp, which claimed nothing had happened.

Same symptom, different consequence: in the first case the stale record **kept**
the action from happening; in the second it **hid** that the action already had.
Waiting on the `merged` field would never have ended.

## Why

**The lag is systemic, not incidental.** The record aggregates state from several
sources — commits, checks, branch protection — and is recomputed on events, not
on request. An event may never arrive, arrive late, or not touch the aggregate.
That is the design, not a fault, and waiting for it to "fix itself" is futile: in
the first case that wait lasted four days.

**Debugging goes astray predictably.** Every readable datum agrees, so the
investigation loops: branch rule, check name, app, approvals — and every answer
is correct. Nobody compares the record's timestamp with the checks: it looks like
plumbing.

**The error is one-sided.** The record lies towards "not yet", never towards
"already". So it does not corrupt data — it burns time, and the more careful the
investigator, the longer it burns.

**This amends [049](049-derive-state-from-live-artifacts.md) rather than
repeating it.** 049 says to compute state from live artefacts and names API
responses among them. Here an API response only **looks** live: it is an
aggregate, and an aggregate has a time of its own. 049's list needs this caveat.

## In practice

- there are **two** sources of state: the head and the main branch. The record's
  `merged` field is a third, and the latest of them;
- name the symptom explicitly: the record's timestamp is older than the last
  check on the head;
- the cure is a **new head**, not a re-run: a re-run adds runs to the commit and
  leaves the aggregate as it was. A new commit or an update from the base is
  needed;
- automation does not wait on the record: a loop "until `merged` is true" never
  ends on a stale one. Wait for the commit to appear on the main branch;
- do not confuse with a conflict ([004](004-conflict-is-normal-not-outage.md)) or
  an empty check list ([010](010-empty-checklist-is-not-green.md)): there the
  data itself says something is wrong. Here the data says everything is fine.

## Where it applies

**Works** wherever a foreign platform makes the decision and exposes its state as
an aggregated record: changes, check suites, deployment states.

**Does not work** where state is computed on request: such a source has nothing
to lag behind.

**Symptom of need:** an action is refused by reference to a condition that every
readable datum says is satisfied — or a wait on a record field never ends though
the thing waited for has already happened.

## Trace

ArtVsMark/claude-code-playbook#74