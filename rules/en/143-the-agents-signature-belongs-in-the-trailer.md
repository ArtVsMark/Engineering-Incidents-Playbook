# The agent's signature belongs in the trailer, not in the author field

**Area.** agent sessions, pipeline

**The rule.** The commit author is the person answering for the change; the
agent is named in a co-authorship trailer. The author field and the trailer are
different fields with different fates: the trailer survives the merge as text,
while the platform carries the author field into the shared branch and resolves
it to an account. Check it **before** the merge: afterwards the shared branch is
protected and there is nothing left to rewrite.

## The incident

A session was working in the rule catalogue, signing commits with whatever
identity the container carried by default: `Claude <noreply@anthropic.com>`. The
co-authorship trailers were correct, the attribution gate was green on every
change, all seven checks passed.

The change merged by squash. For the author of the commit in the shared branch
the platform wrote **`claude[bot]`** — it found no account for the signing
address and substituted the app whose installation had pushed the branch.

The eight preceding merges on that branch are authored by a person. The ninth is
a bot. Two kinds of authorship now appear in the contribution graph, and it
cannot be fixed: the shared branch's history is not rewritten
([114](114-migrate-from-the-current-version-not-from-zero.md)).

**The rule had already been paid for — in a neighbouring project.** There a
change from an agent is deliberately not merged, and is instead opened under the
owner's identity by a separate pipeline job. None of that reached the rule
catalogue, neither as a record nor as a gate — so
[080](080-every-new-rule-goes-into-the-catalogue.md) was broken earlier and the
bill arrived here.

**It is telling that the documentation described the outcome.** The catalogue's
auto-merge notes say it outright: "author of the change = a person → author of
the commit in main = a person". That is a **consequence**, not a mechanism: it
holds exactly when the commits are signed by a person — and nothing checked
that.

## Why

**Two fields look alike and behave differently.** The `Co-Authored-By` trailer
is a line in the message body: it travels into the shared branch as text and
threatens nothing. The author field is **resolved to an account** by the
platform, and everything that counts contribution is built on it. A gate that
matches only trailers inspects the harmless field and never looks at the
dangerous one.

**The error is discovered after it stops being fixable.** Before the merge the
branch history is rewritten by a single command. Afterwards the shared branch is
protected and a debt remains. It is the same skew as with attribution generally
([123](123-attribution-is-verified-on-the-final-history.md)), only sharper:
there a trailer is missing, here the author is wrong, and it is visible to
anyone who opens the history.

**The default works against you.** The signature in an agent's environment is
set automatically, and in this sense it is always wrong. Without a gate the
error is not "possible" — it happens by default: avoiding it requires knowing
about it in advance.

**Asymmetry of cost.** Checking the author field is one comparison against a
list already read. Not checking it costs permanently wrong authorship in the
shared branch.

## In practice

- the commit author is a person; an agent listed in `.github/authors.txt` in the
  author field is **rejected** by the gate: that list holds agreed
  **co-authors**, not authors;
- the check lives in the branch-commits mode, before the merge. In the
  first-parents mode the author is not checked: there the finding is
  unfixable and would become permanent red
  ([051](051-warn-on-likely-block-on-certain.md),
  [114](114-migrate-from-the-current-version-not-from-zero.md));
- the gate has a subject on both sides: a commit with the agent as author must
  be rejected, a commit with a person as author and the agent in the trailer
  must pass ([140](140-a-gate-is-tested-by-what-it-must-reject.md));
- revisit if the agent is given an account of its own: a bot author becomes
  legitimate then, and what needs forbidding is the absence of a signature, not
  its presence.

## Where it applies

**Works** wherever an agent commits and the platform performs the merge: squash
merges, merge queues, auto-merge.

**Does not work** where agent authorship is the desired outcome: a repository
owned entirely by automation, mirrors, generated branches. A human signature
there would be a forgery.

**Sign of the violation:** a first-parent appeared in the shared branch whose
author is an application rather than a person's account.

## Trace

ArtVsMark/claude-code-playbook#79 — the post-mortem and the cost;
ArtVsMark/claude-code-playbook#78 — the merge with the bot author.

Related: [123](123-attribution-is-verified-on-the-final-history.md) —
attribution is verified on the final history;
[114](114-migrate-from-the-current-version-not-from-zero.md) — the past is not
rewritten, and that is a debt rather than a task;
[080](080-every-new-rule-goes-into-the-catalogue.md) — the neighbouring
project's rule never arrived here, and the bill came;
[135](135-session-identity-is-established-by-a-write.md) — what a session signs
with.
