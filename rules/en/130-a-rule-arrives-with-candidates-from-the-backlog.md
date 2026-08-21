# A new rule arrives with candidates from the recipient's backlog

**Area.** catalogue, tracker

**The rule.** Delivering a rule is not enough. It arrives together with a **list
of candidates from the recipient's backlog** — open issues it may already answer.
A rule with no subject in your project stays an abstraction that gets postponed.

## The incident

Rule 128 ("a required field is checked for completeness, not for non-emptiness")
came out of a single issue. Rule 124 ("re-run the minimum, but green on the
second attempt is a finding") gathered **three trails**, and all three issues
**existed before the rule**: they were different symptoms of one cause.

A human connected them, at the moment of writing the rule, because he held the
backlog in his head. The neighbouring projects of the same owner had no such
person — and nobody looked for candidates there, although the rules apply to them
too.

The scale that puts this beyond attention: **59 open issues** in one project
alone. Nobody will re-read them for every new rule, and "this looks familiar"
only works for whoever filed them.

## Why

**A rule is adopted through its subject, not its wording.** "Useful thought, we
should keep it in mind" is a deferred refusal. "Here are three of your open
issues about exactly this" is work for tomorrow. The difference is not the
persuasiveness of the statement but whether it is attached to something that
exists.

**Candidates already exist wherever the rule applies.** A rule is born from an
incident, an incident repeats — so in a project where the subject exists, its
symptoms are almost certainly already filed, just not connected to each other.
That disconnectedness is exactly what hides the common cause: three issues about
different tests look like three flakes rather than one property of the system.

**A mechanism replaces memory precisely here.** Matching a rule against a backlog
is a cheap operation over data that already exists: the rule's area, the paths
and files from its trails, the words of its statement against the titles of open
issues. Computing it is cheap; remembering it is not.

## In practice

- a candidate is **a suggestion, not a link**: it is presented to a human and
  confirmed by them. Automatic linking creates false connections, and refuting
  them costs more than finding them
  ([086](086-the-finder-does-not-grade-the-finding.md),
  [051](051-warn-on-likely-block-on-certain.md));
- **a rejected candidate is remembered**, or the next pass offers it again and
  the list turns into noise
  ([026](026-rejected-findings-must-be-recorded.md),
  [087](087-a-second-pass-needs-a-novelty-rule.md));
- **an empty candidate list is an answer too**: the rule applies, there is no
  subject yet. That is not "unreviewed", and the difference is recorded
  ([027](027-empty-state-is-a-state.md));
- **the matching has two error types, priced differently**: a missed candidate
  leaves an issue unconnected, a spurious one spends attention. Tune the
  threshold towards missing, because humans read the list
  ([097](097-a-checker-has-two-error-types.md));
- it works **within** a single project too: a new rule is matched against its own
  backlog, not only against other people's.

## Where it applies

**Works** where the recipient keeps an open list of issues and rules arrive from
outside — from a shared catalogue, from a neighbouring team, from somebody else's
review.

**Does not work** with an empty or tiny backlog: there is nothing to match, and
the candidate list creates the appearance of work.

**Sign you need it:** a rule adopted a month ago gets its first issue only now —
and three similar ones turn out to have been open the whole time.

## Trace

ArtVsMark/claude-code-playbook#16; the mechanism is specified in #14, the
contract in #15. Rule 124 (three trails, connected by hand) and rule 128. See
also: [129](129-a-catalogue-needs-a-consumption-contract.md) — the delivery
contract; this record says **what exactly** is delivered along with a rule;
[019](019-audit-from-surfaces-not-files.md) — entering from surfaces;
[091](091-work-sources-are-ordered-first-non-empty-wins.md) — the order of work
sources.
