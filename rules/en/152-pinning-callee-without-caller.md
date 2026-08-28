# Pinning the callee without pinning the caller protects nothing

**Area.** pipeline, security

**The rule.** Pinning called code to the shared branch is worth doing only where the
**calling** file is also taken from the shared branch. On a `pull_request` event
the platform takes the workflow file from the change itself — so whoever edits
the change edits the step too, and the pinned script gets rewritten along with
the call. On `pull_request_target` and `workflow_run` the reasoning inverts: the
workflow file comes from the shared branch, and pinning the callee is mandatory.

**Portable outside Claude Code.** yes — the subject belongs to the CI platform,
not to agent sessions: the same distinction between events holds for anyone.

## The incident

A showcase repository moved platform-response handling into
`scripts/gh_outcome.py` and made `automerge.yml` take it from the shared branch
via `ref: base.sha`. The motive looked sound: the step's environment holds the
owner's personal token, and running code from the change under it looked like a
substitution of trust.

The protection turned out to be **zero**. `automerge.yml` itself still comes
from the change: whoever edits the change rewrites the step and calls whatever
they like, and the pinned script simply stops being called. A locked door beside
an open wall.

The cost arrived immediately, from the other side. On the very change that
**introduces** the script, it does not yet exist on the shared branch — the step
failed with `Process completed with exit code 2` on a missing file. The
mechanism landed in exactly the deadlock it was meant to fix: a red `automerge`
puts the change into `unstable`, and the platform refuses to enable auto-merge
on an unstable change, by pipeline or by hand.

The real boundary lies elsewhere: a change from a fork has no secrets at all,
and the job exits at `SKIP` before any `checkout`.

## Why

Pinning protects a **link**, while trust is decided by the **whole chain**. If
the caller comes from an untrusted place, it is under no obligation to call the
pinned thing; if the caller comes from the shared branch, an unpinned callee is
the hole. There is no state in between: one pinned link in an unpinned chain
does not reduce the surface, it only creates the impression that it did.

**The asymmetry of cost is what gives the rule its shape.** Needless pinning is
not merely useless — it introduces a failure where none existed: the callee may
not exist on the shared branch yet, and the first victim is the change that adds
it. A missing pin on `pull_request_target` is a genuine hole. The same-looking
decision carries opposite signs in the two cases, and the sign is set by the
event, not by the author's intent.

## In practice

- look at the **event**, not at the step: `pull_request` takes the workflow file
  from the change, `pull_request_target` and `workflow_run` from the shared
  branch;
- easy to miss: secrets. A change from a fork has none, so trust in its code is
  moot there — the job is cut off earlier;
- revisit the decision if the triggering event changes: the same pin turns from
  useless into mandatory.

## Where it applies

**Works** where a workflow calls the repository's own code and the event decides
where the workflow file itself comes from.

**Does not work** for third-party actions (`uses:`) — those are pinned by SHA
always, regardless of event: they come from someone else's repository, and the
version there moves without us. This rule is about **your own** code living in
the same repository as the workflow.

**Symptom of need:** a step takes its own script from the shared branch on a
`pull_request` event — or fails on the change that introduces that script.

## Trace

`ArtVsMark/ArtVsMark` — `.github/workflows/automerge.yml`: the pin was removed
and the reason written in a comment beside the step, so the next session does
not "restore the security" it looks like.

Related: [097](097-a-checker-has-two-error-types.md) — a checker's two error
types cost differently; [139](139-a-mechanism-is-confirmed-by-a-run.md) — a
mechanism is confirmed by a run, not by reading: the zero protection here was
shown by a run.
