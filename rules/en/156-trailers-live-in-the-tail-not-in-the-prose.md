# A trailer lives in the tail block, not in any line of the message

**Area.** process, pipeline

**The rule.** Commit message trailers are read only from the **tail block** —
the last paragraph, made entirely of `Key: value` lines. Parsing by "the line
starts with a trailer name" takes a prose mention for a directive, and it does
so more often the more carefully the message is written.

**Portable beyond Claude Code.** yes — the subject belongs to the commit
message format, not to agent sessions: git parses trailers the same way.

## The incident

On 30 August the catalogue's `scripts/check_attribution.py` rejected the
showcase's pull request `ArtVsMark/ArtVsMark#95`, naming as a co-author the
string "github-actions[bot] into the squashed commit. #83 made the author".

No such co-author exists. It is the middle of a sentence from a paragraph
explaining why the platform appends a trailer when authors disagree: the word
"Co-authored-by" stood in prose and, after a line wrap, happened to come first
on its line. A regular expression with `re.M` saw the start of a line and
missed the paragraph.

The cost landed twice. The change was fixing a **red main branch** — so the
rejection delayed the repair of the very gate that issued it. It was worked
around by rewriting the message: the author had to write worse than intended
for the parser's sake.

## Why

The error is asymmetric, and the bias points the wrong way: the attribution
gate rejects a change the more readily the more carefully its subject is
described. A terse "fix typo" never contains the word "Co-authored-by"; a
thorough explanation of how attribution works always does.

The failure mechanism is substituting **position** with the sign "start of a
line". A wrap inside a worked paragraph puts any word first without the
author's intent, and the longer the paragraph the likelier it is. A tail block
is immune: its boundary is a blank line, not the column width.

## In practice

- trailers come from the last paragraph, and only if **all** of its non-empty
  lines have the `Key: value` shape;
- a paragraph with even one prose line is not a tail block at all — otherwise
  the parser goes back to guessing;
- the same holds for reading any directive out of free text: a pull request
  body, an issue description, a comment.

## Where it applies

**Works** wherever a machine reads directives from text written for humans —
and especially where a false rejection costs more than a miss.

**Does not work** where the message format is machine-made end to end: a
templated message has no prose, and position adds nothing. Nor for trailers the
platform appends itself after a merge: their placement is its doing, not the
author's.

**Sign of violation:** the gate names as a "co-author" a string absent from the
agreed list, and in the message that string sits inside a paragraph.

## Trace

ArtVsMark/ArtVsMark#95

Related: [123](123-attribution-is-verified-on-the-final-history.md) — that same
gate is the subject of the fix; [051](051-warn-on-likely-block-on-certain.md) —
a false rejection on correct work costs more than a miss, and here it cost a
delay in fixing the main branch;
[141](141-a-marker-is-matched-whole-not-by-prefix.md) — the same error on
another surface: a sign taken by its part instead of whole.
