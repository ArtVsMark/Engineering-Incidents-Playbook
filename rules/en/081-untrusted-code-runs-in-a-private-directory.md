# Untrusted code runs from a private directory, not from the shared temp

**Area.** security

**The rule.** A file that will be executed goes into a directory created for one
run and readable only by its owner. The shared temporary directory is untrusted
input, not a convenient location.

## The incident

The sandbox saved submitted code to a temporary file and ran it. The directory
was the shared system one — the very place everybody writes to.

The defect is that the interpreter puts **the directory of the executed file
first** on the module search path. So any file named after a standard library
module, planted in the shared directory in advance, would replace that library
for the submitted code — and the substitution would happen **before** its first
line.

Anyone with an account on the same machine can plant such a file, and they can
wait as long as they like: the file survives until reboot.

The fix: the directory is created for a single run, with owner-only permissions,
and removed entirely on completion.

## Why

The shared temporary directory has a property that is easy to overlook:
**others write into it**. Anything you put there sits next to somebody else's
content, and anything you read from there, or pick up implicitly, may be theirs.

"Pick up implicitly" is the key part. The danger is not that somebody reads your
file but the **name resolution rules**: module search path, executable search
path, default configuration. All of them look beside the file or in the current
directory, and all of them fire before your code does.

Second: a unique file name does not save you. The attacker does not need to guess
your name — it is enough to occupy the name of something you will **load**.

## In practice

- the directory is created for one run, owner-only permissions, removed entirely
  in the finally block rather than "at some point";
- removal in the finally block is mandatory on failure too: otherwise private
  directories accumulate;
- the same applies to executable search paths and environment variables: they are
  cleaned, not inherited;
- directory isolation is **not a substitute** for privilege isolation: it closes
  dependency substitution, not network access or writes outside the boundary.

## Where it applies

**Works** for running untrusted code, unpacking untrusted archives, processing
untrusted files.

**Does not work** as the only defensive measure: it is one layer among several.

**Sign of trouble:** the temporary file is created by a generic "give me a temp
path" helper and then executed.

## Trace

ArtVsMark/Stepik-Python-Grader — `src/stepik_grader/web/playground.py`,
ArtVsMark/Stepik-Python-Grader#799. Related:
[068](068-allowlist-not-denylist.md),
[070](070-a-heuristic-guard-fails-open-with-a-written-risk.md).