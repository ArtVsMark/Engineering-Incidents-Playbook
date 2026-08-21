# Write the field, not the snapshot, when there are several writers

**The rule.** When one store is edited from several places, save **the changed
field**, not the whole snapshot you read. Otherwise every writer overwrites
others' edits with its own stale copy.

## The incident

The same settings are changed from two places: the web interface and the
interactive menu. The usual sequence "read everything → change one thing → write
everything" breaks exactly between the first step and the third.

The web reads a snapshot. While the user is clicking a toggle, a neighbouring
setting is changed in the menu. The web writes **its** snapshot — and the
neighbouring setting reverts to its previous value. No error occurs: both
operations succeed, and the change simply disappears.

The fix: write one flag, not the snapshot. Then a concurrent edit to a
neighbouring field survives the write.

## Why

A snapshot is a claim about **all** the state at the moment of reading. Writing
it back, the writer asserts "everything was like this and still is" — and it
does not know that. The longer the gap between read and write (and with a human
in the middle it is long), the more often the assertion is false.

Writing a field is a claim only about what the writer actually changed. That is
always true.

A separate reason such losses are never found: they are **silent**. No error, no
conflict, no journal entry — the setting simply "reverted by itself". The
complaint arrives as "it keeps resetting on me", and reproducing it is hard.

## In practice

- writing a field is a distinct store operation, not "read, modify, write
  everything" under another name;
- the operation still takes a lock: simultaneous writes of **different** fields
  still rewrite the whole file;
- if fields are coupled and must change together, that is one transaction, not
  several field writes;
- a failed write must not break the response if the change has already been
  applied in the current operation's memory: the next launch will simply see the
  old value.

## Where it applies

**Works** for settings, profiles, configurations — anything edited from several
places with a human involved.

**Does not work** if the state is coherent by meaning and a partial write would
leave it contradictory.

**Sign of trouble:** complaints that "the setting resets itself", not
reproducible step by step.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/settings_adapter.py`,
#997. Related: [066](066-lock-the-companion-not-the-target.md).
