# Verify a finding's premise before working from it

**The rule.** A finding contains a claim about the current state. That claim is
verified as the first action — before planning, before the task, before code.

## The incident

An audit carried a finding: "there is no shared interface over the content
providers, we should introduce one". The wording read like an implementation
task, and it got as far as planning.

The premise turned out to be **factually wrong**: two such interfaces already
existed — two protocols with the same set of methods, each in its own module.
The real fork was not "introduce it or not" but "merge the two existing ones or
keep them separate", and the answer to that was the opposite of the original
proposal: **do not merge** until a third case appears.

The upshot: had the work been carried through as originally worded, it would
have introduced a redundant abstraction for the sake of two implementations —
and it would have been accepted, because the finding looked convincing.

## Why

A finding has two parts, and they are of different quality. **A claim of fact**
("there is no such thing", "this is duplicated", "this path is not covered") can
be verified in a minute. **A proposal** ("we should introduce it") is already a
decision, and it inherits the error of fact whole.

Checking early is cheaper for a simple reason: the further a finding travels,
the more scaffolding accumulates around it — an estimate, a priority, a plan —
and by review time its premise looks agreed simply because nobody challenged it.

Findings phrased as an **absence** are especially dangerous: "there is no X". An
absence is proved by exhaustive search but is usually established by searching
for one name — and anything named differently is not found.

## In practice

- the first step of work on a finding is **to reproduce the claim**, not to
  start fixing;
- a finding of the form "there is no X" is checked by searching for behaviour,
  not for a name;
- if the premise fails, the finding is not "minor" — it is **closed as
  incorrect**, with the reason recorded: otherwise it returns with the next
  audit;
- if a real fork was hiding under the wrong premise, it is raised afresh in its
  own words rather than by editing the old one.

## Where it applies

**Works** for audit findings, tool reports, other people's review comments.

**Does not work** where verifying the premise costs as much as the fix — then
fixing is cheaper.

**Sign of trouble:** the task describes a solution rather than an observation.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0010 § context ("the premise is factually
wrong"). Related: [026](026-rejected-findings-must-be-recorded.md),
[037](037-finding-status-depends-on-window.md).
