# Count unique names, not records

**The rule.** A counter that sums records about one object lies whenever the
object repeats. Collapse by identifier first.

## The incident

The front page claimed "32 checks per PR". Reality: sixteen.

```
PR #1294: 16 records, 16 unique names, no duplicates
PR #1293: 32 records, 16 unique names, duplicates: coverage-combine,
          test (windows-latest, 3.14, true), test (macos-latest, 3.12, false)…
```

After a branch update GitHub creates a **second set** of check runs while the
first stays attached to the old commit. `total_count` adds them together.

The only difference between the two pull requests was whether the branch had
been updated. Nothing was broken: the API returns exactly what exists.

## The second case, same root

The same walk classified checks with an empty `conclusion` as failures — and
recorded seven **in-progress** ones among them. It nearly raised a false alarm
about a red build.

Same class of cause: the field did not mean what was assumed. An empty
`conclusion` is "still running", not "failed".

## Why

The API returns a history of events, not a current state. There are as many
records of a check as there were runs of it; "how many checks does this pull
request have" is a question about **unique names**, not about the number of
records.

The error is quiet: the figure is plausible, nobody is surprised, and it lives
until a machine recomputes it.

## Where it applies

**Works** for any counter built over an event log: runs, delivery attempts,
retries, webhooks.

The generalisation: **before counting, ask what the unit actually is.** An event
or an object? The answer decides whether you need to collapse by key.

**Does not work** where repetitions matter in themselves: number of attempts,
retry counts — there you want every record.

## Trace

ArtVsMark/ArtVsMark#7
