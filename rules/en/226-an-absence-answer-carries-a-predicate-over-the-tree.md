# An answer of "there is nothing here" carries a predicate over the tree that would make it false

**Area.** catalogue, gates

**Tier.** 1 — rules and roles

**The rule.** A negative answer — "there is nothing here", "not applicable" — is
a **claim about reality**, not a turn of phrase: it names a **predicate over the
tree** — a path, a name, a command — whose appearance makes the answer false,
and it is held exactly by whatever checks that predicate. A predicate refutable
by a single command with no network is run by a gate, not by a re-reading eye.
An answer for which no predicate can be written says so out loud and goes first
in the re-reading queue: its inapplicability rests on reasoning rather than on
the tree.

**Portable beyond Claude Code.** yes — the subject exists in any document that
answers "we don't have this" (a showcase, a project card, a coverage report),
and in any body of rules adopted in part with an answer recorded per item:
someone else's standard, an industry checklist, another team's rulebook.

## The incident

**A showcase that outlived two releases** (ArtVsMark/Claude-Code_Usage-Token#59,
admitted to the catalogue on 2026-09-03 as rule 175). A consumer's showcase
answered two of the set's questions like this: "there is nothing here: the
project has never been released, no release tag exists in the repository", and
"no distribution has been published, version 0.0.0".

By the time of the review the repository held the tags **v0.1.0 and v0.2.0**,
both with a created release and attached distribution files, and the version in
the tree read **0.2.0**. The answer had outlived **two releases** and had
sounded confident throughout.

The showcase gate was green and would have stayed green: it checks the
contract's **form** — that every question has exactly one answer and that the
stated reason is at least twenty characters — and it cannot check the truth of
free text by construction.

The lie was refutable by one command with no network: `git describe --tags`. A
subclass check was introduced: an answer beginning with "there is nothing here"
is compared against the tree. Measured on the real set — **one finding, exactly
that one**.

**A measurement over the catalogue registry's whole history (2026-09-17, 149
snapshots of `.rules/bindings.json`).** The verdict "not applicable" was
**refuted for twelve rules** — 001, 017, 033, 037, 050, 058, 085, 092, 101, 102,
137, 149. **Eight of the twelve are held by a GATE today.** That is, the answer
"this does not concern us" stood on something we then went and built by
machine. Transitions the other way: nineteen. The state is fluid; the verdict
was recorded as final.

**State on the day of the same measurement.** 29 records answer "not
applicable". They carry exactly three fields: `status`, `why`, `analysed`. Not
one carries a condition — neither `holdable` nor `awaiting`. A path, a file name
or a command appears in `why` for **five of the twenty-nine**; the other
**twenty-four** name nothing that can be run to yield a yes or a no.

**The neighbour's measurement, from which the proposal for 205 came**
(ArtVsMark/Engineering-Pipeline-Mechanisms, the same day). Answers changed from
"not applicable" to "active" — **twenty-two**, against fourteen live ones; that
is, more than half of every negative answer ever given turned out to be wrong.
Seventeen of the twenty-two were found across two days, once the re-reading
order became mechanical. Their cause is shared, and it is not staleness: **the
answer answered the wrong question**. Seven answers at once rested on one
premise, "the project runs no parallel executors" — while the review run starts
an agent four times over, and a command could have checked that on the day the
answer was written. Exactly one of the twenty-two was a fact going stale.

**Where the merge came from.** Proposed by the profile showcase
(ArtVsMark/ArtVsMark:merge/an-absence-answer-carries-a-predicate-over-the-tree):
there both rules are held by one function — `scripts/check_bindings.py::refuted`
(the `refuted_by` probe) and the ratchet on the queue without a probe,
`prose_budget`; on 9 October re-reading that queue found **10 wrong answers out
of 30** (ArtVsMark/ArtVsMark#322). Admitted in
ArtVsMark/Engineering-Incidents-Playbook#645, review —
ArtVsMark/Engineering-Incidents-Playbook#744.

## Why

**One failure from two ends.** 175 and 205 answered one question — how a
negative answer stays true — and split it in half: 205 demanded a predicate of
every such answer, 175 a gate on the subclass refutable by a single command.
Apart, the link was lost: a predicate without a gate is re-read by the same eye
that erred, and a gate without the demand for a predicate covers only the
answers their author happened to make checkable. The failure is the same for
both: a confident negative answer that no job reads.

**An empty field and a false claim are different states, and the second is
worse.** A gap is visible: people look for it, people ask about it. A confident
sentence looks like a **decision** — like work somebody has already done — and
therefore does not get re-read. It is worse even than an invented number: a
number at least invites re-checking, because a number has to come from
somewhere. The sentence "we have never released" owes nothing to anything.

**An event is not a predicate.** An event ("once we add a second language",
"once a second database appears") guards the answer against going stale: the
world changes, the answer gets revisited. It does not guard against the answer
having been wrong FROM THE START, and a misreading is the most common kind of
wrong "not applicable". Some of the neighbour's answers HAD an event set, and
it would never have fired, because what was wrong was the premise, not the
date.

**A predicate makes the answer refutable, not merely re-readable.** An answer
without one can only be re-read — by the same eye that erred the first time. An
answer with one is checked by a command, and anyone can run it, including
someone who has not read the rules. The subclass refutable by a single command
with no network is cheap enough to be run by a gate rather than by memory.

**[184](184-an-answer-of-not-applicable-is-split-in-two.md) says HOW to reach
the verdict; this rule says what the verdict must CARRY.** The neighbour's
measurement shows 184 can be satisfied and the answer still be wrong: the
premise was misread while the split was made in good faith. The catalogue's own
series says the same from the other side: 184 has been in force since
7 September, and twenty-four records out of twenty-nine still named nothing
checkable.

**An unwritable predicate is the finding itself.** If you cannot say WHAT would
have to appear in the tree, the inapplicability was deduced about the project
rather than read off it. That is not grounds to refuse the answer — it is
grounds to re-read it before the others.

**Two kinds of absence must be told apart** — without this boundary the gate is
removed at the first edit. "There is nothing here" is a claim that is either
true or false, and there is something to check it against. "We have no
indicator of our own" is a decision to show an existing subject through someone
else's source, and there is nothing to check it against. A gate that conflates
them goes red on a correct answer.

**The asymmetry of outcomes is deliberate:** the subject found while the answer
denies it — refuse; the subject not found — stay silent. In a cloud session's
shallow clone "there is no tag" means "we did not look", and red on that would
be false ([039](039-three-outcomes-not-two.md)).

## Practical boundaries

- the predicate names the TREE: a path, a name, a command, a tag, a file, an
  entry, a version — something you can run today and get a yes or a no. An
  intention, a plan or a role is not a predicate;
- a predicate refutable by a single command with no network is run by a gate;
  any other predicate need not be a gate — it is enough that a person can run it
  with one command;
- the predicate is phrased so that its firing makes the answer FALSE, not
  "worth a look": otherwise it is a reminder, not a check;
- the gate refuses in one direction only: a refutation found — red; none found —
  silence, because not knowing does not prove absence
  ([075](075-a-guard-that-finds-nothing-must-fail.md) reads inverted here: the
  subject of the check is the claim itself, and it is present);
- "there is nothing here" and "we have no indicator of our own" are different
  answers and are checked differently;
- an event remains a legitimate ADDITION to the predicate, never a substitute;
- an answer with no predicate says so out loud and goes first in the re-reading
  queue — silence here is the defect;
- THERE ARE TWO LEGITIMATE FORMS, not one: a predicate over the tree, or — where
  the inapplicability follows from the project's nature — a NAMED event with the
  reason the predicate degenerates there. An answer carrying neither is the
  violation. Demanding a predicate of everything forces a fake path where the
  second answer is the honest one;
- prose that does not reduce to an object stays prose: demanding a machine check
  of it would create a gate nothing can satisfy
  ([002](002-rule-without-mechanism.md)).

## Where it applies

**Works** where a document answers "we don't have this", or a body of rules is
adopted in part with an answer recorded per rule, and the project's tree can be
read by a command: the catalogue and its consumers, a showcase, someone else's
standard with a conformance map.

**Does not work** where the inapplicability follows from the project's NATURE
rather than from the state of its tree: "a rule about a mobile app, and there is
no app at all", "we have no review process", "we don't track satisfaction". A
predicate there degenerates into an event ("an app appears"), and it is more
honest to call it an event than to pass it off as a check; a gate has nothing
to check, and the rule collapses into ordinary editing. Such an answer is
legitimate — but the boundary is named, not stepped around. Nor does the gate
work in a shallow clone with no history: the command answers "no" to everything
there, and the gate would become a generator of false findings — which is
exactly why its refusal is one-sided.

**Sign of a violation:** a negative answer carrying NEITHER of the two
legitimate forms — no path, name or command that can be run, and no named event
with the reason the predicate degenerates; or a "there is nothing here" refutable
by one command with no network that no job reads. A missing predicate alone is
not the sign: an answer working under the boundary above legitimately has none.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Claude-Code_Usage-Token#59 — scripts/preflight.py, the subject check;
.rules/showcase.json, the release and distribution questions

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/bindings.json`,
`docs/decisions/030-the-answer-audit-stops-on-a-measured-yield.md`

Supersedes: [175](175-an-absence-claim-that-a-command-can-refute-must-be-a-gate.md),
[205](205-inapplicability-names-a-predicate-over-the-tree.md) — the demand for a
predicate on every negative answer and the gate on its subclass refutable by a
single command were recorded as two rules, while a consumer holds both with one
function; the old entries remain with a supersession mark
([043](043-decisions-are-superseded-not-edited.md)).

Related: [184](184-an-answer-of-not-applicable-is-split-in-two.md) — how to
reach the "not applicable" verdict; here, what the verdict must carry to be
refutable;
[182](182-an-unmechanisable-answer-is-split-in-two.md) — the same operation for
the answer "a machine cannot";
[154](154-none-must-name-its-reason.md) — "nothing" names its reason: the same
argument about silence, for a different state;
[146](146-a-green-gate-does-not-verify-its-premise.md) — green confirms itself;
an answer without a predicate confirms itself the same way;
[046](046-name-the-gaps-do-not-level-them.md) — name the gaps rather than
levelling them; here the naming of a gap goes stale too;
[002](002-rule-without-mechanism.md) — a rule with no mechanism is a
preference; the same holds for a claim with no check;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a guard with no subject
must fail.
