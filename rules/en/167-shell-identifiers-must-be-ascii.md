# Shell variable names are ASCII, even when the project is not written in it

**Area.** CI, code

**The rule.** A project's internal language does not extend to the shell: a
variable name in bash must consist of ASCII. The mistake shows up in two ways,
and the second is the dangerous one. An assignment with a non-ASCII name is
parsed as a **command name** — the job fails with code `127`, and that is
visible. But an environment variable with a non-ASCII name is created normally,
while `$NAME` does not expand at all: the parser wants an ASCII identifier, the
expansion comes out empty, and a condition written on such a variable always
takes the same branch. The gate stays **green** and checks nothing.

**Portable beyond Claude Code.** yes — the subject belongs to any project whose
internal language is not Latin script while part of its logic lives in the
shell.

## The incident

The consumer's project is written in Russian: docstrings, comments, error
messages and even Python identifiers are in Cyrillic, and its rulebook says so.

A gate was being built — "the changelog entry travels with the change" — as a
three-step job. The first step collected the changed files:
`файлы=$(git diff --name-only "$BASE...$HEAD" | tr '\n' ' ')`. The job failed at
once: bash parsed the line not as an assignment but as running a command named
`файлы=.github/workflows/changelog.yml`, output `No such file or directory`,
exit code `127`. It cost one cycle and announced itself.

The second case in the same file would not have announced itself at all. The
step "is an entry required?" received the change's labels through `env:` with
the keys `ТИП`, `ЧЕРНОВИК`, `ФОРК` and matched them as
`case " $ТИП " in *" bug "*)`. Environment variables with such names are
created, but `$ТИП` does not expand — the substitution is empty, no pattern
matches, `required` stays `no`, and the requirement switches itself off in
silence.

One and the same mistake produced a loud refusal in one step and a quiet "passed"
in its neighbour.

## Why

The difference is not in the shell but in where the name stands. In assignment
position the parser must see an identifier; failing that, it treats the word as
a command — and errs **out loud**. In expansion position it must see an
identifier after `$`; failing that, it substitutes nothing — and errs **in
silence**, because an empty string is a legitimate value.

Hence the asymmetry of cost. The first form costs one red job. The second costs
a gate: it ran, returned zero and checked nothing, and the only way to tell it
from a working one is to know what it was supposed to reject
([075](075-a-guard-that-finds-nothing-must-fail.md)).

The temptation comes from the neighbouring language: in Python a Cyrillic
identifier is legal and works, so "we write in the project's language" carries
over into the `.yml` file by inertia — where messages and comments sit right
next to it, and there it is true
([013](013-write-escapes-to-file-not-heredoc.md): two interpreters in a row with
different parsing rules are enough to make what is correct in one an error in
the other).

## In practice

- shell variable names and `env:` keys are always in Latin script;
- prose, docstrings, message text and step names stay in the project's language;
  there is no constraint here;
- a variable's value may be anything: the rule is about the name, not the
  contents;
- a gate meant to **demand** something is run against the case where it must
  demand it: otherwise an empty expansion is indistinguishable from an honest
  "not required".

## Where it applies

**Works** for bash, sh and anywhere a name passes through a shell: job steps,
`env:`, build scripts.

**Does not work** for languages where Unicode identifiers are legal — Python,
JavaScript, Java. There a Cyrillic name works, and a ban would import someone
else's boundary; that is exactly why the mistake gets made.

**Sign of violation:** a job contains a variable with a non-ASCII name and the
step is green.

## Trace

ArtVsMark/Claude-Code_Usage-Token#10 — .github/workflows/changelog.yml, the steps
"collect the changed files" and "is an entry required?"

Related: [075](075-a-guard-that-finds-nothing-must-fail.md) — a guard that finds
no subject must fail; the quiet form of this mistake is exactly such a guard.
[013](013-write-escapes-to-file-not-heredoc.md) — two interpreters in a row parse
one string by different rules.
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — a gate is tested by what
it must reject.
