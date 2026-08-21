# Cleanup after a failure must not turn the failure into a success

**Area.** code, reliability

**The rule.** A handler that cleans up after itself catches **everything** that
interrupted the work and always re-raises the cause. A narrow catch misses the
interruption; a broad catch without re-raising hides the failure.

## The incident

Atomic writing was leaving junk behind. The cleanup handler caught only
input/output errors — while a keyboard interrupt arrives as a **different
class**, outside that branch, and passed straight through.

The result: a temporary file with a random name stayed beside the target
forever, with nobody to sweep it up. It accumulated for exactly those who
interrupt work most often — that is, for active users.

The fix is to catch **everything** that interrupted the write, not only the
expected class. And the second half, no less important: the exception is
**always** re-raised after cleanup — removing a temporary file does not turn a
failed write into a success.

## Why

Cleanup and error handling have different jobs, and they are constantly
conflated. Cleanup is responsible for leaving no traces. The decision whether
the operation succeeded belongs to the caller — and must not be taken away from
them.

Hence two symmetric mistakes:

- **too narrow a catch** — cleanup does not run on an unforeseen interruption,
  and junk accumulates;
- **too broad a catch without re-raising** — the caller receives a silent
  success where nothing was written. That is worse: the next step works with
  data that does not exist.

Separately: **errors inside the cleanup itself are suppressed**, and that is
correct. Failing to delete a temporary file is no reason to lose the original
cause of failure; the cause matters more.

## In practice

- the catch is broad and the re-raise is mandatory — both halves, not one;
- inside the cleanup, errors are suppressed precisely, not with a blanket
  silencer;
- cleanup does nothing but clean up: no writes, no retries;
- the tests include an interruption scenario, not only an input/output error.

## Where it applies

**Works** for any operation with temporary state: files, locks, processes,
connections, transactions.

**Does not work** where the failure really is acceptable and continuing is
normal — but then it is not cleanup, it is a fallback path, and it must be
visible.

**Sign of trouble:** temporary files accumulate in the working directory and
nobody knows where they came from.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/atomic_io.py`, #996.
Related: [045](045-no-silent-fallback.md).
