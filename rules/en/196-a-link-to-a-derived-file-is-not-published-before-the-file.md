# A link to a derived artefact is not published before the artefact itself

**Area.** showcases, pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** A link to a derived artefact does not reach the shared branch
before the artefact has been rendered. The ordering is secured one of two ways:
the run that renders it also adds the block of links, in the same pass; or the
link ships as a separate change AFTER the first run. A "the file exists" check
does not fix this: on the change under review the file must not be there.

**Portable beyond Claude Code.** yes — the subject exists for any project whose
derived files live outside the shared branch: badges, images, coverage reports,
generated documentation.

## The incident

The profile showcase `ArtVsMark/ArtVsMark`, 7 September, **twice in one shift
and in the same file**.

The first time: change #145 added a block to the README linking four images on
the `assets` branch that were not there yet — they are rendered by the daily
build, which runs AFTER the merge. The profile displayed four broken images
until the owner triggered the run by hand. The lesson was written into the
changelog in that same pass.

The second time, hours later: change #147 moved the block to a new layout and
added a fifth image. The README again reached the shared branch ahead of the
run, and the profile again showed broken content — plus the old images squeezed
to half width by the new layout.

**Compliance measured: 0 out of 2.** The rule was derived, written down, and
broken by its own author, in the same file, on the same day.

**What was tried first.** The obvious fix is a gate: "the file a link points to
exists". It is wrong by construction — the derived file lives outside the shared
branch, on the change under review it is not there and must not be, and such a
gate would go red on EVERY change that touches the showcase
([051](051-warn-on-likely-block-on-certain.md)).

## Why

While the derived file sat next to the text, the ordering was secured by the
storage itself: link and file travelled in ONE commit and could not appear
apart. The guarantee was not discipline — it was that there was no other way.

Moving the derived file to a separate branch
([160](160-derived-artifacts-live-off-the-branch.md)) removes that guarantee,
and the loss goes unnoticed, because what is lost is not a mechanism but the
IMPOSSIBILITY of the mistake. The work looks the same: same file, same link,
same change. A window opens between merge and first run that did not exist
before.

**The asymmetry of cost here is unusual.** A broken link is visible not to the
author but to a stranger: on a profile page, in a consumer's README, on a
project's front page. The author sees it last, and only by going to look. That
is why "next time I will trigger the run by hand" is not a fix — 0 out of 2 is
exactly what that measured.

## In practice

- the decision is made BEFORE the link is written: who will add it, the run or
  the next change;
- "I will trigger the run by hand after the merge" does not count as a
  decision: that is discipline, and it has already scored 0 out of 2;
- the "file exists" gate is neither suitable nor built: by construction the
  subject is not in the change's tree;
- a run that adds the link keeps the same ordering internally: render first,
  write the link second — otherwise the window merely moves inside the run.

## Where it applies

**Works** wherever a derived file lives outside the shared branch: badges on a
separate branch, images in `assets`, reports assembled by a run, showcase
pages.

**Does not work** when the derived file sits in the same branch and the same
commit: there the storage holds the ordering and the rule adds nothing. Nor
does it work for a link to SOMEONE ELSE'S resource — that is a different
subject, held by [194](194-a-name-is-not-proof-of-ownership.md): you do not
order the appearance of what is not yours.

**Sign of violation:** a change adds a link to a path that is not in the tree
and must not be, and does not say who will put the file there, or when.

## Trace

ArtVsMark/ArtVsMark — ArtVsMark/ArtVsMark#145, ArtVsMark/ArtVsMark#147

See also: [160](160-derived-artifacts-live-off-the-branch.md) — it is what
creates the subject: moving the derived file off the shared branch removes the
guarantee everything rested on;
[002](002-rule-without-mechanism.md) — knowledge in someone's head is not a
mechanism, and here that was measured on the rule's own author on the day he
wrote it;
[051](051-warn-on-likely-block-on-certain.md) — the obvious "file exists" gate
would go red on correct work, which is why it is not here;
[125](125-a-generated-file-is-not-a-store.md) — a derived file is not a store;
the corollary is here: since it is assembled, it has a MOMENT of appearing, and
that moment is accounted for.
