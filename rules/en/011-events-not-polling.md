# Watching: events over polling, and if polling, then conditional

**Area.** quotas, observation

**Tier.** 2 — the pipeline and CI

**The rule.** A watch loop is the most expensive way to use an API. Prefer
subscription to polling; poll only conditionally and only over the delta.

## The incident

Watching a queue of pull requests in a loop burned quota faster than any other
work. The arithmetic is simple: six open pull requests give **seven or more
calls per pass** (the list, plus a visit to each). Once a minute, that is close
to a thousand calls an hour.

And nearly every response was identical: nothing in the pull requests had
changed.

## What lowers the price, in order of effect

- **Subscription instead of polling.** If the environment emits activity events,
  the watcher must use them: they arrive **without a single request**. Polling
  is the fallback, not the default.
- **Conditional requests (`ETag` / `If-None-Match`).** A `304 Not Modified`
  response **does not consume the limit**. While an object is unchanged, polling
  is free.
- **Delta instead of a full walk.** List sorted by update time; visit only the
  items whose timestamp moved.
- **Interval in minutes, not seconds**, growing with every additional watcher:
  the quota is shared across the account.

## Why

Polling pays for **the absence of change** — that is, for the most common
outcome. All four techniques aim at the same point: do not pay when nothing
happened.

An additional argument against the expensive transport: GraphQL has no
conditional-request mechanism. In a loop that makes it unusable in principle,
not merely "a bit pricey".

## Where it applies

**Works** for any monitoring over a rate-limited HTTP API.

**Does not work** if the API offers neither events nor `ETag` — then delta and
interval are all you have.

**Not relevant** to CI: it has its own token with a separate limit.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § the watcher session