# Whose name a write carries belongs to the individual session, and only a write tells you

**Area.** agent sessions, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** That a session is an agent session in the cloud tells you nothing
about its identity on writes. The criterion is the credentials **this** session
was handed, and they are announced nowhere. Asking does not reveal them: on reads
the token answers with the owner. What is left is a probe — a cheap, reversible
write **of the same class** as the operation ahead, and a look at what the result
is signed with. Until that probe, the ban from
[131](131-no-writes-from-a-cloud-session.md) holds: an operation carrying a
human's identity moves into the pipeline.

## The incident

Rule [131](131-no-writes-from-a-cloud-session.md) was paid for twice, in two
projects, and both times a merge from a cloud session was signed by a bot. On
that sample two criteria — "the session is in the cloud" and "the session was
handed a bot's credentials" — always coincided, and nothing could tell them
apart. The conclusion was recorded about the one visible without measuring: the
class of environment.

Three measurements taken in a single night pulled the class apart.

**The first.** The merges of changes #33 and #37 were performed from a cloud
session deliberately, to test the conclusion. The author of merge commits
`5b01ae0` and `a04f409` turned out to be the owner, not a bot; the committer was
the platform. Under 131 this could not have happened.

**The second.** Cleaning up after the same merge: deleting the merged branch in
the shared repository was refused with a 403, while an ordinary write to the
session's own branch goes through from that same session. The set of permitted
writes is not uniform, and its contents are never disclosed to the session.

**The third.** Within one and the same repository: issue #35 was filed by a
session belonging to another project — author `claude[bot]`, repository
association `NONE`; issues #34 and #36 were filed by this session — author the
owner. One platform, one owner, two identities on the records.

The explanations "the project differs" and "the way of merging differs" both fell
at the third measurement: the project and the method matched, the sessions
differed.

## Why

**The criterion chosen was the one available without measuring.** A session knows
its class of environment for free; its credentials it does not. A criterion that
costs nothing always looks better than one that has to be obtained — that is the
substitution mechanism, not somebody's carelessness. While the sample stays
small, the convenient criterion coincides with the real one and looks confirmed.

**There is nobody to ask.** Asking the token answers about reads — 131 measured
that correctly, and it stands here. There is no announcement at all: the second
measurement shows that even the set of permitted writes is unavailable to the
session until it has been tried. The only remaining source is the write itself.

**The class of the operation is part of the question, not a footnote.** One
session, one measurement: reads go through, writes to its own branch go through,
merging goes through and is signed by the owner, deleting a branch is refused.
"The session can write" is not a boolean, so the only useful probe is one that
matches the class of the operation ahead.

**The asymmetry of cost sets the default.** Treating your session as a bot's when
it is in fact the owner's costs some manual work. The error in the other
direction is irreversible: a commit on the shared branch cannot be rewritten —
131 has already paid for that. So until the probe is done, the ban holds, not the
permission.

## In practice

- **the probe matches the class**: opening a record does not answer for merging,
  and merging does not answer for deleting a branch;
- **the probe is cheap and reversible**: a draft issue, a commit to your own
  branch — not a release and not a merge into the shared branch;
- **look at what the result is signed with, not at what the tool replies**: the
  author of the record, the author of the commit, the repository association;
- **a refusal is a result too**: a 403 means "this write is not granted to the
  session", not "it will be signed by a bot";
- **the result holds for this session**, not for the project and not for cloud
  sessions in general: the next session checks again;
- **a conclusion from one session does not transfer to the class of sessions** —
  that is precisely what this rule was paid for.

## Where it applies

**Works** wherever a session reaches a platform through an intermediary that
hands it credentials from the outside and does not announce what they are.

**Does not work** where the session acts with an explicitly issued token whose
permissions are known: the criterion is announced, there is nothing to probe. Nor
does it work where a probing write is never cheap — the platform offers a single
irreversible operation; there the ban from 131 remains.

**Sign you need it:** two sessions of one project left records under different
names — or a rule about agent sessions leans on the class of environment with no
per-session measurement behind it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#34 — the three measurements, each in its own
comment; ArtVsMark/Engineering-Incidents-Playbook#36 — the session handover, where the
divergence from 131 is named and left to the next session.

Supersedes the **criterion** of rule
[131](131-no-writes-from-a-cloud-session.md): its incident, its conclusion about
the uselessness of asking, and the irreversibility of the error all stand; the
tie to the "cloud session" class does not. The revision is recorded as a new
entry, per [043](043-decisions-are-superseded-not-edited.md). See also:
[107](107-it-works-for-the-author-means-tested-on-the-authors-sample.md) — there
a conclusion drawn from the author's sample, here one drawn from a single
session; [123](123-attribution-is-verified-on-the-final-history.md) — what
exactly is lost once the signature turns out to be the wrong one.