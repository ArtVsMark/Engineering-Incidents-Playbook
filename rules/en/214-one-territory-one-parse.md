# One subject is parsed by one implementation: a second parse drifts from the first silently

**Area.** code

**Tier.** 4 — code and tests

**The rule.** A question the code asks about one and the same subject — what
counts as an issue in a trail, a push in a command, an analysed record — is
answered by one implementation, and every other place asks it. A second
implementation, even one that matches the first letter for letter today,
drifts from it at the first edit to either, and drifts silently: each is sound
on its own and covered by its own suite. A copy kept on purpose is signed under
[071](071-deliberate-duplication-is-signed.md), and a check holds the two
equal.

**Portable beyond Claude Code.** yes — any code where several places parse the
same string, record or format has the subject: gates, validators, reports,
builders over one tree.

## The incident

**10.09, THE PUSH GUARD: THREE PARSES OF ONE COMMAND.** The hook
`.claude/hooks/push_guard.py` parsed a `git push` line in three places. One
function read it ref by ref, its neighbour answered "is there a deletion
marker anywhere in the command" with a parse of its own, and a third decided
whether the command pushes at all. The first two diverged: for
`git push origin mine :theirs` the first saw a push and a deletion at once —
telling them apart is what it was built for — while the second saw only the
deletion, and the resurrection check for a deleted branch was switched off for
the whole command. The knowledge of the mixed form was already in the file; it
was not used. The review on #475 caught it. The review on #477 found the same
in the next pair: two places stripped a leading `+` in different orders, and
`+:name` — a deletion — read as a content push. Both fixes were the same: one
function parses the line, and the different questions are asked of its answer.

**THE SAME DAY, THE ANSWER GATE: TWO PREDICATES FOR ONE QUESTION.**
`scripts/check_bindings.py` rejected a "document" answer on two conditions —
no analysis word or a foreign one; a word but no reason — while the tier-0
count looked only at the first. A record with an empty `why` was printed as
analysed by the very run that rejected it (#481).

**THE 25.09 MEASUREMENT: THE IDEA LIVED WITHOUT A RULE.** 58 code comments
justified a single implementation by citing
[022](022-one-canonical-document.md), a rule about documents. The sweep of
citations against applicability
([204](204-a-citation-is-checked-by-applicability.md)) removed the number from
them, and no rule in the catalogue fitted. A parse of the tree found eight
regular expressions repeated letter for letter in two modules of working code.
Six are one subject: the record file name, the "Area" line, the "Portable"
line in both languages, the issue in a trail, the path in a source. Two of the
six sat right under a comment saying that a second parse would drift from the
first silently. The other two are generic markdown grammar: a section heading
and a table separator.

## Why

**Equal today is not one.** Two implementations are identical on the day they
appear and drift at the first edit to either. Whoever edits sees their own
function, its suite and a green run; the other copy never appears in the diff.

**Each copy is sound — which is why the drift is invisible.** The push guard
had no wrong function: each answered its own question correctly over its
own parse. The fault lived between them — one line understood in two ways.
Each copy's suite is green because it checks that copy alone.

**A comment about uniqueness does not hold.** Two copies sat under the very
sentence forbidding them. A claim about the code next to it is checked by the
code, not by rereading
([183](183-a-claim-about-the-mechanism-is-checked-against-it.md)).

**This is not 022 and not 209.** 022 is about documents: two descriptions of a
topic drift. [209](209-a-constant-is-quoted-by-reference-not-respelled.md) is
about text a mechanism prints or recognises. Here the subject is logic: a
regular expression, a predicate, the order of stripping a prefix. Neither of
the two covers its duplicate.

## In practice

- a subject has one implementation, the rest call it — by import, not by copy;
  different questions are asked of one parse's answer, not each of its own
  parse;
- a copy kept on purpose — a dependency boundary, a separate process — is
  signed under 071: what it matches, why it is not merged, under what
  condition the decision is revisited;
- merging two parses into one, take the wider: narrowing the shared parse to
  one question breaks the other
  ([195](195-a-narrowed-predicate-names-its-neighbour.md));
- a literal copy is machine-visible: the same regular expression in two
  modules of working code is a finding until named in a closed list. A near
  copy — the same idea with another capture group — and a duplicated
  predicate written as code are not.

## Where it applies

**Works** for code where several places parse one subject: gates, guards,
builders and reports over one tree.

**Does not work** for generic grammar that belongs to no subject: a markdown
heading, a table separator — the same parse does not make the subject one.
**Does not work** either across processes with no shared code — a script and a
shell step: there a copy is unavoidable and is signed under 071.

**Sign of a violation:** a second place in the code answers a question the
first already answers — in its own wording.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#475 — `.claude/hooks/push_guard.py`

See also: [022](022-one-canonical-document.md) — the same for documents;
[209](209-a-constant-is-quoted-by-reference-not-respelled.md) — the same for
text that is printed and recognised;
[071](071-deliberate-duplication-is-signed.md) — a deliberate copy is signed;
[211](211-a-mechanism-is-alive-only-if-a-working-path-reaches-it.md) — a second
implementation that displaces the first leaves an orphan;
[195](195-a-narrowed-predicate-names-its-neighbour.md) — merging parses, name
what each one decided.
