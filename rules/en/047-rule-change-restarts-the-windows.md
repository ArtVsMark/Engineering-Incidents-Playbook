# Changing the working rules is a reason to restart the sessions, not to send a memo

**The rule.** If you changed the rules the sessions work by, restart the
sessions. Age has nothing to do with it: the rule changes by an event, while
context is read once, at startup.

## The incident

The transport to an external API was switched to the cheap one: the old way
burned quota, the new one did not. The rule was written into the project's main
file, the tooling grew to full coverage, the documentation was updated.
Everything was done correctly.

The quota kept burning. The cause was found in the dates: one session had
started **six days before** the change and was working to instructions current
at the moment of its launch. Sessions created later used the new way — so the
rule worked, but only for those born after it.

From outside this is indistinguishable from sabotage: the session does not
argue, does not complain, and confidently does it the old way.

## Why

Project rules reach a session **once** — when it reads them at startup. After
that the file may change as much as it likes: a running session keeps a snapshot
of the era it was born into.

Hence an asymmetry that is easy to miss: **editing a document affects future
sessions and does not affect current ones**. Writing a rule is half the work;
the other half is delivering it to those already working.

Simply saying it in the chat helps partly and unreliably: the instruction
competes with accumulated context where the same thing is written differently,
and it loses more often the older the session is. A restart removes the conflict
entirely.

## In practice

- a restart is mandatory if what changed was: transport and the way of reaching
  outside, prohibitions, role boundaries, merge order, artefact formats;
- it is unnecessary if only the content of tasks changed: the session re-reads
  those anyway;
- the order is **edit first, restart second**, otherwise the new session reads
  the old text again;
- the opening message of a new session names the changed rule explicitly instead
  of implying "it is in the file";
- while the sessions are not yet restarted, observed behaviour is compared
  **against the session's start date**, not against the date the rule changed —
  otherwise the diagnosis goes astray.

## Where it applies

**Works** for any agent that reads configuration or a rulebook at startup.

**Does not work** if the rules are re-read before every turn — then editing is
enough.

**Sign of trouble:** the new rule is followed by some sessions and not others,
and the boundary falls exactly on their creation dates.

## Trace

ArtVsMark/Stepik-Python-Grader#1283. Related:
[006](006-window-lifetime.md) — the same effect caused by age;
[002](002-rule-without-mechanism.md) — a rule without a mechanism.
