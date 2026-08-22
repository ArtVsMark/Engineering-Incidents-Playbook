# No writes from a cloud session: credentials are substituted on writes

> **The criterion has been revised.** The tie to the "cloud session" class is
> superseded by [135](135-session-identity-is-established-by-a-write.md):
> identity on writes belongs to the individual session and is established by a
> probing write. Everything else here stands. The record is not edited after the
> fact ([043](043-decisions-are-superseded-not-edited.md)).

**Area.** agent sessions, pipeline

**The rule.** An operation that must carry a human's identity is never run from
an agent session: the proxy substitutes credentials **on writes**, and a bot
becomes the author. You cannot detect this by asking the token who it is — on
reads it answers with the owner. So either the action moves into the pipeline, or
a gate refuses it by environment.

## The incident

A profile storefront had just fixed attribution: commits authored by the owner,
the executor in a trailer, and the merge message reassembled so the trailers
reach the first-parent history of the shared branch.

The very first merge was run **from the session**. The trailers arrived, and the
author of the merge commit became a bot: half of the attribution was fixed and
the other half broken by the same command.

The measurement taken straight afterwards explains why the obvious check does not
catch this. Same token, same session:

| Operation | Who it turned out to be |
|---|---|
| "who am I" request | the owner |
| opening the change | the owner |
| **merging** | **a bot** |

Asking the token who it is, is useless: the answer describes reads.

## Why knowing did not help

The mechanism was **already known and written down** — in a workflow comment in a
neighbouring project, verbatim: the cloud session's proxy substitutes credentials
on writes. The executor read that comment **an hour** before the merge and
paraphrased it in the description of its own change. And still merged from the
session.

This is [002](002-rule-without-mechanism.md) in its purest form: a requirement
that cannot be checked by machine is not followed even immediately after being
said out loud. The distance between "I know" and "I cannot do otherwise" is
**measured here at one hour**.

## Why

**The transport behaves differently on reads and on writes**, and the difference
is announced in no response. An identity check returns the owner because it is a
read; the same identity is substituted on a write. Any "who am I" check you might
want to lean on answers about the other half.

**The error is irreversible from the moment of the merge.** A commit on the
shared branch cannot be rewritten, and the attribution stays wrong forever — while
nothing breaks: the build is green, the change works, the author is simply not
the right one.

Hence the only workable form of a mechanism: check the **environment**, not the
identity. A session knows its own environment, and a ban by environment is
enforceable.

## In practice

- **the operations are named explicitly**: what exactly must carry a human's
  identity — merging, publishing a release, signing, anything that lands in the
  shared history;
- **check the environment, never the token's self-report**: it answers about
  reads and creates a false sense of protection;
- **the escape hatch is named rather than hidden**: a person at their own machine
  merges with their own token, and that is a separate variable with a clear
  message;
- **the pipeline's own default token is not a human either**: merging with it
  fixes one hole and opens another, the author becomes a service account;
- **a written warning is not enough** — this one was written and read; either a
  gate, or there is no rule.

## Where it applies

**Works** wherever an agent session reaches an external platform through a proxy
that substitutes credentials.

**Does not work** where the session acts with its own token directly: then the
identity is the same on reads and writes, and there is no subject.

**Sign you need it:** the shared branch contains commits authored by a service
account although the work was done by a person.

## Trace

ArtVsMark/Stepik-Python-Grader#1302 — the original incident and its fix: a
workflow opens the change with the owner's token. ArtVsMark/ArtVsMark#20 — the
repeat in another project and a gate by environment; merge commit `0728344` is
the proof.

The rule was **paid for twice, in two projects**: the first project's conclusion
lived in a workflow comment rather than in the catalogue — exactly what
[080](080-every-new-rule-goes-into-the-catalogue.md) is for. See also:
[002](002-rule-without-mechanism.md),
[107](107-it-works-for-the-author-means-tested-on-the-authors-sample.md) — there
somebody else's tool outside the author's sample, here your own transport
behaving differently on reads and writes;
[123](123-attribution-is-verified-on-the-final-history.md).
