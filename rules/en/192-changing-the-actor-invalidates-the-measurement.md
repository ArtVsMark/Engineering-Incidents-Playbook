# Changing who performs an action invalidates a measurement taken on the previous performer

**Area.** observation, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** A measurement of another system's behaviour was taken with ONE
performer of the action. A change that hands that action to a different performer
invalidates the measurement — and most often exactly the measurement it relied
on. Before such a change, the question is not "was it measured correctly" but
"will what was measured still hold when the action is performed by someone other
than the one it was measured on".

**Portable beyond Claude Code.** yes — the subject exists wherever another
system's behaviour was measured on one way of invoking it and a change alters
that way.

## The incident

`Claude-Code_Usage-Token`, 7 September 2026. Contributor attribution in the base
branch history had split in two: 52 commits with one trailer form and 33 with
another.

Breaking it down by merge method explained the pattern completely:

- a change of ONE commit — the window's line collapses into the platform's
  (survived 0 times out of 40);
- a change of SEVERAL — the bodies are inserted as text, the window's line ends
  up in the middle and no longer counts as a trailer (survived 14 out of 14).

The conclusion drawn: "the platform ALWAYS adds its own trailer, taking the name
from the account" — and for the observed case it was true.

The fix: the merge queue began assembling the body itself and stripping the
window's signature from it, relying on the platform's. But the measurement was
taken on a merge WITHOUT a supplied body, and the fix supplies exactly that. The
platform appends a trailer only when it assembles the body itself; given a
finished one, it adds nothing.

The cost: three merges in a row reached the base branch with NO signature at all
— worse than the duplication the change was made to remove. It was not noticed
straight away: the gate introduced by the same change counted only "more than one
name" as a finding and let zero signatures through, and on top of that read a
stale local reference — it printed "commits 0, names 0" while four merges sat in
the base branch.

## Why

A measurement of external behaviour is an observation under fixed conditions, and
the performer of the action is one of those conditions, on par with the inputs.
The word "always" in a measurement's conclusion usually means "always the way we
were doing it".

The substitution mechanism is simple and therefore invisible: the change alters
the INPUT by which the other side decides whether to do the work. While the
platform assembled the body, it appended a trailer because it was assembling.
Given a finished body, it stopped assembling — and stopped appending. Nothing
broke: the conditions under which the observation held had changed.

The asymmetry here is particularly cruel: the change breaks the very support it
stands on. The more precise the measurement, the more convincing the change, and
the less reason anyone sees to re-measure afterwards.

**Sign that the question is needed:** the justification for a change contains the
word "always" about someone else's behaviour, while the change alters the input
by which that someone decides.

## In practice

- before handing an action to a different performer, RE-MEASURE rather than
  reason it through on paper;
- a gate introduced alongside such a change must also catch ZERO — otherwise it
  only confirms the absence of duplicates;
- write "always" in a measurement's conclusion together with its conditions: who
  performed it and with what input;
- a change that does not alter the performer is exempt — there the measurement
  still holds.

## Where it applies

**Works** where another system's behaviour is known by observation rather than by
contract: a platform, a third-party service, someone else's tool.

**Does not work** where the behaviour is stated by a versioned contract: there
the support is the contract, not the observation, and the question moves to its
version. Nor does it apply to measurements of your own code: the performer there
is yours, and changing it is visible in the diff.

## Trace

ArtVsMark/Claude-Code_Usage-Token — `scripts/merge_queue.py`, the signature
constant and `squash_message`; `scripts/attribution.py`; the suites
`tests/test_merge_queue.py` and `tests/test_attribution.py`

Related: [037](037-finding-status-depends-on-window.md) — a finding from the
wrong surface is a hypothesis; here the surface is the same and the performer
differs; [146](146-a-green-gate-does-not-verify-its-premise.md) — a green gate
confirms itself, and the gate from this incident confirmed precisely the absence
of duplicates; [157](157-a-contract-version-bump-is-a-re-read.md) — there the
support changes in a contract and is announced by a number; here the support is
an observation, and it has no number at all.
