# To check a link, look for the link, not for the path in the text

**Area.** gates, documentation

**Tier.** 3 — gates and processes

**The rule.** A check that a document **links** to a file looks for the link
itself — `](address` or `]: address` — not for the address as a substring. The
address appears in the document twice, in the link target and in its label, and
a substring check stays green when the target is swapped: the condition is
satisfied by the label. More broadly: any check of a **relationship** done by
substring presence goes green where the relationship is absent.

**Portable beyond Claude Code.** yes — the subject belongs to any relationship
check over text: a link in documentation, an import in code, a declared
dependency in a manifest.

## The incident

A consumer's showcase gate requires both showcases to lead to the question set
`.rules/showcase.json`. It was written as `SET not in text`.

On a forged tree the gate went red exactly as expected: the test removed the
line entirely, and there were two findings, one per showcase. Sixty-two tests
were green at the same time.

Then a failure test on a copy of the live repository: the link's address was
swapped — `](.rules/showcase.json)` for `](nowhere)` — while the label was left
as it was, ``[`.rules/showcase.json`]``. The gate stayed green: ten questions,
one live badge, zero findings. The path had not gone anywhere — it remained in
the label, and the condition was satisfied there.

## Why

A substring is evidence of **presence**, not of a relationship. A document that
names an address and a document that leads to it are different states, and what
tells them apart is the markup, not the run of characters.

What decides the rest is the shape real breakage takes. Links break by moving,
not by deletion: a file is relocated, the address in the target is edited or
forgotten, and the label stays as it was — it is read by humans and did not
notice the move. So a substring check is blind in precisely the case that
happens, and sharp-eyed in the one that does not.

The forgery hid this because it removed the whole line. That tests deletion, not
substitution, and the gate was confirming itself
([146](146-a-green-gate-does-not-verify-its-premise.md)): it rejected what it
could, rather than what it was built for
([140](140-a-gate-is-tested-by-what-it-must-reject.md)).

## In practice

- look for the markup: `](address` or `]: address` — the link's target, not its
  text;
- keep **two** regressions: a mention without a link must go red, a legitimate
  reference-style link must not; otherwise fixing one side breaks the other;
- the forgery reproduces a moved file, not a deleted line;
- the same holds for import and dependency checks: `import X` in a comment and
  in code are different states.

## Where it applies

**Works** for relationship checks: a link to a document, a module import, a
declared dependency.

**Does not work** where mere presence of a string is the subject itself: "the
old name must be gone from the tree", "the config carries no debug flag". There
is no relationship there, and a substring search is the exact statement rather
than an approximation.

**Sign of violation:** the test for a missing link deletes the whole line
instead of swapping its target.

## Trace

ArtVsMark/Claude-Code_Usage-Token#27

Related: [140](140-a-gate-is-tested-by-what-it-must-reject.md) — a gate is tested
by what it must reject; 166 names a common form of the mistake: deletion is
rejected while substitution is what happens.
[146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate confirms
itself, not the claim it was built around.
[049](049-derive-state-from-live-artifacts.md) — state is derived from a live
artifact; a link's label is not one.
