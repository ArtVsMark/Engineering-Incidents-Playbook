# A mechanism is also subject to the rules on mechanisms

**Area.** gates

**Tier.** 3 — gates and processes

**The rule.** A gate, hook, run or skill built for one rule must also obey
the other rules on mechanisms: a deadline on a call, one implementation, the
floor interpreter, truncation with a count, the third outcome. This is held
not by the gates of those rules but by meta-gates, and each one's scope is
every mechanism in the tree: `scripts/`, `.claude/hooks/`, `.github/`. A scope
of "where the rule was born" will not do. A gate looks at its subject and not
at itself, so a violation inside a mechanism is seen neither by that gate nor
by the gate of the broken rule if its scope is narrower.

**Portable beyond Claude Code.** yes — any project that holds its rules with
its own check code writes that code by the same rules or not; an agent window
only makes mechanisms appear faster.

## The incident

**Repairing one rule brought back a violation of another** (the catalogue,
16 October 2026). The review of change #868 found under rule
[211](211-a-mechanism-is-alive-only-if-a-working-path-reaches-it.md): the
skill call log stayed silently empty when the window had no floor interpreter.
Fix #869 added a fallback system `python3` to the hook's wrapper. The review
of #869 found that a system 3.9 would fail on `datetime.UTC`, and #875 narrowed
the fallback to "3.11 or newer". Both changes passed **every** gate and were
merged. Both violated [217](217-a-version-move-is-done-in-the-code.md): the
window hook ran on something other than the floor interpreter — exactly the
first incident of 217 itself. The owner noticed it with a question: "doesn't
this contradict, given the project is on 3.14?". Removed in #877.

The style gate holding 217 checks which version the code is **written** for,
not what **runs** it. Both times the review looked at the rule the fix was
for — 211 — and not at its neighbours.

**An analysis of all the catalogue's mechanisms** (the same day,
ArtVsMark/Engineering-Incidents-Playbook#879; 84 scripts, 50 of them gates,
and `.claude/hooks/`). The requirements on a mechanism itself were listed from
the rules on mechanisms, and for each it was checked whether a meta-gate
covers all scripts. Most are held: 214, 211, 176, 165, 158, 159, 140, 212, 001,
040, the style half of 217; file reads without an encoding and bare `except:`
— zero. Three violations were found **inside the gates themselves**:

- **46 subprocess calls without a deadline**
  ([100](100-two-deadlines-start-and-work.md)) — in `check_gates.py`,
  `check_attribution.py`, `check_facts.py` and others. The catalogue's answer
  to 100 named only the CI runs' `timeout-minutes`, so the meta-gate's scope
  was narrower than the rule;
- **one shell-parsing function in two gates**
  ([214](214-one-territory-one-parse.md)) — `check_workflows.py` and
  `check_paging.py`. The `check_copies` meta-gate catches copies of regular
  expressions, not of functions;
- **a list of removed items cut at 12 without a count**
  ([016](016-no-silent-truncation.md)) — `check_narrowing.py`.

## Why

**A gate is built for its subject, not for itself.** Whoever writes a gate
thinks about what it must catch and checks that with a rejection test
([140](140-a-gate-is-tested-by-what-it-must-reject.md)). The requirements on
the gate's own code — deadline, encoding, third outcome — are background at
that moment, not the subject, and they hold only because someone built a
separate check for them **with a scope that includes this gate**.

**A meta-gate's scope grows from where the rule was born, not from its
subject.** Rule 100 was born on a hung CI job — and its meta-gate looks at
runs. Rule 217 was born on code style — and its meta-gate looks at style. The
code of gates and hooks did not fall into that scope by decision, but because
the incident happened elsewhere. From outside, an answer "held by a gate"
looks the same for a full scope and a partial one
([182](182-an-unmechanisable-answer-is-split-in-two.md)).

**A fix is the most dangerous place.** It is written quickly, for one rule,
under a review that looks at that rule. The second incident of 217 was born
exactly so: 211 was being repaired.

The asymmetry of cost: checking scope costs one list "rule → meta-gate →
scope". A violation inside a mechanism costs more than the same one in
ordinary code: a mechanism is what people trust, and its green is read as
proof.

## Practical boundaries

- for every rule on mechanisms the meta-gate and its scope are named; the
  scope is every mechanism in the tree, not only where the rule was born;
- an answer "held by a gate" is checked against that gate's scope: does it
  hold the requirement in all mechanisms or in a part
  ([182](182-an-unmechanisable-answer-is-split-in-two.md));
- a fix to a mechanism is checked not only against the rule it is for but
  against the rules on mechanisms: which interpreter, which deadline, is there
  a second implementation, is anything cut silently;
- requirements held only by judgement are easy to miss
  ([070](070-a-heuristic-guard-fails-open-with-a-written-risk.md),
  [084](084-best-effort-channels-never-block-the-main-path.md)): they have no
  meta-gate by construction and are reread by eye when a mechanism is
  reviewed;
- the decision is revisited if the rules on mechanisms become too many for the
  "rule → meta-gate" list to be read at a glance: then the list becomes data,
  and a gate checks its completeness.

## Where it applies

**Works** in a project that holds its rules with its own check code: gates,
window hooks, runs, skills.

**Does not work** for checks taken whole from another project and pinned by a
tag: their owner edits that code and holds it to the rules
([162](162-a-gap-asks-the-neighbours-first.md) — report what was found to
them). Nor for rules on content (record texts, contracts): their subject is
not a mechanism.

**Sign of a violation:** a rule on mechanisms is answered "held by a gate",
while measuring its predicate over `scripts/`, `.claude/hooks/` and
`.github/` finds violations in the gates themselves.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#879

Related: [197](197-a-publisher-uses-what-it-publishes.md) — a publisher
applies to itself what it hands out; this is narrower: a mechanism obeys the
rules on mechanisms even if it is given to no one.
[182](182-an-unmechanisable-answer-is-split-in-two.md) — an answer about half
a requirement; this is the path by which the gap in 100 stayed invisible.
[146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate does not
confirm its premise; here a green gate does not confirm its own code either.
[162](162-a-gap-asks-the-neighbours-first.md) — ask the family before
building; Token already had a meta-gate for the deadline —
`scripts/subprocess_timeout.py` in ArtVsMark/Claude-Code_Usage-Token at
`52efb3a`, and the catalogue took its technique into
`scripts/check_subprocess.py` (the catalogue's answer to 100, field `origin`).
