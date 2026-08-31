# A derived artefact rebuilt more often than changes lives off the main branch

**Area.** pipeline

**The rule.** An artefact rebuilt **more often than changes arrive** — a badge,
a picture, a report over live data — is not stored in the main branch's tree.
Its place is a separate branch a workflow writes to. Otherwise it turns every
merge into a conflict and paints the branch red for a shifted number rather
than a break.

**Portable beyond Claude Code.** yes — the subject belongs to any repository
where an artefact is built by automation and shown to the outside.

## The incident

Three breakages in a row, all on one device.

**First — a conflict on every merge.** The rule count, coverage, test count and
check count lived in `main` under a freshness gate. The gate was right in
intent: a number in an artefact is put there by the build
([005](005-hand-written-numbers-rot.md)). The price turned out higher than the
intent — a badge in the main branch demands a rebuild from **every** change, and
in one session that produced a conflict on every merge and a red `main` not
because something broke but because a number moved. A check that goes red on
correct work is the one people learn to skip
([051](051-warn-on-likely-block-on-certain.md)).

**Second — ignore rules are not consulted on merge.** After the move four badges
came back into the tree during conflict resolution: `.gitignore` covered them,
and `git checkout --theirs` does not ask.

**Third — two copies of one derived file.** The picture "how rules are enforced
across consumers" was added after the move and stayed in the tree: the showcase
reads it **from the branch** `badges`, while the copy in `main` is rebuilt by a
nightly run. In one session that produced four commits to the main branch with
redrawn files nobody reads.

## Why

An artefact's rebuild rate and the rate of changes are independent, and once the
first exceeds the second, the tree stops being the place for the second. Every
rebuild becomes a commit, every commit an occasion for a conflict, and the
conflict is resolved by hand in content that is never written by hand.

Hence the second half: such a branch is a **projection** of what was built, not
an accumulator. Copying over leaves an abandoned file answering forever: it is
not in the main branch, the showcase gate does not see it, and there is nothing
to notice it with ([046](046-name-the-gaps-do-not-level-them.md)).

The asymmetry of cost: an artefact in the tree makes noise on **every** change,
while its absence from the tree costs one line in a workflow. The first is paid
by the whole team continuously, the second once by whoever sets it up.

## In practice

- the derived branch is filled by a run, not by hand, and wholly: a removed
  artefact disappears from it;
- the showcase links **to the branch**, not to the tree — otherwise there are
  two copies again;
- `.gitignore` is required but not sufficient: it is not consulted on merge, and
  a check is needed that the artefact has not returned to the tree;
- no freshness gate is put on such an artefact: it would go red on correct work.

## Where it applies

**Works** wherever an artefact is built by automation and shown outside: badges,
showcase pictures, reports over live data.

**Does not work** for derived files that must change **together** with a change
and be read in its diff: a catalogue index, a summary of answers, an assembled
changelog. They are rebuilt exactly when the source is edited, conflict no more
often than it does, and moving them to a branch would hide from the reviewer
what they are supposed to see.

**Sign of violation:** the main branch's history contains commits touching only
built files, authored by a run rather than a person.

## Trace

ArtVsMark/claude-code-playbook#144

Related: [125](125-a-generated-file-is-not-a-store.md) — a generated file cannot
be a store; here the same artefact is considered from the side of **place**
rather than content; [030](030-changelog-from-fragments.md) — the same cure for
conflicts applied to the changelog: two files with different names never
conflict; [051](051-warn-on-likely-block-on-certain.md) — the badge freshness
gate is exactly the check that went red on correct work.
