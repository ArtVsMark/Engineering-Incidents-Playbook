# An answer of "no machine can check this" is split in two before it is believed

**Area.** catalogue, gates

**Tier.** 1 — rules and roles

**The rule.** Before writing down "no mechanism, this needs judgement", take the
requirement apart and ask each piece separately: which part genuinely needs
understanding (or a resource we do not have), and which part follows from the
data alone. The second half is almost always there, and a machine holds it.
Refusing wholesale refuses that half too — and with it the only thing that was
within reach.

**Portable beyond Claude Code.** yes — the subject belongs to any register where
"this cannot be automated" gets written down: technical debt, a risk register, a
list of manual checks.

## The incident

The catalogue, 4 September. Three rules stood **declared active and held by
nothing**, and each carried an honest, detailed answer explaining why no
mechanism was possible. All three turned out to be closable in one pass.

| Rule | What the answer said — and it is true | What followed from the data alone | Measured |
|---|---|---|---|
| 158 | "you cannot tell cause from subject in prose by parsing" | is the subject **named at all**: an interpolation or a literal address | 19 nameless third outcomes out of 43 |
| 170 | "there is nothing to compare forgeries against right now" | is the **address** named, the one you would compare against: no network needed | source named in 1 test module out of 6 |
| 144 | "a gate would catch legitimate cases more often than violations" | did the **author say** what is being cut: a module path or prose | 4 cuts, none declared |

None of the three answers was a lie or laziness. Each is correct — about its own
half.

**What was tried first.** Nothing: the answers were taken as given for months.
The "held by nothing" number was read as a measure of difficulty — "that is how
much of this is inherently non-mechanical" — and so it did not go down. The
review began only after the owner demanded that debt be closed before new work
(177).

## Why

A requirement is a **conjunction**, and the answer is written looking at it as a
whole. If any one part needs judgement, the whole answer reads "needs judgement":
it is true of the conjunction and false of each part taken alone.

Then the thing that makes the error long-lived kicks in: **an honest answer is
not re-examined**. A lie invites checking; half a truth does not — it looks like
analysis, and the next reader inherits the conclusion together with trust in it.
This is the same self-sealing verdict as in
[178](178-a-source-mismatch-is-your-reader-until-proven-otherwise.md), except
that here the expensive explanation is not about the data but about one's own
capabilities.

The easy half almost always has one shape, and that is worth remembering: **the
machine holds not the judgement but the fact that the question was asked**. The
gate does not decide whether this is prose or a path — it requires the author to
say. It does not decide whether a forgery's source is right — it requires the
source to be named. In this catalogue that pattern holds `check_skips.py`,
`check_duplicates.py`, `check_forgeries.py`, `check_text_cuts.py` and
`check_exclusive.py`.

**The asymmetry of price.** Refusing to build costs nothing today and accrues
debt that reads as impossibility. Splitting in two costs one pass and almost
always yields a mechanism. Erring towards the split is cheap: if no half was
found, you write down the same answer, now verified.

## Practical boundaries

- before writing "no mechanism", write the requirement out in parts and mark each
  one: machine or human;
- easy to miss that the easy half is usually **not a check but a duty to
  declare**: "name the address", "name the subject", "say what you are cutting";
- easy to miss that **the honest answer is the dangerous one**: it does not
  invite re-examination, because it does not look like a brush-off;
- revisit the decision when the split yields a machine half that **requires no
  edit anywhere in the tree and would find nothing**. That is a gate holding
  nothing ([146](146-a-green-gate-does-not-verify-its-premise.md)), and then "no
  mechanism" is the right answer. That is how it went with 139 here: 103 answers
  claim `mechanism: gate`, 4 point at something non-executable, and all four are
  legitimate.

## Where it applies

**Works** for any register where "this cannot be automated" is written down:
a catalogue's answers about its rules, technical debt, a risk register, a list of
manual checks.

**Does not work** for an atomic requirement: with no parts there is nothing to
split, and the answer is simply right or wrong. Nor does it work where the
missing resource blocks both halves — for instance both need a key we do not
have: then the obstacle is single and already named, as with 105.

**Sign of violation:** an answer of "no mechanism" that names **one** obstacle for
the **whole** requirement and does not say which part of it is mechanical anyway.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#148 — the 4 September handover, where all
three cases are written down with numbers; the reviews themselves live in
`.rules/bindings.json` under rules 158, 170 and 144. The mechanism is the
`machine_half` field on `mechanism: none` answers, held by
`scripts/check_bindings.py`.

Related: [057](057-unmechanizable-rules-are-named-explicitly.md) — a rule that
cannot be machine-checked says so explicitly; 182 demands the next step: say
WHAT exactly cannot, and what can.
[146](146-a-green-gate-does-not-verify-its-premise.md) — the lower bound: a half
that requires no edit anywhere is not a mechanism.
[177](177-unfinished-rule-work-comes-first.md) — the queue in which those three
answers stood for months, because the number read as difficulty.
