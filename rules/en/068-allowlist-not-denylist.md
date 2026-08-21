# An allowlist, not a denylist

**Area.** security

**The rule.** What we accept and what we serve is enumerated by name. A denylist
knows nothing about what appears tomorrow, and lets new things through in
silence.

## The incident

The server serves images from a task statement. The list of acceptable types is
an enumeration: five raster formats, each stated explicitly.

Vector graphics is **deliberately absent** from the list, and the reason is
recorded right next to the code: such a file can carry a script, and it is served
from our own origin — so it would be a hole through our own endpoint, bypassing
all the markup sanitisation.

A denylist would not have closed that hole: it enumerates known dangerous things,
while the danger here lies in a property of the format, not in its name. One new
format with the same property, and the ban misses again.

The same technique is applied to the command set: exactly what is implemented is
enumerated, with a note saying "do not append here". The list is a contract, not
a convenient constant.

**A second case, of a different kind: the names in the list belong to somebody
else.** An agent project's rulebook denied a third-party MCP server's tools by
name — twenty-nine `deny` entries, so that the expensive transport (GraphQL,
~300 units out of 5000 an hour) would be unavailable to the session.

The vendor consolidated the tools and **renamed them**: `get_issue`,
`list_issues`, `search_issues` and `get_issue_comments` became a single
`issue_read`; `list_workflow_runs` and `get_workflow_run` became `actions_list`
and `actions_get`. Not one of the twenty-nine denied names still exists.

The ban stopped working entirely — and **said nothing about it**. An entry that
matches no tool is indistinguishable from one that fired: silence either way. It
surfaced weeks later, through a manual reconciliation.

## Why

Allowlists and denylists err in **opposite directions**, and that settles
everything. An allowlist with a gap refuses something legitimate — noticeable,
fixed in a minute. A denylist with a gap **lets something dangerous through** —
unnoticed, and discovered by its consequences.

Second: an allowlist is finite and known. The set of dangerous things is bounded
by nothing and grows by itself — new formats, encodings, schemes. Nobody manages
to keep a denylist complete.

Third, organisational: an allowlist **makes addition a decision**. To accept a
new format you must add a line — and at that moment somebody wonders whether it
is safe. In a denylist, the new thing passes on its own, with no decision at all.

Fourth, and in the second incident this is the whole of it: **whose names are in
the list**. The gap there did not come from incompleteness — the subject of the
ban was still present and its properties had not changed. What changed was the
**name**, and the name is owned by somebody other than the author of the list. An
allowlist would have failed loudly in the same situation: a tool under a new name
would not be found in `allow` and would be refused on the first attempt. Hence
the general sign: a list built on somebody else's identifiers goes stale on
**their** release schedule, not yours, and stays silent until it does.

## In practice

- next to each exclusion from the list, **the reason for the exclusion**, not a
  silent absence: otherwise the next person will read it as an oversight and
  "complete" it;
- the list is a contract: it has a place, a test, and a note on who may change
  it;
- a rejection says **what exactly** was not accepted, or a legitimate user will
  not know what to do;
- a list that refers to **external identifiers** must verify that they exist: an
  orphan entry is a failed check, not silence
  ([075](075-a-guard-that-finds-nothing-must-fail.md)). Otherwise the protection
  lasts until the vendor's next release;
- where an allowlist is impossible (free-form input), protection comes not from
  filtering but from handling: escaping, isolation, restricted permissions.

## Where it applies

**Works** for file types, URL schemes, fields, commands, request origins.

**Does not work** where the set of acceptable values is open by design —
filtering user text through a list is meaningless.

**Sign of trouble:** the list grows after every incident. For a list built on
somebody else's names — not one entry has ever fired, and nobody finds that odd.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/statement_adapter.py`
(`_IMAGE_TYPES`), `web/commands.py`. The second incident —
ArtVsMark/Stepik-Python-Grader#1346, predecessor #1280. See also:
[075](075-a-guard-that-finds-nothing-must-fail.md).
