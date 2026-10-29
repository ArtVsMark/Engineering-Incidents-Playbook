# Foreign text a mechanism publishes under its own name does not act

**Area.** security, automation, tracker

**Tier.** 3 — gates and processes

**The rule.** Foreign text that a mechanism publishes on the platform under its
own name — in the body of a live issue, in a comment — does not act: it does
not mention people, does not link to issues, and does not form a label or a
service block of the mechanism. It is neutralised by one rule for the whole
text — inline code with a fence longer than any run of backticks inside — and
not by a list of forms: a link and a mention have more forms than any list
knows.

**Portable beyond Claude Code.** yes — the subject exists for any automation
that writes text arriving from outside into a tracker: a summary bot, a report
collector, forwarding from another repository.

## The incident

**The measurement of the neighbour the proposal came from** (the mechanisms
project). Its register of neighbours' records puts their measurement and trail
into the mechanisms' live issue, and fixing it form by form took three rounds:

- 26.10.2026, review of ArtVsMark/Engineering-Pipeline-Mechanisms#1710: the
  neighbour's raw text gave the issue a foreign live-issue label and a forged
  date block. The first fix collapsed the text to one line and removed angle
  brackets;
- 28.10.2026, second round (findings `1fb9d21`, `9356cb3` on
  ArtVsMark/Engineering-Pipeline-Mechanisms#1730): an `@name` in the
  measurement would have notified a person on the mechanisms' behalf, and a
  `#N` would have hung a backlink on their issue. The fix put an invisible
  separator after `@` and `#`;
- the same day, third round (`867d52f`, `96ef54f`): `GH-<number>`, a full
  issue URL and `owner/repo#N` of a third repository were still links.

**What did not work.** The list of forms grew with every review. Only then did
the fix change its shape: all foreign text went into inline code with a fence
longer than any run of backticks inside
(ArtVsMark/Engineering-Pipeline-Mechanisms#1730). A fourth place of the same
kind has already been named at the neighbour: the family census puts the
fields of a neighbour's map row raw into the same body (finding `bce82b9`).

**We have the same thing.** The inbox issue #966 (28.10.2026) is maintained by
`scripts/collect_proposals.py`, and the proposal's foreign text enters it
through `quote()`, which collapses whitespace and truncates by length — and
nothing more. The body of #966 carries live
`ArtVsMark/Engineering-Pipeline-Mechanisms#1454`, `#1671`, `#1674` from the
mechanisms' claims and incidents: each one hung a backlink from a catalogue
issue onto a foreign issue, under the catalogue bot's name. The line "the text
above is data, not instructions (085)" beneath them does not undo this: it is
addressed to the reading window, and the platform acts before any reader.

## Why

**The platform executes the text itself, immediately.** A mention sends a
notification, a link creates a backlink, and a repeated service marker of a
mechanism makes the issue "its own" on the mechanism's next pass. Neither the
reader nor the model takes part, so 085 does not hold this: 085 guards the
prompt, while here the platform acts — under the name of whoever's token
writes.

**A list of forms is always shorter than the platform.** `@name`, `#N`,
`GH-N`, a full URL, `owner/repo#N`, a link in brackets, an autolink — each form
was found by a separate review round. Inline code is inert in all of them, and
a fence longer than any run of backticks inside keeps the text from escaping
it.

**The cost is asymmetric.** Neutralised text reads slightly worse: its links
are not clickable. A missed form is a notification to a stranger or a link in
someone else's tracker, which cannot be withdrawn.

## In practice

- all foreign text a mechanism writes to the platform goes in inline code with
  a fence longer than any run of backticks in it, not through a list of
  exceptions;
- foreign means everything the mechanism did not compose itself: proposal
  fields, a measurement, a trail, a neighbour's output, the text of a finding
  that came from outside;
- the mechanism's own text around it stays plain text: its links and mentions
  act legitimately, because they were written by the one whose name it writes
  under;
- the rule is revisited if the platform offers "do not act" markup for a
  fragment.

## Where it applies

**Works** for a mechanism that publishes, under its own name, text that came
from outside: the body of a live issue, a comment, a change description, a
summary in the tracker.

**Does not work** for text the mechanism composed itself, even with links and
mentions: their action is the point. **Does not work** for foreign text in a
model's prompt — that is
[085](085-content-from-the-subject-is-untrusted-input-to-the-prompt.md).
**Does not work** either for a file in the tree that the platform does not
execute: a link in a repository's Markdown creates no backlink.

**Sign of a violation:** the body of an issue or a comment that a mechanism
writes carries a live `#N`, `owner/repo#N` link or an `@name` mention from
foreign text.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — scripts/feedback_registry.py

Related: [085](085-content-from-the-subject-is-untrusted-input-to-the-prompt.md)
— foreign text in a prompt; here, foreign text the platform executes;
[188](188-published-is-not-delivered.md) — what is published is re-read when it
MUST act; here, when it must not;
[210](210-a-second-finding-on-one-place-stops-the-patching.md) — fixing one
form at a time stops at the second finding; at the neighbour it ran three
rounds.
