# A write carrying a human's identity waits for a probing write from this session

**Area.** agent sessions, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** An operation carrying a human's identity moves into the pipeline
until a probing write of the same class from this session has shown the
human's signature. Asking the token does not reveal identity on writes — on
reads it answers with the owner — and the criterion "the session is an agent
session in the cloud" does not determine it: it belongs to the credentials
this particular session was handed, and they are announced nowhere.

**Portable beyond Claude Code.** partly — credentials substituted on writes
happen to any executor that an intermediary hands a token from the outside (a
pipeline bot, a service account), and a probing write of the same class works
there as is; tying the probe to a single session and its lifetime is specific
to agent sessions.

## The incident

**A merge from the session was signed by a bot** (a profile storefront,
ArtVsMark/ArtVsMark#20; recorded in the catalogue on 22 August 2026 as rule
131). A profile storefront had just fixed attribution: commits authored by the
owner, the executor in a trailer, and the merge message reassembled so the
trailers reach the first-parent history of the shared branch. The very first
merge was run **from the session**. The trailers arrived, and the author of the
merge commit became a bot: half of the attribution was fixed and the other
half broken by the same command. Merge commit `0728344` is the proof.

The measurement taken straight afterwards explains why the obvious check does
not catch this. Same token, same session:

| Operation | Who it turned out to be |
|---|---|
| "who am I" request | the owner |
| opening the change | the owner |
| **merging** | **a bot** |

Asking the token who it is, is useless: the answer describes reads.

**It was a repeat, and knowing did not help** (the same incident). The rule was
first paid for in ArtVsMark/Stepik-Python-Grader#1302: the fix was a workflow
that opens the change with the owner's token. The conclusion lived in a
workflow comment in a neighbouring project, verbatim: the cloud session's proxy
substitutes credentials on writes. The executor read that comment **an hour**
before the merge and paraphrased it in the description of its own change. And
still merged from the session. This is [002](002-rule-without-mechanism.md) in
its purest form: the distance between "I know" and "I cannot do otherwise" is
**measured here at one hour**. The rule was **paid for twice, in two
projects**, the second time because the first project's conclusion lived
outside the catalogue ([080](080-every-new-rule-goes-into-the-catalogue.md)).

**The "cloud session" criterion was pulled apart by three measurements taken in
a single night** (the catalogue, ArtVsMark/Engineering-Incidents-Playbook#34;
recorded on 22 August 2026 as rule 135). In the two incidents above the
criteria "the session is in the cloud" and "the session was handed a bot's
credentials" always coincided, and nothing could tell them apart. The
conclusion was recorded about the one visible without measuring: the class of
environment.

- **The first.** The merges of changes #33 and #37 were performed from a cloud
  session deliberately, to test the conclusion. The author of merge commits
  `5b01ae0` and `a04f409` turned out to be the owner, not a bot; the committer
  was the platform. Under the earlier conclusion this could not have happened.
- **The second.** Cleaning up after the same merge: deleting the merged branch
  in the shared repository was refused with a 403, while an ordinary write to
  the session's own branch goes through from that same session. The set of
  permitted writes is not uniform, and its contents are never disclosed to the
  session.
- **The third.** Within one and the same repository: issue #35 was filed by a
  session belonging to another project — author `claude[bot]`, repository
  association `NONE`; issues #34 and #36 were filed by this session — author
  the owner. One platform, one owner, two identities on the records.

The explanations "the project differs" and "the way of merging differs" both
fell at the third measurement: the project and the method matched, the
sessions differed. The divergence from the earlier conclusion was named and
left to the next session in the handover
ArtVsMark/Engineering-Incidents-Playbook#36.

**The family's answers diverged across two numbers for one requirement** (the
`export/where.json` snapshot at commit `87209c7` of the `badges` branch,
8 October 2026). All six connected projects answered both 131 and 135. The
usage-limits project answered 131 `not-applicable` and 135 `active`: it made
the probe, saw the owner's signature, and the ban stopped applying to it — the
second answer decided whether the first one held. In the mechanisms project
131 is held by the pipeline (`.github/workflows/agent-pr.yml` opens the change
with the owner's token) and 135 by an attribution gate over the first parents
of the shared branch (`.github/workflows/attribution-history.yml`): different
mechanisms, one breakage.

The merge was proposed by the mechanisms project
(ArtVsMark/Engineering-Pipeline-Mechanisms:merge/a-human-identity-write-waits-for-a-probe)
from the merge skill's card taken on this pair
(ArtVsMark/Engineering-Incidents-Playbook#728), admitted in
ArtVsMark/Engineering-Incidents-Playbook#645, reviewed in
ArtVsMark/Engineering-Incidents-Playbook#744.

## Why

**The transport behaves differently on reads and on writes**, and the
difference is announced in no response. An identity check returns the owner
because it is a read; the same identity is substituted on a write. Any "who am
I" check you might want to lean on answers about the other half. There is no
announcement at all: even the set of permitted writes is unavailable to the
session until it has been tried. The only remaining source is the write
itself.

**The criterion chosen was the one available without measuring.** A session
knows its class of environment for free; its credentials it does not. A
criterion that costs nothing always looks better than one that has to be
obtained; while the sample stays small, the convenient criterion coincides with
the real one and looks confirmed. So a ban "by environment" and a ban "until
the probe" are not two requirements but two phases of one: the class of
environment only sets the default, and the probe lifts it.

**The class of the operation is part of the question, not a footnote.** One
session, one measurement: reads go through, writes to its own branch go
through, merging goes through and is signed by the owner, deleting a branch is
refused. "The session can write" is not a boolean, so the only useful probe is
one that matches the class of the operation ahead.

**The error is irreversible from the moment of the merge, and that sets the
default.** A commit on the shared branch cannot be rewritten, and the
attribution stays wrong forever — while nothing breaks: the build is green, the
change works, the author is simply not the right one. Treating your session as
a bot's when it is in fact the owner's costs some manual work; the error in the
other direction cannot be repaired at all. So until the probe is done, the ban
holds, not the permission.

## Practical boundaries

- **the operations are named explicitly**: what exactly must carry a human's
  identity — merging, publishing a release, signing, anything that lands in the
  shared history;
- **the probe matches the class**: opening a record does not answer for
  merging, and merging does not answer for deleting a branch;
- **the probe is cheap and reversible**: a draft issue, a commit to your own
  branch — not a release and not a merge into the shared branch;
- **look at what the result is signed with, not at what the tool replies**: the
  author of the record, the author of the commit, the repository association;
  asking the token answers about reads and creates a false sense of protection;
- **a refusal is a result too**: a 403 means "this write is not granted to the
  session", not "it will be signed by a bot";
- **the result holds for this session**, not for the project and not for cloud
  sessions in general: the next session checks again, and a conclusion from one
  session does not transfer to the class of sessions;
- **the escape hatch is named rather than hidden**: a person at their own
  machine merges with their own token, and that is a separate variable with a
  clear message;
- **the pipeline's own default token is not a human either**: merging with it
  fixes one hole and opens another, the author becomes a service account;
- **a written warning is not enough** — this one was written and read; either a
  pipeline or a gate, or there is no rule.

## Where it applies

**Works** wherever a session reaches a platform through an intermediary that
hands it credentials from the outside and does not announce what they are —
including a proxy that substitutes credentials on writes.

**Does not work** where the session acts with an explicitly issued token whose
permissions are known: the identity is the same on reads and writes, the
criterion is announced, there is nothing to probe. An inner branch: where a
probing write is never cheap — the platform offers a single irreversible
operation — there is no probe, and the operation always moves into the
pipeline.

**Sign of a violation:** the shared branch contains commits authored by a
service account although the work was done by a person; or two sessions of one
project left records under different names; or a rule about agent sessions
leans on the class of environment with no per-session measurement behind it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Stepik-Python-Grader#1302 — the original incident and its fix: a
workflow opens the change with the owner's token. ArtVsMark/ArtVsMark#20 — the
repeat in another project and a gate by environment; merge commit `0728344` is
the proof.

ArtVsMark/Engineering-Incidents-Playbook#34 — the three measurements, each in its own
comment; ArtVsMark/Engineering-Incidents-Playbook#36 — the session handover, where the
divergence from 131 is named and left to the next session.

Supersedes: [131](131-no-writes-from-a-cloud-session.md),
[135](135-session-identity-is-established-by-a-write.md) — the ban and the
probe that lifts it were recorded as two rules, and the answer to the second
decided whether the first held; the old entries remain with a supersession
mark ([043](043-decisions-are-superseded-not-edited.md)).

Related: [002](002-rule-without-mechanism.md) — knowledge without a mechanism
did not stop the merge even an hour after it was read;
[080](080-every-new-rule-goes-into-the-catalogue.md) — the first project's
conclusion lived in a workflow comment rather than in the catalogue;
[107](107-it-works-for-the-author-means-tested-on-the-authors-sample.md) —
there a conclusion drawn from the author's sample, here one drawn from a single
session and your own transport behaving differently on reads and writes;
[123](123-attribution-is-verified-on-the-final-history.md) — what exactly is
lost once the signature turns out to be the wrong one.
