# A claim about the mechanism is checked by a mechanism, not by re-reading

**Area.** gates, documentation

**Tier.** 3 — gates and processes

**The rule.** Prose that states WHAT a mechanism does and HOW — a comment above a
call, a field in the rules answer, a line in the handbook — is a claim about the
current code and is checked against it by machine. A claim nobody can check does
not count as an answer: it goes stale silently and reads as a decision already
carried out.

**Portable beyond Claude Code.** yes — the subject exists wherever a decision
is recorded next to the code: a comment, an ADR, a section README.

## The incident

On 7 September 2026, a single shift turned up four cases of one shape, each
with an address:

| where | claimed | actually |
|---|---|---|
| comment in `scripts/check_task_state.py` | "BY REST, NOT GraphQL: the latter has a narrow quota" | the `gh issue view --json` call went through GraphQL exactly |
| catalogue answer for rule 001 | "everything else has been moved to REST" | 22 live calls of the `gh issue`/`gh pr` families |
| catalogue answer for rule 085 | "the catalogue builds no requests to a model" | the review workflow builds one and puts the change into it |
| neighbour `Stepik-Python-Grader` answer for 085 | mechanism is `tests/test_ai_grounding.py` | 12 tests, none about untrusted input |

The cost was measured the same day: an exhausted GraphQL quota took down the
merge duty, red on the shared branch froze the queue, and the investigation ate
a shift. Note that the first comment was written CORRECTLY — it named the right
policy; what it described wrongly was the code beside it.

The first fix was case by case: correct the comment, move the call. That failed
— the next step turned up a second case, then a third. A single fix cures the
instance and leaves the shape: none of the four claims had anyone to re-read it.

## Why

Prose about a mechanism reads as a decision already carried out. A comment
saying "we go by REST" looks like a record of work rather than a claim about it,
and the next reader — the author an hour later included — takes it for fact and
does not check. That is why such claims drift LONGER and more QUIETLY than
ordinary comments: an ordinary one is contradicted by the first edit nearby,
this one never is.

Cost asymmetry. A false "everything here is right" costs more than a missing
comment: the missing one makes the reader look, the false one does not. An
absent answer is visible; a false answer is not.

Hence the shape: not "write more precisely" but "every such claim has something
that checks it". Precision is held by the check, not by care.

## Practical boundaries

- state the claim so that it can be checked: name the subject (what exactly is
  done) and the place (where);
- build the check in the same pass as the claim — otherwise it never appears;
- check that the correspondence EXISTS, not that it is good: "the call uses the
  API it names" is machine-checkable, "the comment explains well" is not;
- revisit the decision if the check starts firing on legitimate cases: the
  claim is then broader than the check, and it is those two that must be
  separated, not the author from the rule.

## Where it applies

**Works** where a decision is recorded next to code that can change
independently of the record: comments about a chosen API, transport or format;
"what holds this" fields; gate tables in the handbook.

**Does not work** for prose that claims nothing about current code: why a
decision was made, the history of a rejected option, a past measurement. There
is nothing to check them against, and demanding a check would turn explanation
into a label — exactly what rule 154 refuses.

**Sign of violation:** a comment or field names a mechanism, and there is no
answer to "what turns red if this stops being true".

## Trace

ArtVsMark/Engineering-Incidents-Playbook#355

Related: 002 (a rule without a mechanism is a promise — there the mechanism is
ABSENT, here it exists and the claim about it is false), 044 (an address is a
claim about the tree and is verified), 146 (green confirms itself), 166
(structure instead of prose where prose has to be parsed by regex).
