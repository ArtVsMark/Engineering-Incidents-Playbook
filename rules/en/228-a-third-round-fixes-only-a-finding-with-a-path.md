# From the third review round on one place, code fixes only a finding with a path from a real input

**Area.** code, quality

**Tier.** 4 — code and tests

**The rule.** From the third review round on one place — a gate, a window hook, a
parser inside a script — code fixes only a finding that names a path from a
real input to a wrong result: a file in the tree, a real call or a real window
run produces a false refusal, a false pass or a crash. The other findings of
that round are closed with a "Разобрано" line that gives a reason and carries
no code: a finding about text, about a message, about the shape of a test, or
about an input that does not exist in the tree.

**Portable beyond Claude Code.** yes — the subject exists in any team where an
outside eye reviews changes: a human reviewer also finds a new edge on every
gate fix, and the author also fixes it with the next change.

## The incident

**16–17 October 2026, six catalogue gates, one sequence.** A gate is built,
the review finds things, a fix closes them, the review of the fix finds new
ones — on the same gate. Measured from change bodies and reviews:

| Place | Round 1 | Round 2 | Round 3 | Round 4 |
|---|---|---|---|---|
| invisible characters | #874 — 3 | #905 — 2 | #907 — 2 | #909 — 0 |
| facts contract number | #901 — 1 | #904 — 2 | #907 — 1 | #909 — 0 |
| hook interpreter | #878 — 3 | #906 — 2 | #909 — 0 | — |
| mechanism-rule coverage | #891 — 4 | #908 — 3 | #909 — 1 | — |
| push guard deadlines | #882 — 3 | #883 — 2 | #887 — 1 | #910 — 1 |
| asking the family | #884 — 2 | #888 — 1 | #910 — 1 | — |

**For every finding from round two on, the path from a real input to a wrong
result was read.** In round two it exists for 1 of 12: a 10 s hook deadline
shorter than subprocesses of 60 and 600 s (#883) — a setting of the tree on a
real push. One more is conditional: `OSError` if `git` is missing. The other
10 named a `python-guard.sh` hook that is not in `.claude/hooks`, an invented
`echo` line with `;` inside quotes, a "broken `facts.version`" while the file
holds a valid `2.0.0`, a hand-written number in a fragment. From round three
on, no path was found for any of 7. One says that "only which selector is
named in the message changes" (#907): the gate's verdict stays the same. Two
more concern a number in a docstring and future records "rather than the
current tree" (#910). Each of them cost a change: push, run, review, merge.

**What worked, worked before the rule.** In #909 the window for the first
time closed two round-three findings with a "Разобрано" line and a reason:
"not worth its code" and "the boundary is named". The review of #909 found 0
on three of four gates. The chain was stopped not by an enumeration of forms
(210 was already in place by then) but by refusing to fix a finding without a
path.

## Why

**Every round's review looks at the new edge, not at the subject.** A fix
moves the gate's edge, and the next look finds what lies beyond it. While
beyond it lies a real input, that is work. Once the edge has moved past the
tree, the look keeps finding — hypothetical lines, names in messages, the
shape of a test. The number of findings falls more slowly than their worth:
each costs the same cycle, and the third round returns nothing.

**A path from a real input is the sign that tells one from the other.** A
finding with a path changes the gate's verdict on something that is or will
be in the tree. A finding without one changes text or a message, or guards
against an input nobody writes. Leaving the first unfixed costs more: the
gate lies. Fixing the second costs more: every fix moves the edge and starts
the next round.

**Why the third round and not the second.** Round one is the review of a new
gate, round two the review of its first fix; real paths still turn up there.
By round three the gate has passed the outside eye twice and been
fixed twice. The round-two measurement — 1 of 12 — says the threshold may
belong earlier; that is a question for the next measurement, not this one.

**Closing without code is a decision, not a skip**
([026](026-rejected-findings-must-be-recorded.md)). The "Разобрано" line
names the reason, and the next review does not reopen the finding: the path
was checked and not found, and that is on record.

## In practice

- **a place** is the same as in
  [210](210-a-second-finding-on-one-place-stops-the-patching.md): one
  question the code decides, not a file. A finding about another question in
  the same file is round one of another place;
- **a round** is the review of a change that edits this place. Round one is
  the review of the change that created it;
- a path is named by an input and a result: "file X of the tree / call Y
  gives a refusal instead of a pass". "One can imagine a line…" is not a path;
- a path that was looked for and not found is recorded as such: "Разобрано:
  <fingerprint> no path — <what was checked>";
- a finding without a path that is cheaper to fix than to write a
  "Разобрано" line is still closed without code: a cheap fix moves the edge
  just as an expensive one does;
- the threshold is revised by measurement. If round two keeps yielding a
  path less than once in ten, the threshold moves to round two.

## Where it applies

**Works** for code that decides on an input: gates, window hooks, parsers in
pipeline scripts — from the third review round on one place.

**Does not work** for security findings: there an input absent from the tree
is written by the attacker, and "no path" means "not written yet". **Does not
work** for a finding about a wrong fact in the change's own text — a number,
a path, a list: that is
[215](215-a-retelling-of-your-own-work-is-checked-against-its-source.md), and
it is fixed by editing the text, not code. **Does not work** for the first
two rounds: there findings are fixed in the usual order, and a repeated one
on the same place stops form-by-form patching under 210.

**Sign of a breach:** the third change in a row on one place fixes a finding
that names neither a file in the tree nor a real call — only "a line like",
"if" or a name in a message.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#912

Related: [210](210-a-second-finding-on-one-place-stops-the-patching.md) — a
second finding on a place stops form-by-form patching, while 228 says when
the chain of rounds stops altogether;
[026](026-rejected-findings-must-be-recorded.md) — a closed finding carries a
reason; [044](044-check-the-premise-before-fixing.md) — whether a finding is
true, while here — whether it is worth code;
[087](087-a-second-pass-needs-a-novelty-rule.md) — a repeated audit does not
reopen what was found.
