# A side-effect guard blames the wrong suspect — and exclusions are defined by shape

**Area.** tests, gates

**Tier.** 3 — gates and processes

**The rule.** A guard comparing "before" and "after" snapshots attributes a change
to whoever it was completing when it noticed. Neighbouring processes produce false
accusations, and they must be excluded **by the shape of the name**, not by a
list — yet more narrowly than "everything".

## The incident

The guard watched that no test wrote outside its own temporary folder. It
snapshots the dangerous directories at startup and compares after every test.

A full run produced **14 false accusations in a row** — all of them caused by
files from a **neighbouring tool** running on the same machine at the same time.
The run itself was green: the tests violated nothing, the neighbour did, and the
blame went to whoever was completing when the file was noticed.

The first attempt at a fix — a list of exact names — failed predictably. The tool
wrote its settings atomically, and beside the main file lived a lock file and a
temporary file with a random suffix. The exact list filtered out the first two
and **kept accusing on the third**.

The opposite extreme — "ignore everything in the home directory" — would have
restored exactly the defect the guard was written for: a test once deleted a real
user database there.

The working solution is exclusion **by prefix**: it covers the whole family of
the tool's temporary names without opening up the directory.

## Why

The guard sees **a difference of states**, not the author of a change. Between two
snapshots more than the subject is running: other processes of the same user,
background services, editors, the run tooling itself. Attributing the change to
the subject is all the guard can do, and it is wrong exactly in the cases where
the change is not the subject's.

A false accusation here costs more than a miss: it points at the innocent, and
time goes into studying a test that has nothing to do with it. Fourteen of those
in a row and the guard stops being believed at all.

Second: **atomic writing spawns a family of names**. The main file, the lock, the
temporary with a random suffix — all appear and disappear at arbitrary moments.
Any list of exact names falls behind the tool's next version, so the exclusion is
defined by a pattern rather than an enumeration.

## In practice

- separate two classes of exclusion: **artefacts of the run itself** (written
  legitimately by the tooling) and **neighbours' files** — different reasons,
  different lists;
- the exclusion is defined by a prefix or a pattern; an exact name breaks on the
  first atomic writer;
- the exclusion stays **narrow**: "the whole directory" repeals the guard;
- the guard's message says honestly that it shows a difference, not an author —
  otherwise the first false accusation will be investigated as a real one.

## Where it applies

**Works** for side-effect guards: file system, environment variables, global
state, network ports.

**Does not work** in an isolated environment where outside writers do not exist by
construction — there the difference really does belong to the subject.

**Sign of trouble:** accusations arrive in batches and point at unrelated tests.

## Trace

ArtVsMark/Stepik-Python-Grader — `tests/conftest.py` (`_no_writes_outside_tmp`),
ArtVsMark/Stepik-Python-Grader#818 (a deleted user database),
ArtVsMark/Stepik-Python-Grader#646. Related:
[072](072-guard-the-cause-and-the-effect.md).