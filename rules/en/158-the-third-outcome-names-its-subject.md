# The third outcome names its subject, not just its cause

**Area.** gates, reliability

**The rule.** "The check did not run" must say **what exactly** did not run:
which source, file, address. The code and text of a foreign error answer "what
happened", but not the one question the third outcome exists for — is this
failure theirs or ours. The address is attached at the point of the call, not
reconstructed later from a traceback.

**Portable beyond Claude Code.** yes — the subject belongs to any mechanism
that reaches more than one source.

## The incident

On 31 August a showcase session started from a handover and first ran the
mandatory gate `scripts/build_metrics.py --check`. The gate answered "the build
did not run: the source did not respond — HTTP Error 403: Forbidden" and cited
[039](039-three-outcomes-not-two.md).

The build reaches four foreign repositories and PyPI. Which of them failed was
not in the message. The address had to be recovered by monkey-patching
`urllib.request.urlopen`: the rule catalogue had refused. After the scope was
fixed the second run failed the same way, and the traceback had to be repeated —
a second source stood behind the first.

The cause, moreover, was **not on the other side** the rule's wording points to:
a cloud session starts with a scope of one repository, and its proxy answers 403
to everything else. The repositories are public; `curl` without a token gets 200.

Two gate runs went into recovering what the mechanism knew at the moment of
failure and threw away.

## Why

The third outcome exists to separate "we checked and found" from "we did not
check". But the second has a fork of its own, and it costs more: **ours or
theirs**. Without naming the source, the mechanism hands the reader a task it
has just solved itself — finding the side that failed.

Recovering the address from a traceback costs exactly one run more than printing
it, and that price is charged more than once: a second failing source may stand
behind the first.

Separately, a message without an address **misdirects**. "The source did not
respond" reads as "something broke on their side" and leads away from one's own
environment — which is where the cause was.

## In practice

- the address is written where the call is made: `f"{url} did not respond —
  {exc}"`, not further up the stack where the source is already lost;
- when walking several sources, name the **failing** one, not the whole list;
- the return code and exception text stay: they answer "what happened", the
  address answers "where".

## Where it applies

**Works** for any mechanism reaching more than one source: builds over foreign
repositories, polling consumers, reading several config files.

**Does not work** for a mechanism with a single source: there the address is
already in the check's name, and printing it only lengthens the message.

**Sign of violation:** to know what to fix you have to run the mechanism again
with debugging — while at the moment of failure it knew the address.

## Trace

ArtVsMark/ArtVsMark#95

Related: [039](039-three-outcomes-not-two.md) — it introduces the third
outcome, and 158 says what that outcome owes;
[075](075-a-guard-that-finds-nothing-must-fail.md) — a step without a subject
must fail, and here the same demand applies to the message itself;
[046](046-name-the-gaps-do-not-level-them.md) — "absent" and "broken" differ
only when the difference is said out loud.
