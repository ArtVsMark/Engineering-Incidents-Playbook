# A finding obtained on the wrong surface is a hypothesis

**Area.** audit

**The rule.** A defect found against a fake but living on a real surface gets no
severity until it is confirmed on the real one. It goes into the other
environment's checklist with the status "hypothesis".

## The incident

The 2026-08-10 audit: 83 findings claimed at `high`. Adversarial verification
left **16** — and that was with the surface available, so most were filtered out
without even reaching the expensive environment.

The inflation mechanism is simple. An executor reads the code, sees a branch that
"ought to fail", and assigns `high`. They cannot check it: there is no live
network, no real token, no display. But the severity is already set, and from
there it travels into the summary as a fact.

## Why

Severity is a claim about **the consequence in production**, not about the shape
of the code. The shape of code is visible everywhere; the consequence is visible
only where the surface is real. Between them sits an assumption, and it must be
labelled as one.

The cost of error is asymmetric. An inflated `high` costs queue position: people
fix by priority, and invented severity pushes real severity behind it. A missed
`high` costs an incident. So "hypothesis" is not a softening but an honest name
for something not yet verified.

A second consequence of the same principle: a surface belonging to another
environment **is not covered by reading code**. It either goes into the other
session's checklist or is called a **blind spot** in plain words. There is no
third option called "we checked it by reading".

## In practice

- the environment is assigned **at the same moment** as the audit slice itself,
  not worked out afterwards. Otherwise the surface drops out silently: the
  executor could not run it, told nobody, and it surfaces at the critic's stage;
- in the audit document a hypothesis carries no severity but a line saying
  "confirm in <environment>";
- the list of what is **never** attempted in the cheap environment is written in
  advance: a wave spent on a certain refusal costs as much as a successful one;
- an issue is closed by proof **in the environment where the surface lives**,
  not by a diff: the change merges, the issue waits for a run.

## Where it applies

**Works** anywhere part of the checking runs against fixtures, mocks or
synthetic data.

**Does not work** if nobody has the real surface — then the hypothesis stays a
hypothesis forever, and it is more honest to call it a blind spot immediately.

**Sign of a breach:** the audit summary contains more `high` findings than
reproduced scenarios.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/environments.md` § the status of a
finding depends on the environment, § closing an issue requires proof in the
same environment.