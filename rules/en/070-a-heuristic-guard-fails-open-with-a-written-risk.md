# A heuristic guard is relaxed deliberately — with the residual risk written down

**Area.** security

**The rule.** A check that is a guess by nature **lets things through** when data
is missing rather than refusing — but only if real barriers stand beside it and
the residual risk is stated in writing.

## The incident

The web shell defends against requests initiated by somebody else's page. One of
the signals is the headers that reveal a request's origin.

The absence of **both** headers is deliberately not treated as a violation. A
strict refusal would break documented non-browser use of the interface: scripts,
console clients and our own tests do not send those headers, and for them
"signal absent" is normal, not an attack.

Importantly, the relaxation does **not stand alone**. The browser vector is
closed by two barriers before it: a check on the address the request arrived at,
and request metadata that modern browsers always send.

The residual risk is written out plainly: a legacy browser without that
metadata, which additionally suppresses the second header. And in the same place:
what the heuristic will be replaced by once real authentication exists.

## Why

Strictness belongs where the signal **must** be present. If its absence is a
legitimate state for some clients, strictness becomes a refusal to serve the
legitimate — and it is bypassed not by attackers but by your own people,
switching the check off entirely.

Hence a distinction easily mistaken for a contradiction: **a guarantee fails
loudly, a heuristic passes quietly**. Requested isolation that is missing is a
failure. An origin signal that was not sent is not. The difference is whether we
promised it or are guessing.

The relaxation is legitimate **only in layers**. A lone heuristic that passes on
missing data protects against nothing. It makes sense strictly as the last,
softest layer on top of hard ones.

## In practice

- three things are recorded beside the relaxation: **why** strictness is
  impossible, **which barriers** stand before it, **what risk** remains;
- it says what the heuristic will be replaced by and under what condition;
- the relaxation is not widened "while we are at it": every newly permitted case
  is a separate decision;
- anything promised as a guarantee never falls under this rule.

## Where it applies

**Works** for layered defence where the outer layer is a guess.

**Does not work** as an excuse for a single check: "we decided not to refuse"
with no layers beneath it is simply an absence of defence.

**Sign of error:** the relaxation exists and there is no list of barriers beneath
it.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/http_guards.py`, #631.
Related: [045](045-no-silent-fallback.md) — the opposite case,
[046](046-name-the-gaps-do-not-level-them.md).
