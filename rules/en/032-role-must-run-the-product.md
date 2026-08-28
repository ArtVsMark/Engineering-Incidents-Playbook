# If a role's subject is observable in the running product, the role must run it

**Area.** roles, audit

**The rule.** A conclusion reached by reading code where you could have run the
thing counts as incomplete.

## The incident

An audit was conducted by reading. The density of findings was measured — and
it condemned the method:

| Method | Confirmed important findings |
|---|---|
| reading code | 8 out of 489 findings |
| **running the product** | **7 out of 224** — five times the density |
| **a pass in the browser** | **33 findings** where reading and `curl` gave 2 |

The browser pass was added last, almost as a formality. It found defects that
are invisible in code **in principle**: behaviour on a narrow screen, lost
state, unreadable messages, unreachable-by-keyboard controls.

## What "run it" means per role

| Role | What it actually does |
|---|---|
| tester | runs every mode, breaks the input, reads the report |
| developer | reproduces the defect with a command, not by inference from code |
| designer, front-end | opens it **in a browser**: dark theme, second locale, narrow screen, keyboard navigation |
| analyst | first creates data by running things, then compares what is displayed with fact |
| security | tries to break the boundary instead of reasoning about it |
| release engineer | runs the check on empty input, inspects the artefact rather than the config |
| technical writer | walks the documented scenario by hand |

**The exception** is roles whose subject lies outside the running product:
strategy, promotion, trend research. They stay reading roles, and that is fine.

## Why

Reading code answers "what is written here". The user faces "what happens" — and
that is the result of code interacting with an environment: browser, file
system, locale, screen size, accumulated data.

Whole classes of defect **do not exist in the code**: the missing handler, the
awkward ordering, the unreadable text, the impossible scenario.

## Where it applies

**Works** for any examination of a product: audit, review of a large feature,
investigation of a complaint.

**Does not work** for subjects not observable in the product: strategy,
licensing, plans.

**Requires** an environment where running is possible. If there is none, that is
not a reason to read — it is a reason to name the blind spot.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/roles.md` § a role does not end at
reading code