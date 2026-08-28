# A live document carries no work log

**Area.** documentation

**The rule.** A document describes how things work **now**. "What we did", "what
we plan" and "how it went" live in three other places.

## The incident

Traces of work were woven into feature descriptions: "it used to be like this,
changed in version such-and-such", "we plan to add", "this section appeared
after the audit".

Readers had to separate the current from the historical — and got it wrong. Some
descriptions referred to behaviour that no longer existed, yet looked current.

## Where things go

| What | Where |
|---|---|
| what works now | live documentation |
| what was done | the changelog |
| what is coming | the tracker |
| how it went | the archive |

## Why

Mixing time layers destroys documentation's main property — **being trustworthy
without checking the date**. If the text contains past and future, the reader
must verify every sentence against reality, and the document loses its purpose.

A frequent special case is **a task list inside a repository file**. It goes
stale within a sprint and starts lying: in the project examined, a document
listed long-closed tasks as open for years. The tracker is the only source of
statuses, and duplicating it into files is not allowed.

## Where it applies

**Works** for documentation describing a current state.

**Does not work** for documents whose genre is history: architecture decision
records (where the context of the decision is mandatory), changelogs, incident
write-ups. This catalogue is exactly such a case.

**A practical tell:** if a sentence starts with "previously", "now" or "we
plan", it is in the wrong file.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § what an active document
must not contain