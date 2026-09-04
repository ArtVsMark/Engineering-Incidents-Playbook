# A test asks the mechanism for its verdict, it does not restate the condition

**Area.** tests, gates

**Tier.** 3 — gates and processes

**The rule.** A test that checks a check calls it and asserts on the **verdict**.
Restating the condition in the assertion — "no longer than the limit", "an
extension from the list" — reproduces part of the rule and drops the rest, so it
diverges from the mechanism exactly where the mechanism has a caveat: a platform,
a mode, an exception. The test then goes red not on a violation but on a
condition the mechanism does not apply.

## The incident

A gate picks the temporary directory for a run and separately checks that
directory for fitness. It does have a path-length limit, but applies it **only on
Windows**: there `MAX_PATH` breaks the nested paths of test git repositories,
while on POSIX the ceiling is eight times higher and the question does not arise.

```python
if name == "nt" and len(str(path)) > _MAX_BASETEMP_LEN:
    return "path longer than ..."
```

The test was called "the default choice passes its own check", but never called
the check:

```python
assert len(str(chosen)) <= gate._MAX_BASETEMP_LEN
```

Half the condition — the threshold — moved into the test; the other half — "only
on nt" — stayed in the gate. While the system temporary directory was short, the
difference was invisible. Then the suite moved the temporary directory inside its
own root, and on macOS the path
`/private/var/folders/<hash>/T/pytest-of-<user>/pytest-N` plus the directory name
crossed a hundred characters. Three matrix jobs went red at once — with Linux and
Windows green — even though on that platform the gate would not have refused at
all.

The diagnosis cost three full runs of the suite: the message was about length,
and the question was about the platform.

## Why

**A check has caveats; a restatement has none.** A condition inside a mechanism
almost never reduces to one comparison: next to it sit a platform, a mode, a
flag, an exception for a special case. A restatement takes what catches the eye
and loses what was added later — and what gets added later is usually the caveat.

**The divergence grows silently.** While the inputs stay far from the boundary,
the test and the mechanism answer alike and the gap is unobservable. It surfaces
on a change unrelated to the rule itself — and looks like a violation of it.

**A test that calls the check survives edits to it.** A caveat changes, the
threshold moves, a platform is added — the verdict recomputes itself. A
restatement has to be fixed in a second pass, and it is remembered once it has
gone red.

## In practice

- assert on the **verdict**: `assert check(value) is None` rather than comparing
  against an internal threshold;
- the threshold and the boundary get their **own** test, with the condition
  stated explicitly ("on Windows a path over the limit is rejected") — then the
  caveat is named rather than implied;
- a private constant in an assertion (`gate._MAX_...`) is the tell of a
  restatement: the test reaches inside the mechanism instead of asking it;
- the exception is a test **of the condition itself**: there the repetition is
  the subject, but then the inputs are supplied by the test, not by the machine.

## Where it applies

**Works** for checks that return a verdict: gates, validators, policy resolvers,
functions of the form "what is wrong with this value".

**Does not work** when the mechanism returns no verdict (it raises, or silently
repairs) — then the verdict has to exist first, and that is a product change.
Nor for pure computations without caveats: `len()` has no platform, so there is
nothing to ask.

**Sign of trouble:** the test goes red on a machine or environment where the
mechanism does not apply its rule; the assertion contains an internal constant of
the module under test.

## Trace

ArtVsMark/Stepik-Python-Grader — `tests/test_preflight_basetemp.py`,
`test_default_choice_passes_its_own_check`: the assertion asks
`basetemp_problem()` instead of comparing a length against `_MAX_BASETEMP_LEN`.

Related: [075](075-a-guard-that-finds-nothing-must-fail.md) — a guard that finds
nothing must go red; [140](140-a-gate-is-tested-by-what-it-must-reject.md) — a
gate is tested by what it must reject.