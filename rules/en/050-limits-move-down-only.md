# A gate's budget only moves down

**The rule.** A number in a gate is a ceiling, not a setting. It comes down as
the cleanup progresses and **never goes up**: raising the ceiling means the gate
was adjusted to fit the breach.

## The incident

A gate protects the front page: it must not exceed a fixed number of lines.
Another gate holds explanatory documents at zero task links, and gives border
zones a budget — how many such links are still tolerated there.

The failure scenario is always the same and very tempting: the document grew,
the gate went red, and editing the number up by one makes the build green in a
second. Formally the rule is honoured — it is about not exceeding the written
number, after all.

So the number was declared one-directional: budgets **go down** as the cleanup
progresses and never go up. Growth means not "we now need more" but "the log has
crept back into explanatory text".

## Why

A gate with a two-way number restricts nothing. It becomes a gauge: always
showing the current value, always green. The restriction appears exactly at the
moment one direction is closed.

Second: one-directionality turns the number into **a trace of the cleanup**. The
history shows where the system is heading, and the movement is measurable. A
two-way number gives no such history — it only shows that somebody edited a
config.

Third, psychological: editing a ceiling feels like a technical detail rather
than a repeal of the rule — which is why it passes review. The prohibition has
to live next to the number, explicitly.

## In practice

- next to the number, a comment saying it only decreases, and why;
- the number lives **in one place**: if it is also mentioned in documentation,
  the rule requires editing both, which is a separate reason not to duplicate;
- if growth is genuinely needed, that is not an edit to a number but a
  **decision**, recorded with what changed;
- do not lower it "for the future": a ceiling below the actual value is the same
  false red from the other side.

## Where it applies

**Works** for cleanup budgets: front-page size, number of exceptions, count of
skipped tests, a debt counter.

**Does not work** for thresholds that depend on the system growing (build time
over more data) — there the number must move both ways, and what protects you is
comparison with a baseline, not the number.

**Sign of a breach:** the history of the threshold file contains a commit where
the number grew, with no explanation beside it.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § links to issues (the
`_DESIGN_TAIL_BUDGET` / `_AGENT_TAIL_BUDGET` budgets), § line budget and link
check. Related: [002](002-rule-without-mechanism.md),
[023](023-readme-is-a-storefront.md).
