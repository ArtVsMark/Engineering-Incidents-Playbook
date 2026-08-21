# Talking to GitHub: REST by default, GraphQL only where REST cannot

**Area.** quotas, API

**The rule.** Every GitHub operation goes over REST. GraphQL is used only when
the operation physically does not exist in REST, and every such case is named
explicitly.

## The incident

A quota reading taken in the middle of an ordinary working session:

```
core:    used 11   / 5000
graphql: used 2669 / 5000
```

2669 points is roughly **nine operations** — one GraphQL operation costs about
300 points. The same nine calls over REST would have spent 9 requests out of
5000.

More than half the hourly budget went on work fully available in REST, simply
issued through the wrong tool.

Later the same day the counter read `used: 10435` against a limit of 5000: the
machinery kept calling after exhaustion and kept collecting 403s. Work stopped
for an hour.

## Why

The difference is not convenience but **capacity**: 300 against 1. A pipeline
that fits into a few percent of the quota over REST does not physically fit into
an hour over GraphQL.

"Fewer round trips" is no defence: GraphQL wins only when it replaces more than
300 REST calls at once, and routine work on issues and pull requests never
does.

A separate trap: `used` counts **attempts, not successes**. Past the limit a
request is rejected with 403 and still charged — you cannot "use up the
remainder".

## Where it applies

**Works** for any automated pipeline on top of the GitHub API, especially with
several agents on one account — the quota is shared.

**Does not work** where the operation has no REST equivalent. There are few of
them and the list is closed: enabling auto-merge
(`enablePullRequestAutoMerge`), Projects V2, Discussions, minimising a comment.

**Not applicable** outside GitHub: other hosts price things differently.

## Trace

ArtVsMark/Stepik-Python-Grader#1265, #1233
