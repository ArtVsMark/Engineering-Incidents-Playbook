# A file list from git is read by NUL, and the check states its coverage

**Area.** code, gates

**The rule.** When listing paths from git in order to **read** them, pass `-z`
and split the output on NUL. Without it git escapes names containing non-ASCII
characters and spaces, the reconstructed path does not resolve, and the file
drops out of processing silently. A check that reads such a list must print its
**coverage** — how many paths were examined and how many were skipped: with no
number, its blindness is indistinguishable from a clean result.

**Portable beyond Claude Code.** yes — the subject belongs to any code that
takes a file list from git and then opens those files: a linter, a bundler, a
secret scanner.

## The incident

A consumer's pre-push job runs four gates and scans the files of the coming
commit for secrets. The list was taken as
`git ls-files --cached --others --exclude-standard`, split on newlines.

Tested against forged data: a file carrying an obvious platform token was
dropped into the root. The job returned `0` and printed "all clean: 5 checks".
The token was not found. Of twenty-nine files, twenty-eight were scanned — the
single invisible one was named `утечка.py`, in Cyrillic.

The first attempt to test the gate had used a file with a Latin name. That one
was found, and the check looked healthy — the forgery had confirmed precisely
the case that does not break.

## Why

The mechanism is three steps, each harmless on its own. `core.quotePath=true` is
git's default, so a non-ASCII name comes back escaped: `"\321\203\321\202..."`.
The code builds a `Path` from the escaped string, no such file exists on disk,
and the read fails with `OSError`. Finally the handler
`except (OSError, UnicodeDecodeError): continue`, written for binary files,
swallows it without a word.

The asymmetry of cost is as sharp as it gets. A missed file in a secret scan
costs a leak; an extra parse costs nothing. And the blind spot did not land on
an exotic case: the project is written in Russian, so what became invisible was
the **most likely** name, not a rare one.

The second half of the rule — coverage — is not there for symmetry. Silence from
a check means both "found nothing" and "looked at nothing", and the reader has
no way to tell them apart
([075](075-a-guard-that-finds-nothing-must-fail.md)). A count of what was
examined makes those two states different.

## In practice

- `-z` on `ls-files`, `diff --name-only`, `status --porcelain` — and splitting
  on `\0`, not on `\n`;
- an `except` written for one expected case is not widened to its neighbour:
  `OSError` next to `UnicodeDecodeError` turns a broken path into a skipped
  file;
- coverage is printed as a count of what was examined, not as the word "clean";
- the forgery for such a gate is built from the project's most likely case: a
  name in the language the project is written in
  ([037](037-finding-status-depends-on-window.md)).

## Where it applies

**Works** wherever a path list comes from git and files are then **opened** by
it.

**Does not work** where the list is only printed for a human: escaping is
readable and harmless in output, and demanding `-z` merely adds noise. Nor does
it work where files are walked over the tree without git — there is nothing to
escape, and only the second half of the rule, coverage, survives.

**Sign of violation:** a check prints "clean" without saying how many files it
looked at.

## Trace

ArtVsMark/Claude-Code_Usage-Token — scripts/preflight.py, function
`tracked_files`; ArtVsMark/Engineering-Incidents-Playbook#214

Related: [075](075-a-guard-that-finds-nothing-must-fail.md) — a guard that finds
no subject must fail; here the subject was lost before the check ran, so failing
alone is not enough — a number is needed.
[037](037-finding-status-depends-on-window.md) — a finding obtained on the wrong
surface is only a hypothesis; 165 shows the other side: a forgery assembled from
the convenient case confirms a capability that is not there.
[116](116-the-collector-script-is-a-source-of-loss.md) — the collector itself is
a source of loss.
