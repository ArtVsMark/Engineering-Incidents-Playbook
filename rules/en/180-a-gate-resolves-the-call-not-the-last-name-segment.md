# A gate resolves a call through the file's imports, not the last name segment

**Area.** gates, code

**Tier.** 3 — gates and processes

**The rule.** A gate hunting for calls into a particular library must identify
its subject by **how that library is named in the file being parsed** — by its
imports — and not by the last segment of the call's name. A matching segment
proves nothing: a local function may carry the same name. The other half of the
same requirement: resolution must go **back to the original name**, because an
aliased import otherwise hides the function from the list of names under check,
and the gate stays silent where it is obliged to speak.

**Portable beyond Claude Code.** yes — the subject belongs to any static
analysis over namespaces: `import` in Python, `use` in Rust, `import` in Go and
TypeScript.

## The incident

`Claude-Code_Usage-Token`, 3 September, issue #95. A gate was introduced —
"a subprocess call names its deadline". It identified its subject the way the
neighbouring encoding gate did: by the last segment of the name
(`subprocess.run` → `run`).

**For the neighbour that worked by luck:** its trigger is the `text=` argument,
which local functions never take. The new gate has no such trigger — it catches
**any** `run(...)`. The tree holds local functions with that name: `pr_check.run`
and `merge_queue.run`. The gate declared them findings, the automatic fix added
`timeout=30` to them, and **fifteen** tests failed with `TypeError: run() got an
unexpected keyword argument`.

Resolving through the file's imports — `import subprocess as sp`, `from
subprocess import run as запустить` — removed **17 false findings out of 48** and
closed the reverse hole along the way: before the fix a call through an alias
went unseen, because the alias is not in the list of names under check.

**Measured in the catalogue, 4 September.** The same construction sits in
`scripts/check_subprocess.py`: the name is taken as `node.func.attr` or
`node.func.id` and matched against the `CALLS` list. The tree holds **12 local
functions** named `run`. False findings today: zero — but by exactly the same
luck as the neighbour's, the `text=` trigger. The reverse hole here is **live and
complete**: a call through `from subprocess import run as ...` is not seen at
all, and it is precisely the absence of such a call that turns the gate green.

## Why

The last segment of a name is a **string**; the subject under check is a
**function**. The file's namespace stands between them, and a gate that skips
that step checks a different relation from the one it reports on. While the
trigger is narrow the error does not surface and looks absent; widen the trigger
— and it gets widened at the next requirement — and it arrives all at once.

The asymmetry of price here is unusual and worth saying out loud. Normally a
false finding "just adds noise" while a miss is dangerous. Here it is the other
way round: **a false finding invites you to fix working code**. The gate calls a
correct call a violation, the fix adds a parameter that does not exist, and what
worked breaks. A miss leaves the system as it was; a false finding leaves it
worse than before the gate existed.

The second half of the rule — the alias — is not a symmetric addition but the
same defect from the other side: there a name matched the wrong function, here a
function failed to match its own name. One resolution through imports closes
both.

## Practical boundaries

- the subject is identified through the imports of the file being parsed: the
  names the module is available under in it, and the names functions were taken
  from it under;
- easy to miss: **a narrow trigger masks the defect** — while the gate only
  catches calls carrying a rare argument there are no false findings, and the
  parsing looks correct;
- easy to miss the other side too: `from X import f as g` is the same subject
  under a different name, and the list of names under check does not hold it;
- revisit the decision if the gate stops being static: with runtime inspection
  the subject is known exactly, and resolving through imports is pointless.

## Where it applies

**Works** for any static gate whose subject is calls into a particular module:
subprocesses, network, time, randomness, the filesystem.

**Does not work** where the subject is defined not by a name but by the **shape**
of a call: a gate looking for "a format string with interpolation" or "an empty
`except`" never touches the namespace. Nor does it work for dynamic calls —
`getattr(module, name)` is not available to static analysis, and that is written
down as a boundary of coverage rather than passed over in silence (075).

**Sign of violation:** the gate's list of names under check consists of **last
segments** — `("run", "call", "Popen")` — and the imports of the file being
parsed appear nowhere in the gate's code.

## Trace

`scripts/subprocess_timeout.py` at the consumer, issue
ArtVsMark/Claude-Code_Usage-Token#95; in the catalogue —
`scripts/check_subprocess.py`, measured 4 September: 12 local functions named
`run`, reverse hole open.

Related: [166](166-check-the-link-not-the-path.md) — checking a relation through
the presence of a substring; here the match is exact and the relation is still
absent. [141](141-a-marker-is-matched-whole-not-by-prefix.md) — the neighbouring
half of the same: there a marker is matched by its start, here a name by its
tail. [051](051-warn-on-likely-block-on-certain.md) — why a false finding costs
more than it seems.
