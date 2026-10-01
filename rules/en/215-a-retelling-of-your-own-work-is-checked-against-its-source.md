# An account of the work you have just done is checked against its source, not written from memory

**Area.** process

**Tier.** 3 — gates and processes

**The rule.** Text about the work you have just done — a change's body, a
changelog fragment, a comment above the edit, the `why` field of an answer —
is written from a source taken at that moment: the diff against the main
branch, the findings issue, the commit body, the output of a named command.
A number, a list or "what was touched" is taken by a command when the text is
written, not recalled. When a list has a canonical home, the text links to it
instead of typing out a copy.

**Portable beyond Claude Code.** yes — every author who describes their own
change has this subject: a PR description, release notes, a decision record.

## The incident

**The neighbour's measurement, which the proposal came from** (the mechanisms
project, 30.09.2026). Its registry of finding kinds has a kind called "an
account of your own work not checked against its source". Between 23 and 30
September that kind came up 17 times across 8 changes. The source of these
numbers is the "met" field of that kind in the neighbour's
`.rules/finding-kinds.json` at the merge of
ArtVsMark/Engineering-Pipeline-Mechanisms#966, and the fingerprint of each
occurrence sits in the reviewer's comment on the named change. Of the 11 occurrences
on the last five changes, eight were in the very text of the incident about
this kind and in the fragment that went with it: a copy of the canon, typed
from memory into a neighbouring file, drifted from the canon at the very next
edit.

**Here this kind sits on a third of the changes with findings.** Measured on
01.10 over the outside reviewer's comments on changes from 10 to 27 September:
at least one finding other than `НАХОДКА: нет` sits on 92 changes. The command
counts changes, not comments, takes only the reviewer's comments created
before 28.09, and returns 92:

```bash
gh api --paginate 'repos/ArtVsMark/Engineering-Incidents-Playbook/issues/comments?since=2026-09-10T00:00:00Z&per_page=100' \
  --jq '.[] | select(.user.login == "claude[bot]" and .created_at < "2026-09-28")
        | select([.body | scan("НАХОДКА:[^\n]*")]
                 | map(select(test("^НАХОДКА:\\s*нет\\W*$") | not)) | length > 0)
        | .issue_url' | sort -u | wc -l
```

On **34** of them at least one finding is text about that same change's work
which the change itself refutes. The classification is a manual reading, and
the numbers are listed in `.rules/bindings.json`, entry 215, field `why`. Typical cases:

- #590 — the fragment says "7 calls" for the command it quotes, and the same
  command on the same branch returns 9;
- #574 — the entry says 37 links, the tree has 36;
- #511 — the change's body was not recounted after the fragment: "third and
  fourteen" in the body against the corrected "first and sixteen" in the file;
- #629 — a comment claims `main-red.yml` does NOT exclude `release`, while the
  same change makes it exclude it;
- #631 — the body says "two findings" but clears three `Разобрано:` lines, and
  the third is not explained (entry `750b30c` in the findings issue).

**What did not work.** The outside review does catch these, but late: each
occurrence costs one more review pass and one more change. Fixing the finding
once is not enough either: in #527 and #528 the fragment's body was narrowed,
while its heading kept the refuted "after every merge" — the account was
edited without checking it against what the author had just corrected.

## Why

**An author does not check what they did themselves — because they are sure.**
Someone else's claim gets checked out of habit. Your own, made five minutes
ago, feels known, and the source stays closed, even though it lives on the
same branch and answers in one command. The error comes not from ignorance
but from the work having changed after the author memorised it: a second
commit, a self-correction, a dropped item.

**The cost is asymmetric.** Checking costs one command at the moment of
writing. Skipping it costs a review pass, a fixing change and — if the finding
is missed — wrong text in the changelog that no one will read again:
[030](030-changelog-from-fragments.md) assembles fragments at release time as
they are.

**A copy of the canon is the same error, postponed by one edit.** A list typed
next to its canon is right on the day it is written and drifts at the canon's
first edit. A link never drifts.

## In practice

- a number in text about your own work is taken by a command, and the command
  is named next to it or in the fragment, so the number can be rechecked;
- before a push, the body and the fragment are reread against `git diff --stat
  origin/main`, and against the findings issue if the body clears entries;
- after a self-correction in a second commit, every place that carried the
  corrected item is recounted: the body, the fragment, `why`, the fragment's
  heading;
- a list with a canonical home gets a link to it and a dated measurement, not
  a copy.

## Where it applies

**Works** for claims about this same change's work — a number, a list, "what
was touched" and "what was done" — wherever they stand: the body, a changelog
fragment, a comment above the edit, the `why` field of a rule answer, a
decision record about your own check.

**Does not work** for claims about others: a neighbour, the platform, someone
else's calendar. There the source belongs to someone else and the check is
different — [190](190-a-consumers-answer-about-a-neighbour-is-asked-not-remembered.md),
[203](203-experimental-is-a-claim-about-someone-elses-calendar.md). **Does not
work** for a claim about a mechanism that a machine can check against the
code either: that is [183](183-a-claim-about-the-mechanism-is-checked-against-it.md),
held by a gate, not by a practice. **Does not work** for an argument — the
explanation of WHY it was decided so — even inside the same `why` field: an
argument claims nothing about what the change contains, and there is nothing
to take by a command. The field splits by meaning: numbers and lists in it are
checked, the argument next to them is not.

**Sign of a violation:** a number, a list or "what was touched" in text about
your own work with no command named next to it, which disagrees with that
command's output on the same branch.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — .rules/finding-kinds.json

Related: [105](105-an-outside-audit-needs-outside-eyes.md) — an outside look
catches what the author does not see; this rule removes one kind
of its findings before review; [209](209-a-constant-is-quoted-by-reference-not-respelled.md)
— a copy of a constant in code; here, a copy of a list in prose;
[030](030-changelog-from-fragments.md) — a fragment travels with its change,
so its accuracy is checked in that same change.
