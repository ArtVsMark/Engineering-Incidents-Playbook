# An absence claim a single command can refute must be a gate

**Area.** gates, documentation

**The rule.** The answer "there is nothing here" is a **claim about reality**,
not a turn of phrase, and it goes stale silently: no mechanism moves prose, while
prose looks like a considered decision. Prose as a whole is unverifiable and a
gate must not touch it; but it has a **subclass** that reduces to the existence
of an object — a tag, a file, a registry entry — and that subclass must be
checked. The test of applicability is simple: if a claim can be refuted by a
single command with no network, it should be a gate rather than text.

**Portable beyond Claude Code.** yes — the subject belongs to any document that
answers "we don't have this": a showcase, a project card, a coverage report.

## The incident

A consumer's showcase answered two of the set's questions like this: "there is
nothing here: the project has never been released, no release tag exists in the
repository", and "no distribution has been published, version 0.0.0".

By the time of the review the repository held the tags **v0.1.0 and v0.2.0**,
both with a created release and attached distribution files, and the version in
the tree read **0.2.0**. The answer had outlived **two releases** and had sounded
confident throughout.

The showcase gate was green and would have stayed green: it checks the contract's
**form** — that every question has exactly one answer and that the stated reason
is at least twenty characters — and it cannot check the truth of free text by
construction.

The lie was refutable by one command with no network: `git describe --tags`. A
subclass check was introduced: an answer beginning with "there is nothing here"
is compared against the tree. Measured on the real set — **one finding, exactly
that one**.

## Why

An empty field and a false claim are different states, and the second is worse.
A gap is visible: people look for it, people ask about it. A confident sentence
looks like a **decision** — like work somebody has already done — and therefore
does not get re-read.

Here it is worse even than an invented number: a number at least invites
re-checking, because a number has to come from somewhere. The sentence "we have
never released" owes nothing to anything.

Hence the boundary without which the gate is removed at the first edit: two kinds
of absence must be told apart. "There is nothing here" is a claim that is either
true or false, and there is something to check it against. "We have no indicator
of our own" is a decision to show an existing subject through someone else's
source, and there is nothing to check it against. A gate that conflates them goes
red on a correct answer.

And the asymmetry of outcomes, also deliberate: the subject found while the
answer denies it — refuse; the subject not found — stay silent. In a cloud
session's shallow clone "there is no tag" means "we did not look", and red on
that would be false ([039](039-three-outcomes-not-two.md)).

## In practice

- what is checked is the subclass reducible to an object's existence: a tag, a
  file, an entry, a version — whatever one command can see without a network;
- "there is nothing here" and "we have no indicator of our own" are different
  answers and are checked differently;
- refusal in one direction only: a refutation found — red; none found — silence,
  because not knowing does not prove absence
  ([075](075-a-guard-that-finds-nothing-must-fail.md) reads inverted here: the
  subject of the check is the claim itself, and it is present);
- prose that does not reduce to an object stays prose: demanding a machine check
  of it would create a gate nothing can satisfy
  ([002](002-rule-without-mechanism.md)).

## Where it applies

**Works** where a document answers "we don't have this" and the subject's
existence is visible locally.

**Does not work** for an absence nothing can refute: "we have no review
process", "we don't track satisfaction". There is nothing to check, and the rule
collapses into ordinary editing. Nor does it work in a shallow clone with no
history: the command answers "no" to everything there, and the gate would become
a generator of false findings — which is exactly why its refusal is one-sided.

**Sign of violation:** the document contains the phrase "there is nothing here",
and no job reads it.

## Trace

ArtVsMark/Claude-Code_Usage-Token#59 — scripts/preflight.py, the subject check;
.rules/showcase.json, the release and distribution questions

Related: [046](046-name-the-gaps-do-not-level-them.md) — name the gaps rather
than levelling them; 175 says the naming of a gap goes stale too.
[002](002-rule-without-mechanism.md) — a rule with no mechanism is a preference;
the same holds for a claim with no check.
[075](075-a-guard-that-finds-nothing-must-fail.md) — a guard with no subject
must fail.
