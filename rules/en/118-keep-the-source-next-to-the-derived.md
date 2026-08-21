# Keep the source next to the derived

**The rule.** Anything produced by a transformation is accompanied by its source.
When the transformation rules change, the derived output is rebuilt **locally**,
without going back to the origin.

## The incident

A task statement was downloaded from the platform and saved in a readable form.
Under the markup extension, however, sat the original HTML — it had to be read
through tags and entities.

The fix added a conversion, but the important decision was different: **the source
was kept beside it**, as its own file. The reason is recorded plainly — the
conversion rules will change, and then the readable version is rebuilt locally
instead of requiring the tasks to be downloaded again.

Beside it, a second detail of the same order. Attachments that downloaded
successfully are rewritten to local names; anything that failed to download
**remains a network link**. The phrasing: promising a local file that does not
exist is worse.

## Why

A transformation is almost never final: the rules get refined, edge cases turn up,
requirements for the result change. Every such refinement requires **repeating the
transformation over all the material**, and the only question is whether there is
anything to repeat it from.

Without the source the only route is to go back to the external origin. That is
expensive, slow, quota-limited, requires access — and, most importantly, **may no
longer return the same thing**: the page changed, the task was withdrawn, the key
expired. So the absence of a source turns a refinement of the rules from a local
operation into an impossible one.

Second: the source is the only way to **verify the transformation**. A discrepancy
is analysed by comparing input and output; with only the output you cannot tell a
transformation error from a peculiarity of the origin.

## In practice

- the source sits beside the derived file and is **never edited**: what gets fixed
  is the transformation, not its input;
- the derived output has a rebuild command that runs from the local source, with
  no network;
- a partial result is honest: whatever could not be obtained remains a link to the
  origin rather than being replaced by an empty file with the right name;
- if the source is large, keep at least what makes the derived output
  reproducible: parameters, rule version, checksum.

## Where it applies

**Works** for imports, conversions, builds, caching of external data.

**Does not work** if the source contains what must not be stored (personal data,
secrets) — then keep the minimum sufficient for verification.

**Sign of trouble:** editing the transformation rules is postponed because "we
would have to download everything again".

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/use/grader-workflow.md` § about the two
statement files. Related:
[096](096-storage-follows-lifecycle-not-convenience.md).
