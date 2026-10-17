# A requirement is held by a mechanism, and what nothing holds is named explicitly with a reason

**Area.** process, CI

**Tier.** 2 — the pipeline and CI

**The rule.** A requirement is held by a machine: a gate or an executable step
that cannot be forgotten because it runs. What no machine holds is written
down explicitly as held by nothing — with a reason established by trying to
build a mechanism, not by declaring it. A requirement with neither a mechanism
nor such a record is a promise: it will not be followed, and from outside
nobody can see that.

**Portable beyond Claude Code.** yes — people and agents skip a step they have
to remember in exactly the same way, and a rulebook left with only checkable
rules teaches the wrong thing to any reader; neither the incidents nor the
mechanism depend on an agent window.

## The incident

**Nine incidents out of eleven were skipping, not ignorance**
(Stepik-Python-Grader; trace ArtVsMark/Stepik-Python-Grader#1296,
ArtVsMark/Stepik-Python-Grader#1329). A review of one working session: **nine
incidents out of eleven were not ignorance of a rule but skipping it**. The
telling case: the requirement to run the full test suite had been written into
the project's rules long before a filtered selection silently broke somebody
else's test. The rule was known. The rule was written down. It was skipped.
The conclusion drawn then: a checklist gets **rewritten into a command**, not
extended with one more item — `preflight.py` before committing,
`check_pr_ready.py` before merging.

**A public claim that nothing verifies** (Stepik-Python-Grader, the same
trace). The project's front page stated that the list of branch-protection
bypasses was empty — and nothing verified it. Such a list grows by one click
for an urgent fix and never shrinks back; the build stays green while the
guarantee quietly stops existing. **A public claim about quality that nothing
verifies is a promise.**

**Three breakages no gate catches** (Stepik-Python-Grader,
`docs/agent/preflight.md` § Что гейты не ловят). A review of one session left
three breakages, none of which any automatic check catches:

- **pushing into somebody else's branch** — the gate sees a matching branch
  name, not an intention;
- **code with escapes written through inline shell text** — a newline escape
  turned into a real newline twice, and the file broke before it ever ran;
- **"the test goes red without the fix", proved by reverting the whole source
  tree** — the tests failed on an import error, so all that was proved was "the
  test references the new code".

The temptation: if it cannot be checked, why write it down — "it is obvious
anyway". Each of those three breakages happened to people to whom it was
obvious anyway. So they were gathered into a section with an honest heading:
**what the gates miss — and why this is written here**.

**Where the merge came from.** Proposal
ArtVsMark/Engineering-Pipeline-Mechanisms:merge/a-rule-is-held-by-a-mechanism-or-named-unheld,
issue ArtVsMark/Engineering-Incidents-Playbook#645. The signal: in the export
057 refines 002, while their prescriptions are opposite: 002 sends what cannot
be expressed mechanically to review ("should not pretend to be rules"), 057
says to write it into its own section, marked as having no gate and saying
why; a reader of both numbers got two answers to one question. In the review
ArtVsMark/Engineering-Incidents-Playbook#744 (8 October) the catalogue had
earlier called the pair neighbours on question 1, reading 002 as a rule about
skipping a written step, whereas its letter "either build a gate, or do not
write it down" speaks of a requirement without a mechanism — on 17 October
2026 the owner accepted the merge.

## Why

**One cause: a requirement without a mechanism is not followed, and this is
not visible.** People and agents skip a step you have to remember in exactly
the same way. Not out of malice — under the pressure of the task, attention
goes to the work itself, not to the procedure around it. The gap between "you
must" and "you cannot do otherwise" is the gap between a hope and a property
of the system.

**One breakage: the rule is on the books, and nothing holds it.** It arrives
from two sides. A requirement that a machine could have held is left as prose
— and it is skipped, like nine out of eleven. A requirement that no machine
can hold is thrown out as "obvious anyway" — and "obvious anyway" is not a
property of the rule but a property of somebody who has already been burned; a
new contributor and a new session have no such experience, and they are the
ones who break it most often. A rulebook containing only machine-checkable
rules teaches the wrong thing: the reader concludes that a green build equals
compliance, and everything outside a gate quietly becomes optional.

So this is one requirement, not two: every rule has an answer to "what holds
it", and the answer "nothing" is legitimate if it is written down with a
reason. An explicit "no mechanism" note is **a request for a mechanism**: the
list of such rules shows where the next gate should be spent, and stops them
masquerading as checked.

The asymmetry of cost: a record "held by nothing, because…" costs a paragraph,
while a skipped requirement that was counted as followed is discovered only by
a breakage — and after it the rule is read as having been followed.

## Practical boundaries

- a checklist is rewritten into a command, not extended with one more item:
  what cannot be forgotten is what executes;
- a public claim about quality is checked the same way as an internal
  requirement: a front page without a check is a promise;
- what nothing holds is gathered into a section named plainly rather than
  dissolved among other advice;
- every such rule carries **an incident**, not just a statement: without the
  story it becomes "obvious anyway" again;
- it says **why** a mechanism is impossible: the gate cannot see intent, the
  breakage appears only in a specific combination, the signal cannot be
  expressed;
- a gate with an unclear rejection message is worse than no gate — people
  start routing around it;
- when a mechanism appears, the rule moves over to the checkable ones and the
  section shortens — a measurable sign of progress.

## Where it applies

**Works** anywhere with continuous integration — for requirements a machine
can hold; and, as the second half, for rules about intent, order of actions
and manner of proof, which it cannot.

**Does not work** as an excuse: "no mechanism is possible" is established by
trying, not by declaring. A branch inside: requirements of taste without an
incident — "code should be readable", "the architecture should be simple" —
do not become rules at all; they belong in review, they do not go into the
section of things held by nothing, and they should not pretend to be rules.

**Sign of a violation:** a requirement is written down, and it has neither a
gate nor a "held by nothing" note with a reason; or the rulebook consists
entirely of what the build already checks.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#645

ArtVsMark/Stepik-Python-Grader#1296, ArtVsMark/Stepik-Python-Grader#1329

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § Что гейты не ловят.

Supersedes: [002](002-rule-without-mechanism.md),
[057](057-unmechanizable-rules-are-named-explicitly.md) — 057 refined 002 with
the opposite prescription for the same case; merged into one claim under
ArtVsMark/Engineering-Incidents-Playbook#645.

Related: [182](182-an-unmechanisable-answer-is-split-in-two.md) — an answer
"no machine can" is split in two; that is the attempt by which the reason
"held by nothing" is checked.
