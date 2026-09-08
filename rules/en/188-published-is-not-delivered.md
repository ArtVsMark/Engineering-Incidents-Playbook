# Read back what you published: the platform may rewrite it, and a 201 will not show that

**Area.** automation, reliability

**Tier.** 2 — the pipeline and CI

**The rule.** Sent through an intermediary is not the same as delivered.
Automation that publishes text somebody MUST read and act on — a command to a
bot, a mention of a participant, a trigger link — has to read the published
version back and compare it with what it sent. A success code proves the request
was accepted, not that the meaning arrived.

**Portable beyond Claude Code.** yes — the subject exists wherever you publish
through a third-party service entitled to normalise text: chat platforms,
trackers, mail gateways.

## The incident

A profile showcase, 7 September 2026. The branch of change ArtVsMark/ArtVsMark#134, opened by
`dependabot`, had fallen four pipeline fixes behind the base, and it could not be
updated from the session: merging would have carried an edit to
`.github/workflows/pr-check.yml`, and the app holds no `workflows` permission —
the platform refused outright.

The supported workaround is to command the bot itself with a comment,
`@dependabot rebase`. The comment was published, the API returned the address of
the created record, and the session went off to wait.

An hour later it turned out the published form was `·@·d·ependabot r·ebase`: the
platform had inserted invisible characters between the characters. The command
never reached the bot and never could — apps are forbidden from mentioning bots,
and the prohibition is implemented not as a refusal but as a silent edit.

The hour of waiting cost exactly one unchecked line: reading the published
comment back and comparing it with what was sent would have been enough.

## Why

A success code answers "was the request accepted", not "what is now stored on
the other side". Between the two stands the platform's right to normalise, and
it exercises that right silently: a refusal would be diagnosable, a quiet edit is
not.

The asymmetry of cost lies in the shape of the failure. A refusal is visible
immediately and costs one investigation. A silent rewrite turns into WAITING for
a reply that will never come: nobody erred, nothing broke, and the time goes into
patience. The more important the published text, the longer it is waited on.

Worth knowing in advance: defusing mentions is neither a bug nor a rarity.
Platforms do it deliberately so an app cannot summon people and bots in someone
else's name. So any automation whose text is meant to trigger an action will meet
this by design, not by accident.

## In practice

- read back what was published and compare it with what was sent, using the
  address the same call returned;
- compare not the whole text but the part the publication exists for: the
  mention, the command, the link;
- a mismatch is its own outcome: not a failed publish and not a success, but
  "published, but not what was sent";
- there is no need to read everything back: the subject exists where the text is
  ACTED on. A note for the record needs no delivery.

## Where it applies

**Works** for automation publishing, through a third-party service, text meant
to cause the recipient to act: bot commands, mentions, trigger links.

**Does not work** for text nobody is obliged to read: logs, explanations,
summaries. There a read-back adds a call and no knowledge. Nor does it apply
where the delivery platform is not an intermediary but your own code.

**Sign of violation:** automation waits for a reply to published text without
ever reading that text back after publishing.

## Trace

ArtVsMark/ArtVsMark#134 — the change was left waiting for the owner's click; the
conclusion is recorded in `HISTORY.md`

Related: [039](039-three-outcomes-not-two.md) — "published, but not what was
sent" is exactly the third outcome that was missing here;
[049](049-derive-state-from-live-artifacts.md) — state comes from the live
artefact, and a response code is not the live artefact of what was published;
[186](186-exit-code-flips-meaning-in-apply-mode.md) — there the number meant
something other than the reader assumed; here it meant exactly what it said, and
the assumption was about a different question.
