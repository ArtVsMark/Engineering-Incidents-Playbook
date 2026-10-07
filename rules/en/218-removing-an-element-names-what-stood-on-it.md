# A mechanism that removes an element names what stood on it

**Area.** code, configuration, quality

**Tier.** 4 — code and tests

**The rule.** A mechanism that removes an element to clean up its result — a
job, a key, a dependency, a line — lists what stood on the removed element (a
condition, an event filter, an artifact name, an ordering), and either carries
each item over or refuses with a stated reason. Only what leads to the removed
element is removed; an expression that refers to it is not dropped silently
along with it. The question is asked about what was removed, not about what
remains: reading the remainder does not show it.

**Portable beyond Claude Code.** yes — the subject exists in any configuration
generator, dependency pruning or manifest cleanup: anywhere the result is built
by subtracting from the source.

## The incident

**The mechanisms project, 6–7 October: five hits in three external reviews of
one place** (ArtVsMark/Engineering-Pipeline-Mechanisms#1183, #1189, #1195). The
onboarding pass (`scripts/onboard.py::calling_part`) builds a consumer's calling
workflow template: it removes the supplier's own jobs, keeps the job that calls
the shared step and strips that job's `needs`.

1. **#1183 → #1189** (`d354953`, `bdfa067`). The removed job's inputs carried a
   filter on waking events. With the job gone, the facts step with write
   permission would run on any `ci` completion, and an input naming the removed
   job's artifact led nowhere.
2. **#1189, late review** (`0556492`, `e5530c7`, `7ff8f4d`). The caller's own
   condition on `needs.`, a status function inside a carried-over condition,
   references to the removed job in `secrets`, `strategy`, `concurrency` — each
   survived the stripping of `needs` and led nowhere.
3. **#1195** (`b75d8fc`, `86c14e4`, `b9379fb`). `failure()` with `needs` stripped
   and not carried over: the call would never run. And `needs` on ANOTHER call
   job was stripped along with the rest — two calls silently lost their order.

**The cost.** Three review passes of ~10 minutes each and three fixes to one
place. Every template parsed as YAML and passed the shape tests. None of the
errors would have turned red at the consumer: the step would simply not run, or
run at the wrong time.

**What did not work.** Fixing one form at a time: each pass found the next
reference to the removed element. The series was stopped not by another fix but
by [210](210-a-second-finding-on-one-place-stops-the-patching.md) — a list of
what can stand on a removed element, and a strict rule instead of another form.

## Why

**The result without the removed element looks right.** Removal leaves no trace
in what remains: the YAML parses, the jobs are there, the shape tests are green.
A constraint that lived on the removed element — a condition, an ordering, a
name — disappears with it and gives nothing away. A reader of the remainder sees
a consistent file.

**The dependency points from what remains to what was removed.** It is found
only by asking the removed element "who referred to you?". Walking the remainder
does not answer that, because the reference is either already erased or points
into a void that is syntactically legal.

**The cost is asymmetric.** A refusal with a reason costs the author one review.
A silently removed constraint costs a step that will not run, or will run at the
wrong time, at the consumer — and it is noticed by the absence of an event,
which means never right away.

## In practice

- before removing, list what stands on the element: references by name,
  conditions, event filters, artifact names, ordering;
- for each item — carry it over or refuse with a stated reason; there is no
  silent "went along with it";
- only what leads to the removed element is removed; an expression referring to
  it, and a status function with its dependency removed, is a refusal, not a
  quiet edit;
- the test suite checks the list with "stood on the removed element" cases, not
  only the shape of the result;
- there is no general gate and none is promised: what stood on the removed
  element is visible from the meaning of the link, not from its spelling.

## Where it applies

**Works** for mechanisms that build a result by subtracting from the source: a
template generator narrowing someone else's workflow; pruning dependencies from
a manifest; collapsing configuration by removing keys; removing a step, job or
line from a machine-assembled file.

**Does not work** for a removal on which nothing stands by construction: a leaf
with no references to it, and that is checkable. Nor for narrowing a predicate —
a condition, a pattern, a set of keys — where the neighbour is what is decided
by the same predicate: that is
[195](195-a-narrowed-predicate-names-its-neighbour.md). Here nothing is
narrowed, something is removed, and the neighbour is what relied on it.

**Sign of a violation:** a mechanism removes an element, while neither its code
nor its tests hold a list of what stood on the removed element or a refusal with
a reason — and the result is checked only for shape.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `.rules/finding-kinds.json`

ArtVsMark/Engineering-Pipeline-Mechanisms#1183

ArtVsMark/Engineering-Pipeline-Mechanisms#1195

See also: [195](195-a-narrowed-predicate-names-its-neighbour.md) — narrowing a
predicate names its neighbour; here it is removal, and the neighbour is what
relied on the removed element;
[210](210-a-second-finding-on-one-place-stops-the-patching.md) — a second
finding on one place stops one-form fixes: that is what stopped the series;
[211](211-a-mechanism-is-alive-only-if-a-working-path-reaches-it.md) — a
mechanism is alive while a working path reaches it; here the path to the step
existed, and the condition that started it disappeared.
