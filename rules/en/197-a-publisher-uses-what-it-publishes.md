# A publisher uses what it publishes for others

**Area.** contracts, process

**Tier.** 1 — rules and roles

**Portable beyond Claude Code.** yes — the subject is the relationship between a publisher and a consumer, not the workings of an agent session: a library with a schema, a service with an API contract and the owner of a shared pipeline all have it.

**The rule.** A requirement, a form or a number published for somebody else's
use is applied and checked **at home by the same mechanism** — or it is stated
why home is different. Anything published and not used by its publisher drifts
from practice silently: everything is green on the publisher's side because
there is nothing there to check, and the consumer is the first to notice.

## The incident

Three cases in two weeks, all at the publisher of a rules catalogue, and none
of them found by its own gates.

**The signature under a re-read, 8 September.** The catalogue requires of its
five consumers: the `answers_to` number goes in last, as a signature under
re-reading the answers, never instead of it. Its own commit bumped two
contracts and stamped itself the new number while touching **exactly one**
answer record — and that one only to describe a mechanism. A requirement sent
to five was applied to itself zero times.

**Asymmetric strictness, 10 September.** The `where` field in a consumer's
answer must carry a **resolvable address**: "a gate whose address cannot be
named usually is not a gate". The neighbouring `trail` field — a rule's own
trace at the publisher — was only checked for being non-empty. The price:
**12 records out of 195** reached consumers with an empty `trails` while
eleven of them named an address in the text. Seven were created by the
publisher's own record generator, whose refusal promised "a named artefact,
prose does not count" — and let prose through.

**Numbers published for comparison, 10 September.** The catalogue publishes
**six** contract numbers in the file consumers download, precisely so they can
compare them against their own. **One of the six** was compared. A bump of
`proposals` to 1.1 reached nobody: the consumer's file declares 1.0, and there
was no one to say so. In the same document the `contracts` example was typed
by hand and drifted so far it became a **physically impossible moment**:
`proposals: 1.1` alongside `export: 1.4`, when the former happened while the
latter was 1.7.

## Why

**A publisher gets no feedback from its own publication.** The consumer
receives the file and runs into it: a wrong form breaks their run, a stale
number breaks their answer. The publisher receives nothing — its build is
green because the subject of the check sits on somebody else's side. The
divergence exists from day one and has no observer.

**A requirement placed on others is a claim that it is both feasible and
useful.** Not applying it at home verifies neither. Both times the catalogue
turned its own requirement on itself, it immediately found a defect: an
overdue signature the first time, twelve records the second.

**Symmetry is cheaper than an audit.** A separate "do we do what we demand"
check is one more mechanism to remember, and it will go stale itself. One
predicate serving both directions cannot go stale by construction: it either
works for everyone or for nobody, and that shows at once.

## In practice

- one predicate for both directions, not "an equivalent one": two copies of a
  judgement diverge silently ([022](022-one-canonical-document.md));
- at home the requirement is held by **the same class of mechanism**:
  promising a gate and keeping a document for yourself restores the asymmetry
  under another name;
- a number published for comparison is **derived** at the publisher, never
  typed ([005](005-hand-written-numbers-rot.md)): otherwise it drifts first;
- "we do it differently because…" is a legitimate answer, but it is **written
  down**: a silent exception is indistinguishable from an oversight;
- the check of a requirement against your own practice hangs off **publication**,
  not off the calendar: contracts move rarely, and a monthly check goes stale
  between bumps.

## Where it applies

**Works** for anyone publishing a form, a requirement or a number for others
to compare against: a rules catalogue, a library with a schema, a service with
an API contract, the owner of a shared pipeline.

**Does not work** where the published subject is not reproducible at the
publisher: a requirement about an environment it does not have, a scale it
never reaches, a role its project does not contain. Symmetry is impossible
there, and the honest answer is to say so rather than fake a check against a
forgery.

**Does not work** for requirements that have no machine form at all: "the code
must be readable" cannot be applied at home by the same mechanism, because
nobody has one ([057](057-unmechanizable-rules-are-named-explicitly.md)).

**Sign of violation:** the requirement placed on a consumer is stricter than
the check of the same subject at home. A quick probe: take your most recent
contract and ask what happens if the publisher breaks it.

## Trace

ArtVsMark/Engineering-Incidents-Playbook — `scripts/check_reread.py`
§ Издатель освободил себя от требования.
ArtVsMark/Engineering-Incidents-Playbook — `scripts/sync_inbox.py`
§ СВОИ_КОНТРАКТЫ, the comparison of all three numbers describing consumer files.
ArtVsMark/Engineering-Incidents-Playbook — `scripts/build_rules_index.py`
§ CONTRACTS_MARKER_RE, contract numbers in the document rewritten by the build.

Related: [155](155-a-template-you-dont-use-drifts.md) — the same class for
boilerplate, and it refines this record: its subject is narrow, this one covers
any publication; [005](005-hand-written-numbers-rot.md) — numbers in
documentation; [142](142-a-scheduled-red-needs-an-addressee.md) — a finding
about somebody else's file has an addressee, and it is not the publisher.
