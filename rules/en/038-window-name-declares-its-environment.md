# A session's name starts with its environment, not with its task

**Area.** agent sessions

**Tier.** 3 — gates and processes

**The rule.** The first thing in an agent session's title is an environment tag:
`[WEB]`, `[LOCAL]` or `[CLI]`. The task comes after. The name is assigned when
the session opens, not when you need to find it.

## The incident

Sessions differ **not in power but in access to the real thing**, and it is the
environment that decides whether a task is feasible at all: a cloud session has
no real secrets, no live network, no display and no accumulated history; the
local one is the only place where the product behaves as it does for the user.

From outside, though, sessions look identical. The registry shows a title and a
last-activity time, and that is all. Walking the open pull requests kept running
into the same question: whose is this, and can it even be finished where it was
started? The answer had to be reconstructed from indirect traces — branch names,
commit style, which commands that session had managed to run at all.

The idea of a "repair session" for ownerless pull requests grew from the same
soil: the job was less about fixing a red build than about identifying whose
pull request it was. A tag in the title removes half that work: a pull request
from a session tagged `[WEB]` certainly could not have passed a visual
inspection, and there is nothing to clarify.

## Why

A dispatcher needs a **feasibility signal**, not a topic. The topic says
nothing: "user profile" could be layout work (local only) or a schema migration
(anywhere). The environment says it immediately and unambiguously.

A prefix rather than a suffix, because lists truncate the tail: in a narrow
column the beginning of the line survives. Capital Latin letters, because the
tag is found by eye and by `grep` in one pass and does not blend into the words
of the task.

A separate effect is the session's **self-discipline**. A session whose name
begins with `[WEB]` reminds itself that visual inspection and work with real
data are not its job but something it hands over. The work-splitting rule
becomes visible on every approach to the session, instead of sitting in a
document you have to remember.

## The mechanism

Without a mechanism this is a promise, not a guarantee. And the mechanism here
is cheap: in the session registry every record carries a **machine-readable
environment field** distinguishing a cloud container from a session bridged in
from the owner's machine. So the name need not be taken on trust: the prefix is
**checked** against the fact, and a mismatch is an error, not an opinion.

Hence the check folds into the session walk in three lines:

- a session without a prefix is renamed **on the spot**, during the walk, not
  "later";
- a prefix contradicting the environment field is corrected by the field: the
  truth is in the field, not in whoever typed the title;
- the walk is not complete while any session in the list lacks an environment
  tag.

The tag does not duplicate the field; it makes it **visible in one line**: the
field has to be queried and read, while the prefix shows up in any list, in a
notification, and in the link by which a session is handed to another person.

**The limit of the mechanism — and the third tag.** The registry shows only
sessions connected to it. A session started on the owner's machine **without a
bridge** does not appear in the list at all: it cannot be seen, renamed, woken
or accounted for from outside.

So there are three tags, not two, and they distinguish **two different
properties**:

| Tag | What the session **can do** | Visible from outside |
|---|---|---|
| `[WEB]` | only what a clean container offers | yes, fully |
| `[LOCAL]` | real data, network, display | yes, through the bridge |
| `[CLI]` | the same as `[LOCAL]` | **no** — the session is not in the registry |

`[LOCAL]` and `[CLI]` are equal in capability and opposite in observability, and
observability is what settles the dispatcher's questions: who can be woken,
whose pull request has nobody to finish it, whose spending will never reach the
statistics. `[CLI]` is a warning that says "nothing reaches in here from
outside", and only a person can attach it: the registry knows nothing about such
a session.

Hence the asymmetry of discipline: `[WEB]` and `[LOCAL]` are checked by machine,
`[CLI]` is held by hand — and that is where it breaks most often. A session
absent from the list is absent from the walk as well.

## In practice

- format: `[WEB] short task` · `[LOCAL] short task` · `[CLI] short task`;
- `[CLI]` goes wherever a person can see it: the terminal tab title, the session
  name on the machine — and it is repeated in the pull request description,
  otherwise the link between session and work vanishes with the session;
- the name is assigned **when the session opens**, together with the opening
  message, not when the session needs finding;
- the tag does not replace the division of work — it makes a breach visible;
- the tag names the environment, not the host: what matters is what the session
  **can do** and whether it can be reached, not where the hardware stands;
- a session unreachable from outside does not take on work somebody else may
  have to pick up: there will be nobody to ask and nobody to nudge.

## Where it applies

**Works** when several sessions live in parallel and differ in capability.

**Does not work** with a single environment: the tag becomes noise, identical
everywhere.

**Sign of a breach:** to decide who should get a task you have to open a session
and see what it can do. A second sign: work in progress on a pull request whose
author cannot be contacted.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § two environments,
`docs/agent/environments.md` § how to split work between them. Related rules:
[002](002-rule-without-mechanism.md) — a rule without a mechanism;
[018](018-cloud-checks-nodes-local-checks-chain.md) — environments check
different things.