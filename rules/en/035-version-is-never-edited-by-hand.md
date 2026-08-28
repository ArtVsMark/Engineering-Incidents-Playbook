# The version is never edited by hand, in any file

**Area.** release

**The rule.** The version is set in one place and substituted everywhere. Manual
editing produces a mismatch that surfaces after publication.

## The incident

The version lived in several places: package metadata, the output of
`--version`, the release tag, the documentation.

Mismatches appeared regularly and **were not caught by the usual checks**: the
code works, the tests are green, and the user sees one number in the package and
another in the program's output.

Worst of all, this surfaces **after publication**: a release is irreversible and
can only be corrected by the next release.

A dedicated consistency check was needed — and it started catching mismatches
before release.

## Why

A version is the classic value that **has to exist in several places** and has
to match. Maintaining that by hand is a matter of time, not of carefulness.

The usual gates miss it: a version mismatch breaks no test, because no test
knows which version is "correct".

Hence two requirements, not one:

- **one source** from which the version is substituted;
- **a consistency check** before release, in case the source multiplied anyway.

## Where it applies

**Works** for any project with a versioned artefact.

**Does not work** where the version is single and lives in one file — but that
state is unstable: the second location appears with the first external consumer.

**Generalises** to any value duplicated out of necessity: product name, service
URL, supported dependency versions. One source plus a check.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § versioning