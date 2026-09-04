# Retry only the failures that can pass on their own

**Area.** network, reliability

**Tier.** 4 — code and tests

**The rule.** A retry makes sense for transient failures — overload, a connection
glitch, unavailability. A permanent failure is not cured by retrying: "not found"
does not become found on the second attempt. And if the server named a pause,
that pause outranks your computed one.

## The incident

Requests to the external API go through a session with automatic retries, and the
retryable list is defined **by name**: overload and transient server failures.
Other client failures — "object not found", for instance — are **not retried**,
and the reason is recorded plainly: this is not a transient problem, so the
request cannot simply succeed on a second attempt.

The backoff is exponential, from one second, doubling. But if the server sent a
header stating how long to wait, **that** is used, not the calculation.

And separately, what to do once the retries are exhausted: this is no longer a
flicker but a real problem — the service is down, the credentials expired, the
network is isolated. Different exception classes are kept apart so the error text
shows where to go.

## Why

A retry is a bet that the world will change by itself. The bet pays off only if
the cause of failure is **external and passing**. With a permanent cause a retry
is not merely useless: it multiplies load on a system that already failed, and
postpones the moment a human sees the real error.

Hence the requirement to classify failures **before** writing a retry policy,
rather than sorting them by code at random. Three groups behaving differently: a
transient failure — retry; a permanent failure — report at once; quota exhaustion
— stop, because there a retry also pushes recovery further away.

On the pause header: the server knows more about its own state than the client
does. Our exponential backoff is a guess, its instruction is a fact. A fact must
not be ignored in favour of a guess — and that is exactly what a library's
default backoff does.

## In practice

- the list of retryable failures is defined **by enumeration**, not as
  "everything that is not success";
- the backoff is exponential and bounded in attempts; the total waiting time is
  computed and known in advance;
- the server's pause instruction takes priority over the calculation;
- the retry lives at the transport level so it applies to every request, not only
  where somebody remembered it;
- the message after exhausting attempts distinguishes unavailability from access
  denial: those are different human actions.

## Where it applies

**Works** for network calls, database access, external queues.

**Does not work** for operations with side effects and no protection against
repeated execution: there idempotence comes first, retries second.

**Sign of error:** the journal contains four identical attempts to fetch
something that does not exist.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/use/installation.md` § resilience to
network failures, `core/stepik_client.make_session()`. Related:
[058](058-when-the-quota-is-out-stop.md),
[084](084-best-effort-channels-never-block-the-main-path.md).