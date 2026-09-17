# An answer of not-applicable names a predicate over the tree, not an event

**Area.** catalogue, gates

**Tier.** 1 — rules and roles

**The rule.** An answer of "not applicable" names a **predicate over the tree**:
what exactly would have to appear in it for the answer to become false — and that
predicate must be **checkable by a command today**. A named event is not enough:
an event guards against going stale, it does not guard against a misreading, and
a misreading is the most common kind of wrong "not applicable". A predicate you
cannot write is itself a finding: it means the inapplicability rests on reasoning
rather than on the tree.

**Portable beyond Claude Code.** yes — the subject exists in any body of rules
adopted in part, with an answer recorded per item: someone else's standard, an
industry checklist, another team's rulebook.

## The incident

**A measurement over our registry's whole history (2026-09-17, 149 snapshots of
`.rules/bindings.json`):** the verdict "not applicable" was **refuted for twelve
rules** — 001, 017, 033, 037, 050, 058, 085, 092, 101, 102, 137, 149. **Eight of
the twelve are held by a GATE today.** That is, the answer "this does not concern
us" stood on something we then went and built by machine. Transitions the other
way: nineteen. The state is fluid; the verdict was recorded as final.

**State on the day of the measurement:** 29 records answer "not applicable".
They carry exactly three fields: `status`, `why`, `analysed`. Not one carries a
condition — neither `holdable` nor `awaiting`. A path, a file name or a command
appears in `why` for **five of the twenty-nine**; the other **twenty-four** name
nothing that can be run to yield a yes or a no.

**The neighbour's measurement, from which the proposal came** (the mechanisms
project, the same day): answers changed from "not applicable" to "active" —
**twenty-two**, against fourteen live ones; that is, more than half of every
negative answer ever given turned out to be wrong. Seventeen of the twenty-two
were found across two days, once the re-reading order became mechanical. Their
cause is shared, and it is not staleness: **the answer answered the wrong
question**. Seven answers at once rested on one premise, "the project runs no
parallel executors" — while the review run starts an agent four times over, and a
command could have checked that on the day the answer was written. Exactly one of
the twenty-two was a fact going stale.

## Why

**184 says HOW to reach the verdict; this rule says what the verdict must
CARRY.** Rule 184 requires splitting a rule into its letter and its
generalisation and answering "no" only when both are absent. That is about
thinking at the moment of answering. But the neighbour's measurement shows 184
can be satisfied and the answer still be wrong: the premise was misread while the
split was made in good faith. Our own series says the same from the other side:
184 has been in force since 7 September, and twenty-four records out of
twenty-nine still name nothing checkable.

**An event is not a predicate.** An event ("once we add a second language",
"once a second database appears") guards the answer against going stale: the
world changes, the answer gets revisited. It does not guard against the answer
having been wrong FROM THE START. Some of the neighbour's answers HAD an event
set, and it would never have fired, because what was wrong was the premise, not
the date.

**A predicate makes the answer refutable, not merely re-readable.** An answer
without one can only be re-read — by the same eye that erred the first time. An
answer with one is checked by a command, and anyone can run it, including someone
who has not read the rules.

**An unwritable predicate is the finding itself.** If you cannot say WHAT would
have to appear in the tree, the inapplicability was deduced about the project
rather than read off it. That is not grounds to refuse the answer — it is grounds
to re-read it before the others.

## Practical limits

- the predicate names the TREE: a path, a name, a command — something you can run
  today and get a yes or a no. An intention, a plan or a role is not a predicate;
- the predicate need not be a gate: it is enough that a person can run it with
  one command. A gate is the next step, not a condition of the answer;
- an event remains a legitimate ADDITION to the predicate, never a substitute;
- the predicate is phrased so that its firing makes the answer FALSE, not
  "worth a look": otherwise it is a reminder, not a check;
- an answer with no predicate says so out loud and goes first in the re-reading
  queue — silence here is the defect.

## Where it applies

**Works** where a body of rules is adopted in part with an answer recorded per
rule, and the project's tree can be read by a command: the catalogue and its
consumers, someone else's standard with a conformance map.

**Does not work** where the inapplicability follows from the project's NATURE
rather than from the state of its tree: "a rule about a mobile app, and there is
no app at all". A predicate there degenerates into an event ("an app appears"),
and it is more honest to call it an event than to pass it off as a check. Such an
answer is legitimate — but the boundary is named, not stepped around.

**Sign of violation:** an answer of "not applicable" with no path, no name and no
command in it — nothing that can be run to yield a yes or a no.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/bindings.json`,
`docs/decisions/030-the-answer-audit-stops-on-a-measured-yield.md`

Related: [184](184-an-answer-of-not-applicable-is-split-in-two.md) — how to reach
the "not applicable" verdict; here, what the verdict must carry to be refutable;
[182](182-an-unmechanisable-answer-is-split-in-two.md) — the same operation for
the answer "a machine cannot";
[154](154-none-must-name-its-reason.md) — "nothing" names its reason: the same
argument about silence, for a different state;
[146](146-a-green-gate-does-not-verify-its-premise.md) — green confirms itself;
an answer without a predicate confirms itself the same way.
