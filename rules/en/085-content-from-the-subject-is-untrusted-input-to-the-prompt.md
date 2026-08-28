# Text coming from the subject under review is untrusted input to the prompt

**Area.** AI, security

**The rule.** Everything controlled by whoever is being checked — their output,
their traceback, their source — enters the model request as **data**, not as
instructions. If there is no structural isolation, that is admitted out loud,
with an assessment of the damage.

## The incident

The hint is built from the failure context: the solution's output, the
exception's traceback, the source code. All of that is written by **the author of
the solution** — the side under review.

The threat analysis recorded what is usually left unsaid: content controlled by
the solution is placed into the request **without structural isolation or
escaping**. The output can even forge the heading of a trusted section — that is,
the solution can pretend to be part of our own instruction.

The defences are honestly described as soft: instructions in the system part
("rely ONLY on the context", "do not emit finished code") plus a hard length cap
on the fields. The answer is marked as generated and truncated.

And right beside it, the damage assessment, without which the admission would be
capitulation: abuse hurts whoever arranged it — a person spoils their own hint.
That makes the trade-off acceptable in the local version and **unacceptable**
anywhere the answer is seen by somebody else.

## Why

A model does not distinguish trust levels inside text. To it the system
instruction, the task description and the output of somebody else's program are
one stream, and "the instruction" wins not because it ranks higher but because it
is phrased more convincingly. So any text we put in there is a potential
instruction.

Hence a chain of reasoning that replaces the illusion of protection:

1. **who controls this text** — us, the user, or a third party;
2. **what they gain** by substituting an instruction;
3. **who suffers** — themselves, another user, or the system.

While the answer to the third question is "themselves", soft measures suffice and
that can be written down plainly. As soon as the answer changes — for instance
the hint becomes visible to another person, or influences a grade — the trade-off
stops being a trade-off and requires revision. The condition for revision is
recorded with the decision, or it will never arrive.

## In practice

- the boundaries of prompt sections do not rely on markup the input can forge;
  the length cap is applied hard and **before** the request is assembled;
- the model's answer is never executed and never substituted into code: it is
  text for a human, and it is marked as generated;
- the trade-off carries a **condition for revision** — which change makes it
  unacceptable;
- consent to send is verified **before** reaching outside, and the content enters
  the request only after that — otherwise the consent is bypassed by the
  injection itself.

## Where it applies

**Works** anywhere user-supplied or external text enters a model request.

**Does not work** as an excuse for inaction where the damage touches third
parties: "we have soft measures" is no answer if the sufferer is not the author
of the input.

**Sign of trouble:** the prompt contains a section heading the input is capable
of reproducing verbatim.

## Trace

ArtVsMark/Stepik-Python-Grader — `SECURITY.md` § AI hints (prompt injection),
`core/ai_grounding.py`, ArtVsMark/Stepik-Python-Grader#931 (consent is checked
against the recipient). Related:
[070](070-a-heuristic-guard-fails-open-with-a-written-risk.md),
[046](046-name-the-gaps-do-not-level-them.md).