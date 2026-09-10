# A merged branch is resurrected by any push, and the push will not say so

**Area.** pipeline, collaboration

**Tier.** 2 — the pipeline and CI

**The rule.** A branch deleted by the platform on merge is **resurrected by the
next push into it** — together with every commit missing from the shared branch.
So work continued after a merge starts from a **new branch off fresh main**,
never by appending to the old one, and that is checked **before the push** — by
whether the branch still exists on the platform, not by memory of whether the PR
merged.

**Portable beyond Claude Code.** partly — branch resurrection by push exists on
any host that deletes branches on merge. Only the "opening a change is subscribed
to a push" half is tied to this platform.

## The incident

On 8 September change **#180** was squash-merged while a session was writing a
fix into the same branch, `agent/neighbours-gate`.

The platform deleted the branch on merge; the push **recreated it with three
commits** — two already merged (they sit in main as a single squash commit) and
one new. The change-opening run behaved **correctly** and opened #181 on all
three: from its side this is a branch whose content is absent from main, and it
has nothing to tell "new work" from "work merged and the branch resurrected".

The cost: an extra change closed by hand, and a dead branch the session **cannot
delete** — `git push --delete` is rejected with a 403; it has no permission to
delete refs. Half the consequence cannot be cleared by whoever created it.

**The sign of a fake success.** The push itself succeeded and printed
`* [new branch]` — a line that in ordinary work means a new topic is starting and
here meant an old one had been resurrected. Git's output cannot distinguish them,
so "look at what the push printed" is not a method of verification.

## Why

**Memory lies especially readily here, because the merge happens without you.**
The author is writing the next commit; meanwhile someone — a human, a duty run,
an automerge — merges the previous change. Between "I remember the PR being open"
and reality there is not a single event on the author's side.

**Both halves can be mechanised, and they differ.** For the **pusher**: before
pushing, ask the platform whether the branch is alive; "it is gone" with a
non-empty local range means the work has merged. For the **pipeline**: before
opening a change, ask whether a merged change already exists for this same head
branch; if so, this is a resurrection rather than new work.

**The second is the more reliable.** It stands where the decision is taken and
does not depend on what the author remembered, or on whether they ran a check at
all. The first, though, saves an extra run and a dead branch — so neither
replaces the other.

## In practice

- what is checked is **the branch's existence on the platform**, not a PR's
  state in memory: state is derived from a live artefact
  ([049](049-derive-state-from-live-artifacts.md));
- "the branch is gone" with an **empty** local range is an ordinary new topic,
  not a resurrection: the non-empty range is what tells them apart;
- `git push` output is **not** a signal: `* [new branch]` prints in both cases;
- the pipeline half's subject is **the head branch of an already merged change**,
  and it is asked of the platform rather than inferred from a name;
- a resurrected branch is **deleted by whoever has the right**: a session will
  not get past a 403, and leaving the cleanup to it accumulates dead refs.

## Where it applies

**Works** wherever the platform deletes branches on merge and opening a change is
subscribed to a push.

**Does not work** when branches are not deleted: there is nothing to resurrect
and the whole construction is redundant. **Does not work** for branches merged
**without** squashing either: the range after such a merge is empty, and the
ordinary "nothing to push" check covers the case by itself.

**Sign of violation:** the tracker holds a change opened on work already present
in the shared branch and closed as a duplicate.

## Trace

ArtVsMark/ArtVsMark#181

Related: [049](049-derive-state-from-live-artifacts.md) — state is derived from
a live artefact rather than from memory of it;
[003](003-branch-name-is-a-switch.md) — a branch name switches pipeline
behaviour, and here that same name makes a resurrection indistinguishable from
new work; [052](052-only-the-head-of-the-queue-moves.md) — the neighbouring half
of the same ordering: there only the head of the queue moves, here work after a
merge starts afresh.
