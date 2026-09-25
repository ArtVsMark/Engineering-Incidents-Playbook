# A list the platform returns in pages is read to its end, not by its first page

**Area.** API, reliability

**Tier.** 4 — code and tests

**The rule.** A list the platform returns in pages — a change's files, issues,
comments, labels, checks — is read by a mechanism **to its end**. While the
list is shorter than a page, nothing shows the difference: the run is green and
the request in the code is sound. Once the list crosses the edge, the tail
disappears without a single line, and what disappears is what the list was
read for. A single request is legitimate only as a **deliberate limit** ("the
latest N"), and then the limit is named next to the request.

**Portable beyond Claude Code.** yes — any API with lists has pages: GitHub,
GitLab, issue trackers, cloud consoles.

## The incident

**THE NEIGHBOUR'S MEASUREMENT, WHICH THE PROPOSAL CAME FROM** (the mechanisms
project, 23.09.2026): three occurrences in a day. A drift source read the
checks on the shared branch head as one page of a hundred, and there were
nearly ninety of them. Check annotations were read with the default page of
thirty. A measurement over the tree found the same move in seven calls across
five steps, although a paging helper already existed in the tree — nobody
called it. The measurement showed no lost case, and that is the point: a loss
would have looked exactly like "all green".

**HERE ONE AND THE SAME LIST IS READ IN TWO WAYS.** Since 07.09 (#366)
`.github/workflows/ci.yml` reads a change's files page by page, and the comment
there names the reason: a larger change would silently lose its tail.
`scripts/check_overlap.py::files_of` reads the same list as one page of a
hundred. Of 540 first-parent commits on the shared branch, four crossed a page
of a hundred: 358 files (#327), 306 (#195), 257 (the merge of #4) and 109
(#174). For such a change, overlap with its neighbours would be computed from
its first hundred files.

**AND ONE READ THAT WILL CROSS THE EDGE FOR CERTAIN.** `scripts/sync_inbox.py`
looks for the consumer's inbox issue among issues **of every state** in one
page of a hundred. The issues endpoint also returns changes, newest first. Once
a hundred issues and changes have been opened after the inbox, it drops off the
page, the next run does not find it and opens a second one. At the mechanisms
project numbers went from #607 (21.09) to #749 (24.09): a hundred takes three
days.

**The inventory of the tree on 25.09** — 19 list reads with a single request.
Four are deliberate, named limits: the latest open changes
(`check_overlap.LIMIT`), the latest merged changes (`review_findings.снятые`,
"the depth is limited on purpose"), the latest runs (`--limit 40` in
`main_red.py` and `automerge.yml`). Fifteen are one page with no named limit:
a change's files, issues in a marker search (seven places), comments on a
change or an issue (two places, and there the order is **oldest first**, so
what gets lost is exactly the newest), labels, open changes, and head checks
(three places, with the default page of thirty).

## Why

**A short list differs from a long one only in length.** Code, run and the
fake in the suite agree: the fake returns a short list, and the first page
equals the whole list. The difference is born in the live list when it grows
to the edge — and at that moment nobody is looking.

**What is lost is the tail, and the tail is not a random part.** The issue list
runs newest first, so what falls over the edge is the oldest — the issue opened
before all others, which is the inbox. The comment list runs oldest first, so
what falls over the edge is the newest — the latest verdict. Order decides
which part is lost, and it is almost always the part the list was read for.

**Paging costs one request while the list is short.** Reading a short list page
by page is the same single request; only a long list pays, and it pays for
exactly what it would otherwise lose.

**This is not [075](075-a-guard-that-finds-nothing-must-fail.md).** 075
requires failing when the subject is absent altogether. Here the subject is
present and part of it is found — which is exactly why the emptiness that
would make a gate fail under 075 never arises.

## In practice

- the list is read page by page: `gh api --paginate`, and parsing goes per
  element, not per page — `--jq` is applied to each page separately, so "the
  first of the list" becomes "the first of every page";
- a deliberate limit is named next to the request, with its reason: "the
  latest N", "past this horizon a resolution is not looked for";
- the order in which the list is returned decides what is lost. Name it when
  the limit is deliberate: a "latest" limit on an oldest-first list cuts off
  exactly the latest;
- a marker search among issues of every state is the first candidate for the
  edge: a hundred is reached by issues and changes together.

## Where it applies

**Works** for platform lists returned in pages: a change's files and comments,
issues, labels, checks, annotations, runs.

**Does not work** for requests with a deliberate limit named next to them: "the
latest N runs", "the last 30 merged changes". There the limit is a decision,
not a forgotten edge. **Does not work** either for single objects: a change, an
issue, a file by path have no pages.

**Sign of a violation:** a request for a list with no paging and no named limit
next to it.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `tests/test_lists_are_read_to_the_end.py`

See also: [075](075-a-guard-that-finds-nothing-must-fail.md) — emptiness makes a
gate fail, while here there is no emptiness, a tail is lost;
[169](169-cron-is-a-hint-not-a-cadence.md) — a platform's promise about
frequency does not hold, and here the promise "the whole list" holds only up to
the page edge; [001](001-transport-rest-not-graphql.md) — reads go over REST,
and paging is a required part of that.
