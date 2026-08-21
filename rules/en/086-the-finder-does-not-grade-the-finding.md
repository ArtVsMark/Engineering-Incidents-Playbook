# The severity of a finding is not set by whoever found it — but the refuter needs a scale

**Area.** audit

**The rule.** A finding is graded by a separate checker instructed to "refute by
default". And that checker's scale is calibrated with examples, or it will not
filter out the weak but downgrade everything.

## The incident

The first half of the rule has been proved three times.

The author of a finding overrates it — not out of bad faith but because they see
it from inside: they spent time on it, they see the mechanism, they do not see
the context in which the mechanism does not fire. In one audit the authors
claimed **83 findings at `high`**; a separate check left **16**. In another, the
sceptic filtered out **7 of 32** as false.

The second half was discovered at greater cost. Instructing someone to "refute by
default" without a calibrated scale **shifts everything downwards at once**
rather than filtering out the weak: the checkers corrected the severity of **141
findings out of 192 — 73%**, almost all downwards, and confirmed defects at the
level of "downloading fails with an error" ended up in the lowest band.

The outcome is worse than inflation: priority had to be built from risk groups
rather than from assigned severity — that is, the grading mechanism stopped
working altogether.

## Why

Author and checker answer different questions. The author: "what is wrong here".
The checker: "prove it". They cannot be combined in one executor: proving things
to yourself is awkward, and refuting yourself seriously is impossible.

But scepticism has a **side effect** easily mistaken for rigour. "Refute by
default" shifts not the filtering threshold but **the whole scale**: the sceptic
is equally distrustful of the trivial and the serious, and their doubt pulls
everything down uniformly. Genuine filtering can be told from a general shift
only by an external reference point — examples of what counts as severe, medium
and minor **in this project**.

Hence a practical consequence: while there are no verdicts, any "how many serious
defects do we have" is a claim, not a result. Before every conclusion the number
of findings is reconciled against the number of verdicts.

## In practice

- the checker is a separate executor, not a second pass by the same one;
- their brief carries **three examples**: what is severe here, what is medium,
  what is minor;
- the report carries the confirmed grade, with the author's kept beside it — the
  gap between them is a useful quantity in itself;
- every finding has an exact location and a way to reproduce it: without those
  there is nothing to refute, and the check degenerates into opinion;
- mass downgrading is a signal of a faulty scale, not of a successful audit.

## Where it applies

**Works** for audits, reviews, defect reports, risk assessment.

**Does not work** if the finding is machine-checkable (the test fails or it does
not) — there the run gives the verdict.

**Sign of a faulty scale:** the share of corrected grades is large and almost all
corrections go the same way.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § additionally for
audits; audits v1.9.0 (7 of 32), v1.10.0 (141 of 192), 2026-08-10 (83 → 16).
Related: [037](037-finding-status-depends-on-window.md),
[044](044-check-the-premise-before-fixing.md).
