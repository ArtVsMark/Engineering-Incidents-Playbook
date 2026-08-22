# The handover is assembled as you go, not at the end

**Area.** agent sessions, process

**The rule.** A decision taken in conversation lands as an artefact
**immediately** — an issue, a comment, a decision record. Then handing over is
reduced to links. Whatever is left "for later" exists only in the session's
context and dies with it; at the end it has to be retold, which breaks the very
rule the handover exists for.

## The incident

In a single night an administrator session opened nine issues across two
repositories, took about fifteen project decisions — file formats, two entry
points over one implementation, connection modes, rejected alternatives — and
produced five rule candidates.

All of it was born **in conversation**. What settled in the repositories was
only what the session managed to write down as an issue or a comment along the
way.

The check is simple and needs no experiment: had the session closed halfway,
the decisions that survived would have been exactly those already written down.
The rest would have to be taken again — without knowing they had been taken
before, and without the rejected alternatives that show why this one was chosen.

The failure of a hand-written link is telling on its own. A comment pointing at
a candidate issue went stale **within an hour**: the candidate was closed, the
rule got a number, and the link kept pointing at something closed. A retelling in
a starting message goes stale the same way — only nobody notices, because nobody
re-reads the message.

## Why

**A session's context is working memory, not storage.** It does not survive a
restart, and that is by design rather than by accident:
[006](006-window-lifetime.md) requires a restart on a deadline,
[047](047-rule-change-restarts-the-windows.md) on a change of rules,
[121](121-closing-the-container-is-not-closing-the-work.md) — the container
closes on its own. The session always ends before the work does.

**Assembling at the end demands what is not there at the end.** At the end you
must recall what was decided, separate decisions from discussion, and write down
the reasons. That work is done worst exactly when it is done: the session is
running out of context, and the retelling comes out shorter and poorer than the
original.

**The asymmetry of cost.** Recording a decision as you go costs one issue or one
comment. Not recording it costs taking the decision again without knowing it was
ever taken — not "a minute more expensive" but "a different decision, because the
reasons were forgotten". The most expensive loss is not the decisions but the
**rejected alternatives**: they cost the most to obtain and disappear first.

## What counts as the essentials

Five items, each of them checkable:

1. **decisions that are not reversed** — with the reason and the rejected
   alternatives ([042](042-decision-records-its-alternatives.md)). Not written
   down — they get written **before** the restart, not after;
2. **where things stopped** — the state and what blocks it, as links to live
   artefacts rather than a description
   ([049](049-derive-state-from-live-artifacts.md));
3. **what was already tried and did not work** — otherwise the new session
   repeats the whole attempt; this is the most expensive loss of a restart;
4. **what the session does not know** — blind spots, other people's
   environments, branches taken by someone else
   ([046](046-name-the-gaps-do-not-level-them.md));
5. **how we work** — a link to the project's rulebook, never a retelling of it
   ([134](134-a-window-reopens-only-after-the-rulebook-exists.md)).

**What a handover never contains:** a detailed history of attempts, quotations
from the discussion, "we decided" without a link to the decision record, or a
list of issues — that lives in the tracker and goes stale in a message by
morning.

## In practice

- the record is made in the same pass as the decision, not "at the end of the
  day";
- a link points at an artefact that lives: the issue, not a retelling of it;
- there is one cheap completeness check: the new session answers "where did we
  stop" **from the repository** on its very first move, not from the starting
  message. If it cannot, the handover is incomplete, and the still-living
  predecessor is the one who completes it;
- a handover is not written "for the restart": it is a by-product of ordinary
  work, provided decisions settle straight away.

## Where it applies

**Works** wherever the executor changes while the work continues: agent
sessions, on-call rotations, shift handovers.

**Does not work** for a one-off task done in a single pass — there is nothing to
hand over, and recording decisions becomes paperwork without a reader.

**Sign of a violation:** the new session's starting message contains a paragraph
that appears in no artefact.

## Trace

ArtVsMark/claude-code-playbook#35 — the candidate, filed by a session belonging
to another project; ArtVsMark/Stepik-Python-Grader — the starting-message
template and the rulebook section about two sessions.

See also: [006](006-window-lifetime.md) — the session's lifespan and the shape of
a handover, here the moment it is assembled;
[121](121-closing-the-container-is-not-closing-the-work.md) — work does not close
with the container; [047](047-rule-change-restarts-the-windows.md) — the second
reason to restart; [029](029-triggers-and-canon.md) — why a retelling is worse
than a link.
