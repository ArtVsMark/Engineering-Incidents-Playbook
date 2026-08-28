# A mechanism is confirmed by a run, not by reading

**Area.** gates, pipeline

**The rule.** Until a mechanism has run against a live subject it is not
confirmed, however correctly it reads. A platform's refusal depends on state
that does not exist in the code, so "I read it and I am satisfied" confirms only
the absence of typos. And "it worked eight times in a row" is no confirmation
either: what runs in a row may be one side of a race.

## The incident

A catalogue's auto-merge was built in one pass and broke three times, three
different ways. None of them is visible in the code.

**The first.** Auto-merge was enabled after a green run — that is, at the moment
when it can no longer be enabled: the platform refuses a pull request in a clean
state, because there is nothing left to wait for. The mechanism would never have
worked once, and the code read as correct.

**The second.** The first-parent check was a job with a condition, so on pull
requests it produced a `skipped` outcome. A pull request with an unfinished check
is not considered clean — one skipped job quietly broke auto-merge entirely.

**The third, and the most telling.** The refusal also comes on an *unstable*
state: the required check has gone green while the auto-merge job is still
running and is itself making the pull request unclean. Between "blocked", where
enabling works, and "clean or unstable", where it does not, there is a race.
Eight merges in a row won it. The ninth lost.

A fourth turned up along the way: the token has no right to read branch
protection — a `403` where the documentation promised an answer.

## Why

**The refusal lives in the platform's state, not in the call.** The same call
with the same arguments succeeds or fails depending on what the platform thinks
about the pull request *this second*. That state is nowhere in the code, which is
exactly why a reader does not see it: they check the call, and it is not the call
that decides.

**A run of successes does not cover the state space.** Eight identical runs are
eight passes down the same branch of the race, not eight checks. Confidence grows
while coverage does not, so by the ninth attempt the mechanism is considered
better verified than at the first — precisely backwards.

**The asymmetry of cost here is unusual.** A reading error is cheap: a run
exposes it in a minute. Trusting the reading is expensive, because the mechanism
gets declared working — other mechanisms start leaning on it, and the breakage
surfaces inside somebody else's change and looks like their fault.

## In practice

- a mechanism has a **first live subject**, and is not called done before it:
  not "written" but "ran on change number such-and-such";
- verify **outcomes**, not the path: refusal, skip, third outcome
  ([039](039-three-outcomes-not-two.md)) — each at least once;
- a race is not won but handled: if the outcome depends on who got there first,
  both branches must be written;
- a streak of successes counts as one branch, never as coverage;
- read a foreign refusal literally. A `403` where an answer was expected is not a
  network blip or a formatting detail — it is a permissions boundary the
  documentation did not mention.

## Where it applies

**Works** wherever the decision is made by code that is not yours: a platform, an
external API, a scheduler, somebody else's pipeline.

**Does not work** for pure functions and data parsing — there reading and a test
cover the same ground, and a live subject adds nothing.

**Sign of a violation:** the mechanism is described in the rulebook in more
detail than it was ever run, and not one run is named.

## Trace

ArtVsMark/claude-code-playbook#34 — the auto-merge build and three breakages in
a row; ArtVsMark/claude-code-playbook#54 — the fourth, the state race.

See also: [039](039-three-outcomes-not-two.md) — the third outcome, which
reading never finds; [002](002-rule-without-mechanism.md) — a requirement
without a mechanism;
[107](107-it-works-for-the-author-means-tested-on-the-authors-sample.md) — "it
works for the author" means tested on the author's sample, and here the same
goes for a streak; [140](140-a-gate-is-tested-by-what-it-must-reject.md) — a
gate is tested by what it must reject.