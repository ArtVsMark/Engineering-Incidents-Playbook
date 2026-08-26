# Authorship in the shared branch is set by whoever opens the change

**Area.** agent sessions, pipeline

**The rule.** On a squash merge the platform records as the author of the commit
in the shared branch the **author of the change** — the account that opened it.
The signature on the branch commits has no effect at all. So an agent session
that opens a change with its own token leaves a bot in the history, and
re-signing the commits does not help, because it fixes the wrong field.

## The incident

The rule catalogue merged four changes from an agent session in a row. All four
landed in the shared branch authored by `claude[bot]`; the eight merges before
them are authored by a person.

**The first fix was wrong, and that is the point here.** The commit signature in
the session's container was the agent's, and the conclusion suggested itself:
squash takes the author from the branch commits. The three remaining changes
were re-signed with the person's name, rebased, re-run through the gates and
force-pushed.

The merge author **did not change**. A measurement across six changes settled
it:

| Change | Opened by | Author in the shared branch |
|---|---|---|
| two earlier ones | a person | a person |
| four new ones | the agent's app | the agent's app |

One of the new ones had its branch commits signed by a person — and it changed
nothing. What decides is not the signature but the **account that opened the
change**.

**The rule had already been paid for in a neighbouring project.** There a change
from an agent is deliberately not merged; a separate pipeline job opens it under
the owner's identity. None of that reached the catalogue, neither as a record
nor as a gate — so [080](080-every-new-rule-goes-into-the-catalogue.md) was
broken earlier and the bill arrived here.

## Why

**Three fields look like authorship and none of them are linked.** The branch
commit's signature, the co-authorship trailer, and the author of the change. The
first stays in the branch and disappears with it under squash. The second travels
into the shared branch as text. The third is resolved by the platform into an
account — and that is the one that lands in the history and in the contribution
count. The mistake is easy: the first two are visible in the terminal, while the
decisive third lives on the platform's side.

**Plausibility is useless here.** The hypothesis "squash takes the author from
the commits" reads sensibly, is corroborated by the repository's own auto-merge
notes, and is **wrong**. Telling it apart from the true one required a run —
exactly what [139](139-a-mechanism-is-confirmed-by-a-run.md) is about: until a
mechanism has run against a live subject it is unconfirmed, however correctly it
reads.

**The error becomes irreversible at the moment it becomes visible.** Before the
merge it shows in no way: the gates are green, the signature looks right.
Afterwards the shared branch is protected and the authorship stays forever
([114](114-migrate-from-the-current-version-not-from-zero.md)).

**Asymmetry of cost.** Opening the change under a person's identity costs one
pipeline job with the owner's token. Not doing it costs a history that credits
an application, with nothing left to fix it with.

## In practice

- the mechanism is **opening the change under a person's identity**: a separate
  pipeline job with the owner's token, or the owner opening it. No amount of
  editing branch commits substitutes for it;
- with no such job, a change from an agent is **not squash-merged** — it waits
  for a person. That is slower, and cheaper than a wrong history;
- keep the branch commits' signature correct regardless: under a merge commit,
  rather than a squash, it is that signature which reaches the history;
- verify by running against a live change, not by reading the pipeline's
  description: the description in this very repository was right about the
  intent and wrong about the mechanism.

## Where it applies

**Works** wherever the platform merges by squashing: auto-merge, merge queues,
the "squash and merge" button.

**Does not work** under merge commits — there the branch commits travel into the
history with their own signatures, and those decide. Nor where agent authorship
is the desired outcome: automation repositories, mirrors, generated branches.

**Sign of the violation:** a first-parent appeared in the shared branch whose
author is an application rather than a person's account.

## Trace

ArtVsMark/claude-code-playbook#79 — the post-mortem, the measurement across six
changes, and the wrong first fix; ArtVsMark/claude-code-playbook#78 — the first
merge with an application as author.

Related: [139](139-a-mechanism-is-confirmed-by-a-run.md) — why a plausible
reading fails here; [123](123-attribution-is-verified-on-the-final-history.md) —
attribution is verified on the final history;
[114](114-migrate-from-the-current-version-not-from-zero.md) — the past is not
rewritten, it is a debt; [080](080-every-new-rule-goes-into-the-catalogue.md) —
the neighbouring project's rule never arrived here, and the bill came.
