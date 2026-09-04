# Split documentation by reader, not by topic

**Area.** documentation

**Tier.** 1 — rules and roles

**The rule.** First ask who reads this, then decide where it goes. A topical
layout mixes audiences together.

## The incident

Documents accumulated in one directory, arranged by topic: architecture,
installation, security, plans.

A user looking for "how to install" ran into internal layer contracts. A
developer looking for the design ran into beginner instructions. Working notes
for agent sessions lived in the same place and turned up for both.

The worst casualties were the **historical** documents: finished briefs and
one-off audits looked current because they sat next to the live ones.

## The fix

Four directions, by reader:

| Directory | Reader | Answers the question |
|---|---|---|
| `use/` | user | how do I use this |
| `dev/` | developer | how is it built inside |
| `agent/` | automation, agent sessions | how we work here |
| `archive/` | historian | how it used to be |

A new document is created **inside a direction**, not at the root.

The tie-breaker between `use/` and `dev/`: which question does the text answer —
"how do I use it" or "how does it work inside". Not "what is it about" but "who
needs it".

## Why

Topic is a property of the text; reader is a property of the situation. People
come to documentation **with a question**, not with a topic, and a
reader-oriented layout answers the question faster.

A side effect, and a large one: it becomes visible that a document is **stale**.
In `archive/` that is normal; in `use/` it is a defect. While everything is
mixed together, the difference is invisible.

## Where it applies

**Works** from about a dozen documents upwards.

**Does not work** for three files — there the layout costs more than it gives.

**The price:** a "where does this go" question appears, and it must be answered
for every new document. Answering is cheaper than excavating a pile a year
later.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § documentation