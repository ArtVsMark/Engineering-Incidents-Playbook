# Lock the companion file, not the file that gets replaced wholesale

**Area.** code, concurrency

**The rule.** If writing is made atomic by replacing the file, lock a **separate
companion file**. A lock on the target itself disappears together with the
target at the moment of replacement.

## The incident

Atomic writing is arranged the standard way: write to a temporary file, then
replace the target with it in one operation. That way a reader never sees a
half-written file.

The lock against concurrent writes was taken on the target — and did not work.
Replacement **changes the file object itself**: a lock taken on the old one means
nothing after the swap. The second writer calmly takes a "free" file and writes
over it.

The defect is treacherous because tests barely catch it: both operations are
individually correct, and the race requires a coincidence in timing.

So the lock is taken on a companion file beside the target: it is never
replaced, it lives for the whole operation, and it serves as the single point of
synchronisation.

## Why

A lock is bound not to a name but to the object in the file system. An atomic
replacement by definition creates a **new** object and moves the name onto it —
so any association with the old one, including the lock, is severed.

Hence a general rule, broader than files: **synchronise on something that is not
recreated**. As soon as the lock object lives shorter than the operation it
protects, protection becomes the appearance of protection — and the appearance is
worse than nothing, because it closes the question.

Second: the waiting mechanism is chosen by load profile. Writes are rare and
short — a short poll is cheaper than a blocking call, behaves identically across
platforms, and needs no separate timeout path.

## In practice

- the companion lives beside the target and is **never replaced**;
- lock the companion and write the target, not the other way round;
- the companion's name is predictable and documented: people will see it in the
  directory and ask what it is;
- waiting has a bound: an eternal lock turns a race into a hang.

## Where it applies

**Works** for atomic replacement of files, directories, symbolic links,
versioned records.

**Does not work** if the write goes **into the same** object without replacement
— there a lock on the target is correct.

**Sign of trouble:** there is a lock, and concurrent writes are still lost.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/atomic_io.py`
(`LOCK_SUFFIX`), #1136.
