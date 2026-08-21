# A link to a task belongs in a log and hurts in an explanation

**The rule.** An issue number is a date stamp. Logs need it; text explaining how
something works is worse for it.

## The incident

Issue numbers spread across the documentation. Sentences like "a fixed
dictionary of tags instead of a predicate language — a simplification (issue
NNN)" appeared in descriptions of how the system is built.

A reader who came to understand the design got a link to a three-year-old
discussion instead of an answer. And the link itself lost meaning over time: the
context of the task was forgotten faster than the code changed.

## Zone by zone

| Where | Number | Why |
|---|---|---|
| changelog, archive | **required** | it is a log: the number is the link to the change |
| reviews, audits | appropriate | findings are tied to tasks by nature |
| architecture decisions | appropriate in the "context" section | the task is part of the answer to "why we decided so" |
| design documents | only as a **requirement identifier** | other documents and code refer to it |
| working notes for automation | minimal | pointers only |
| **"how it works" documentation** | **none** | it answers "how now", not "when it appeared" |

## How to rewrite when the number feels necessary

Rephrase so that the **trade-off** is explained rather than the decision dated.

Before: "a fixed dictionary instead of a predicate language — a simplification
(issue NNN)".

After: "a fixed dictionary instead of a predicate language — a deliberate
simplification: predicates buy flexibility at the price of being unverifiable".

The second answers the reader's question. The first sends them off to read
correspondence.

## The mechanism

The rule is mechanical: a check holds explanatory documents at zero links, and
gives the zones with a permissible "tail" a **budget**.

The key detail: **budgets only go down, never up**. Growth means the log has
crept back into explanatory text. A threshold you can raise when it becomes
inconvenient protects nothing.

## Where it applies

**Works** for projects that have a tracker and documentation at the same time.

**Does not work** in projects where the documentation is the tracker.

**The generalisation carries over:** a "budget that only goes down" suits any
gradual cleanup — file size, number of linter exceptions, count of skipped
tests.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § links to issues
