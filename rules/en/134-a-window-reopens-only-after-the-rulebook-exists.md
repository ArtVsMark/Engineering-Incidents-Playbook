# A window opens with the project's context, not with the last window's knowledge

**Area.** agent sessions, process

**Tier.** 3 — gates and processes

**The rule.** A window reads the **repository**, not its predecessor's memory:
whatever is not in the project does not exist for it, even if the previous
window knew it. Hence the order when setting a project up: first the minimal
fill — a charter, the gates, a link to the shared catalogue — and **only then**
reopen the window. A fill done mid-session does not affect that session.

## The incident

Three projects of one owner, three windows, one evening. Measured as found:

| Project | Project charter | The rule catalogue in it |
|---|---|---|
| the rule catalogue | appeared the same evening | — |
| the large project | present, 86 KB | **never mentioned** |
| the profile showcase | **none at all** | — |

The consequences spread across all three.

**The showcase's window started blind** and over the evening did exactly what
the rules already describe: it merged a change from a cloud session, where the
credentials get substituted on a write, and it brought a change carrying four
topics. Both rules existed. Neither reached the window.

**The large project's window knew the charter but not the catalogue** — and
**re-derived** rules that were already written down there. The knowledge was
recorded and stayed unclaimed.

**The catalogue's own window started without a charter** and over the evening
broke seven of its own rules. The charter appeared only towards the end — that
is, it did not affect that session at all.

What all three share: the window is not at fault. **No project had any delivery
of rules into the window.**

## Why

**A window inherits the repository, not the knowledge.** "Reopened from the last
window" only means that a person passed on the links. The relay works
([006](006-window-lifetime.md)), but it carries only what lies in the project:
it hands over **addresses**, not contents.

**Context is read once, at start**
([047](047-rule-change-restarts-the-windows.md)). So a charter written mid-session
is work for the next session, not for the current one. A window that wrote the
rule itself keeps working the old way: it does not re-read that file.

**Hence an order that is easy to get backwards.** The natural urge is to restart
the window "to start off right". But a restart before the fill gives the same
blindness: there is still nothing to read. The charter goes down first, the
restart comes second — the reverse order looks sensible and gives nothing.

This is **not the same case as 047**. There the rules exist and change, and the
restart delivers the change. Here there are **no rules in the project yet**, and
the restart has nothing to deliver.

## In practice

- **the minimal fill is** the prohibitions, the list of gates, the procedure for
  adding a rule, and **a link to the shared catalogue**; without the last one the
  window never learns the catalogue exists and starts deriving its contents anew;
- **check "the charter was in place at start", not "the window is new"**: a
  window that wrote the charter works off the state at its own start;
- **a charter is written as triggers and links** — it is read in full at every
  start and costs context every time ([029](029-triggers-and-canon.md));
- **the relay does not replace the charter**: the opening message passes on what
  to work on, not how things are done here;
- **the sign that delivery is missing**: a window re-derives a rule already
  written in the shared catalogue, and does it confidently.

## Where it applies

**Works** when setting up a new project and when connecting a project to a
shared rule catalogue.

**Does not work** for a one-off task in somebody else's repository nobody will
return to: there the fill costs more than the work.

**Sign you need it:** a rule written in the shared catalogue is broken in a
project where the catalogue is not mentioned in a single line.

## Trace

ArtVsMark/Engineering-Incidents-Playbook — the charter appeared the same evening, before
it the window broke seven of the catalogue's rules; ArtVsMark/ArtVsMark — no
charter,
[ArtVsMark/ArtVsMark#20](https://github.com/ArtVsMark/ArtVsMark/issues/20) and
[ArtVsMark/ArtVsMark#21](https://github.com/ArtVsMark/ArtVsMark/issues/21), both
breakages described by existing rules; ArtVsMark/Stepik-Python-Grader — a
charter exists, the catalogue is not mentioned in it.

See also: [047](047-rule-change-restarts-the-windows.md) — a restart when the
rules change, here the case where there are no rules yet;
[006](006-window-lifetime.md) — the relay by links;
[029](029-triggers-and-canon.md) — how a charter differs from a retelling;
[120](120-how-to-run-a-rule-catalogue.md) — a project is linked to the catalogue
by one link; [129](129-a-catalogue-needs-a-consumption-contract.md) — delivering
a rule to a project, here — delivering it from the project to the window.