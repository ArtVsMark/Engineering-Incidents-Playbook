# Every exhaustible resource has a detour map prepared in advance

**Area.** quotas, planning

**The rule.** Know beforehand what stops working and what keeps working when
each resource runs out. The mode on exhaustion is **accumulate**, not wait.

## The incident

There turned out to be five resources that run out independently: two separate
counters on the external API, a separate search limit, the build executor queue,
and the agent session's own limit. Each runs out in its own way and shows itself
differently — from an outright rejection to "the card stopped rendering".

While there was no map, any exhaustion meant stopping all work. The key
observation turned out to be simple: **the boundary does not run where you think
it does**. Pushing branches out goes over the version control protocol, not
through the API — and it works at zero API quota. Verified: a session calmly made
a fix, pulled the shared branch and pushed its own; it would only have been
blocked at opening the pull request.

Hence the mode of "accumulating branches": keep working and publish in a batch
after the reset, or from another session. Not "sit and wait".

The map ended up as a four-column table: what ran out · **how to tell** · what is
unavailable · what is available. The second column matters as much as the first:
in three of the five, exhaustion does not look like an error.

## Why

The detour must be known **before** exhaustion. At the moment of failure there
is no time to investigate, and the obvious conclusion ("nothing works") is almost
always wrong: one channel of several failed while the neighbours are alive.

Second: without a map, exhausting one resource stops work unrelated to it. A list
of what does not depend on the exhausted resource is a ready answer to "what do I
do now", rather than an invitation to improvise.

Third: the map exposes **false dependencies**. While compiling it you discover
that half the operations believed to need the scarce resource do not need it at
all — like pushing branches.

## In practice

- each row carries a tell: **how to know that this is what ran out** —
  especially where exhaustion disguises itself as an empty result;
- beside it, work that does not depend on this resource at all, and it must be
  real work, not "read some documentation";
- the boundary is established by experiment, not by reasoning: "presumably that
  goes through the API too" is a common and expensive mistake;
- the map lives next to the diagnostics: one command shows the remainder of every
  resource at once.

## Where it applies

**Works** where there are several resources and they run out independently.

**Does not work** with a single resource without which nothing happens — there
the map degenerates into "wait".

**Sign that it is needed:** answering "what can we do right now" after a failure
takes more than a minute.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § the route when
limits run out (§ the boundary runs along "git versus API", § what ran out →
where to go).
