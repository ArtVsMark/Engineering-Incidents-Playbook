# Migrate from the current version, not from zero

**Area.** data, migrations

**Tier.** 1 — rules and roles

**The rule.** Each step is applied **only** to a state that has not been through
it. Running every step unconditionally breaks what is already migrated, and "a
version higher than expected" is not an error but the norm for a newer store.

## The incident

The store had reached the third schema version. The steps were applied in
sequence, starting from the first.

The primitive that applies a step knows only about **its own** version and treats
any version above the requested one as a downgrade. On a second-version database —
and that was every database created before this change — an unconditional call to
the first step raised "schema newer than expected", and the history fell over
**immediately after the product was updated**.

So the defect fired precisely for those who had already accumulated data, and
precisely at the moment of the update. It was caught by a migration test from the
second version to the third — that is, by a test of the **transition**, not a test
of creation from scratch.

The second lesson from the same place is the **order relative to backfilling**. A
step that changes the structure comes before filling derived data: the backfill
writes through code that already knows about the new fields. The reverse order
gives a half-filled aggregate.

The third is about tooling: the schema is applied through a function that does not
perform an implicit transaction commit. The usual way of executing a batch of
statements would have released the write lock taken above.

## Why

Migration is a function of the **current** state, not a script from the beginning.
Code written as "apply everything in turn" is correct exactly once — when creating
from scratch, that is, in the single case the developer checks most often.

Hence the asymmetry of risk: the "from scratch" path is exercised by every test
run, while the "second to third" path is only covered by a dedicated test that
usually does not exist. And users travel precisely the second path.

Second: **"a version higher than expected" is not an error**. To the primitive it
is a downgrade; to the migrator it is the normal situation "this step is already
done". Conflating the two views is what produces a refusal out of nowhere.

## In practice

- each step is preceded by a check of the current version; steps are not applied
  unconditionally;
- the tests cover **transitions**, not only creation from scratch: from every live
  version to the current one;
- the order of steps relative to backfilling derived data is fixed and explained;
- migration runs in one transaction, and tools are chosen so as not to release the
  lock implicitly;
- the store records which versions count as live — otherwise the list of
  transitions grows without end.

## Where it applies

**Works** for database schemas, file formats, settings versions, cache states.

**Does not work** where old states are unsupported and deleted: there you need not
a migrator but a clear refusal with instructions.

**Sign of a breach:** the update breaks data only for long-standing users.

## Trace

ArtVsMark/Stepik-Python-Grader — `core/history.py`
(ArtVsMark/Stepik-Python-Grader#990, ArtVsMark/Stepik-Python-Grader#947).
Related: [094](094-a-compatibility-shim-makes-migration-permanent.md).