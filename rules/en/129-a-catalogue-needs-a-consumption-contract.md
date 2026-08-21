# A catalogue needs a consumption contract, not only an authoring order

**Area.** catalogue, contracts

**The rule.** An authoring order is not enough. A catalogue needs a **consumption
contract**: a machine-readable export, each consumer's answer about the fate of
every rule, a back-link into the originating issue, and a schema version. Without
one, shared knowledge stays in the project where it was born.

## The incident

The catalogue is kept impeccably: one unit, a number, mandatory sections, a
trail, a generated index. Three new rules landed in a day — all three born in one
project, out of its incidents.

The next morning's check produced three separate failures.

**The originating issues know nothing about the rules.** Rule 126 has a trail
pointing at one issue, 128 at another. The catalogue knows where they came from;
inside those issues there are either zero comments or a link to a closed
candidate.

**The other projects never heard of them.** The asymmetry is measurable: 121
trails for one project, 4 for the second, 1 for the third, 0 for the remaining
two. Five consumers — the knowledge reached one.

**The one hand-written back-link went stale within an hour.** A human put it into
the issue; the candidate closed, the rule got its number, and the link is
formally alive while pointing at an archived discussion rather than at the rule.

## Why

**"Has a trail" answers one question while three are being asked.** While there
is one project, "adopted here = has a trail from here" works. Once there are
several, **the absence of a trail merges three different states**: rejected
because we do it differently · no subject here · **never heard of it**. They
cannot be told apart in the catalogue or in the project — and the third is the
real loss, disguised as the first two.

**The "held by" level lives in the wrong repository.** The same rule is held by
**different** mechanisms in different projects: a CI gate where there is a full
pipeline, a build step in a storefront, nothing in a static site. The catalogue
does not know about other people's gates and should not. The measurement that
shows it: the index reports "83 rules active, 82 with no mechanism declared" —
the field is empty not because the gates are missing but because it was created
in the wrong place.

**A one-way link decays faster than it is written.** The rule → project direction
is held by the "Trail" field and survives. The issue → rule direction is held by
a person's memory and dies the day the intermediate thing — a candidate, a
discussion, a chat — is closed.

## What the contract contains

- **The export.** A machine-readable file: identifier, titles, area, trails
  **structurally** (`{repository, issue}`, not as a prose section) and a schema
  version. Published so it can be read over plain HTTP — no platform API, no
  clone, no credentials.
- **The consumer's answer.** A file in the project itself, one record per rule:
  status (active · rejected · no subject · unreviewed), what holds it **here**,
  where exactly, and a reason — mandatory for the two negative statuses
  ([026](026-rejected-findings-must-be-recorded.md)). It lives with the consumer
  because the mechanism lives there.
- **The back-link.** A rule whose trail points at an issue is reflected **in that
  issue** by one idempotent entry, written by the project with its own token. The
  catalogue needs no rights in anybody else's tracker.
- **The registry of consumers.** Who is connected, where their answer is read
  from, when it was last read. An empty registry is declared explicitly
  ([027](027-empty-state-is-a-state.md)), a lagging one warns by age
  ([079](079-ttl-counts-from-completion.md)), an unreachable answer from a
  registered consumer is a failure
  ([075](075-a-guard-that-finds-nothing-must-fail.md)), not silence.
- **One tool, and it belongs to the catalogue.** Not a copy of a script in every
  project: the stacks differ and the copies will drift
  ([090](090-shared-helpers-move-up-not-sideways.md)).

## Backward compatibility is part of the contract, not an appendix

Consumers update out of step, and that is a normal state rather than a fault:

- **the schema is versioned**, and the rules for its evolution are written where
  the schema is ([113](113-a-contract-states-how-it-may-change.md));
- **a reader of an old version does not break on new fields**: an unknown field
  is ignored, mandatory fields are never added retroactively;
- **migration starts from the current version, not from zero**
  ([114](114-migrate-from-the-current-version-not-from-zero.md));
- **a transitional shim gets an expiry date**, or it becomes permanent
  ([094](094-a-compatibility-shim-makes-migration-permanent.md));
- **breaking the format means breaking other people's projects**, including ones
  the catalogue's author does not know about. That is the reason to version it
  from day one rather than "when we need to".

## Openness: an outside participant is an ordinary consumer

- **public read only**: the mechanism must not require tokens into somebody
  else's repositories, or participation is limited to your own;
- **a foreign project's answer is untrusted data**: it enters the tables as a
  quotation, never as a command
  ([085](085-content-from-the-subject-is-untrusted-input-to-the-prompt.md));
- **the catalogue is not responsible for foreign mechanisms**: "it is held by a
  gate over there" is their claim, verified by their pipeline;
- **a private participant is not aggregated**, and its status reads "unknown",
  never "not adopted" ([046](046-name-the-gaps-do-not-level-them.md)).

## Where it applies

**Works** when there is more than one consumer: your own projects, other
people's, or one project and its forks.

**Does not work** for a catalogue with a single consumer — there the contract
costs more than the link itself, and the "Trail" field from
[120](120-how-to-run-a-rule-catalogue.md) is enough.

**Sign you need it:** a rule born in one project appears in none of the others,
and nobody can say whether it was rejected there or simply never seen.

## Trace

The mechanism is specified in ArtVsMark/claude-code-playbook#14, this record is
#15; the consumer role in the first project — ArtVsMark/Stepik-Python-Grader#1351.
Rules 126 and 128 are the ones that reached one project out of five. See also:
[120](120-how-to-run-a-rule-catalogue.md) — the authoring order this record
continues into consumption, refining it: "no trail" no longer means "not in
force"; [130](130-a-rule-arrives-with-candidates-from-the-backlog.md) — what
exactly is delivered along with a rule;
[080](080-every-new-rule-goes-into-the-catalogue.md) — the reverse flow;
[049](049-derive-state-from-live-artifacts.md) — why the links are computed;
[113](113-a-contract-states-how-it-may-change.md).
