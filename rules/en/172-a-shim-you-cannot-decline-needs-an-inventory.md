# A shim you cannot decline is answered with an inventory

**Area.** architecture, data

**The rule.** When compatibility is held not by your code but by the
**platform**, and cannot be switched off, the rule
[094](094-a-compatibility-shim-makes-migration-permanent.md) — "break it now and
visibly" — is inapplicable by construction: the old path keeps working whatever
you decide. So there will be no signal of an unfinished migration at all: no red
run, no broken link. The only thing that can replace it is an **inventory** —
list every place the old name is written and check them against a live source
([049](049-derive-state-from-live-artifacts.md)), not against a constant in the
code. Sign that the rule applies: a migration with no way to make the old path
stop working.

**Portable beyond Claude Code.** yes — the subject belongs to any platform
compatibility you cannot disable: a rename redirect, a domain alias, an old
package name kept alive by a registry.

## The incident

The owner renamed three repositories in one day. In the consumer's tree the old
names were written in **twenty places across fourteen files**: version badges,
task links in both showcases, three addresses in the issue templates, the project
URLs in the manifest, the consumer's and the catalogue's addresses in its answer,
six trace fields in its proposals and — the costliest — 
`uses: ArtVsMark/claude-code-playbook@v1.1.0`, that is, the **only** link to the
rule catalogue.

Measured after the rename: a manual run — green, the action resolved through the
redirect under its old name; the full eight-gate pre-push run — green throughout,
with all twenty stale addresses in place. No mechanism noticed anything, and none
could: the platform's redirect removes precisely the failure that would have been
the signal. The drift was found not by a check but because a human said it aloud.

The same thing had happened to the catalogue itself and was found while admitting
this very proposal: the consumer registry named its neighbour by the old name,
both addresses — old and new — answered `200`, and no gate went red.

## Why

An ordinary migration announces itself through **breakage**: the old path stops
working, and that is visible. Here there is no breakage and there will be none —
"it works" is the platform's default, not a consequence of your edit. So the
usual instruments are useless all at once: the run is green, the link is alive,
the integrity gate is content.

The asymmetry of cost lies not in degradation but in **capture**. The redirect
holds while the old name is free; the moment anyone else claims it, `uses:`
starts pulling somebody else's action — somebody else's code with the right to
write to your tracker under your token. Deferring the cleanup changes the class
of the problem: from hygiene to security.

Hence the shape of the answer. An inventory is not a list of "things we ought to
fix" but a comparison of the declared against the live: every place the name is
written is checked against a source that knows the current name. And the
inventory must tell a **live address** from **history**: an old trace in a record
about a past incident must not be rewritten
([114](114-migrate-from-the-current-version-not-from-zero.md)), while an address
people follow today must be.

## In practice

- the inventory lists places, not intentions: file, line, and what it is — an
  address or history;
- searching the tree for the old name is legitimate here: the subject is the
  presence of the string itself, not a relationship
  ([166](166-check-the-link-not-the-path.md));
- `uses:` and anything else that executes foreign code is fixed first and pinned
  by SHA;
- the live source is the platform, not a constant in the code: the name is asked
  of `origin` or of the API, or the inventory compares a copy with a copy;
- after the inventory, its result becomes a check — "the old name is absent from
  the tree" — or the next rename passes just as quietly.

## Where it applies

**Works** where the old path stays alive not by your decision: a repository
rename, a domain alias, an old package name in a registry.

**Does not work** where the old path can be made to stop working — there
[094](094-a-compatibility-shim-makes-migration-permanent.md) governs, and it must
break now and visibly. Nor does it work where the name is written in a single
place: a one-line inventory is ceremony, not a mechanism.

**Sign of violation:** the rename went through, every run is green, and nobody can
state how many places carry the old name.

## Trace

ArtVsMark/Claude-Code_Usage-Token — .github/workflows/rules-inbox.yml,
.rules/bindings.json, both showcases; ArtVsMark/Engineering-Incidents-Playbook#214
— .rules/consumers.json, where the same drift survived until the inventory

Related: [094](094-a-compatibility-shim-makes-migration-permanent.md) — a shim
makes migration permanent; 172 covers the case where the shim is not yours to
place.
[049](049-derive-state-from-live-artifacts.md) — state is derived from a live
artifact, and that is what the inventory checks against.
[114](114-migrate-from-the-current-version-not-from-zero.md) — the past is not
rewritten; the inventory tells history from a live address.
[166](166-check-the-link-not-the-path.md) — a relationship check looks for the
link; here the subject is the opposite, and a substring search is exact.
