# A message points at what the recipient actually has

**Area.** interface

**The rule.** A hint to the user never sends them to a file, directory or name
that does not exist on their machine. The author sees a repository; the user sees
an installed package.

## The incident

Interface strings invited people to read documentation at a path inside the
repository. After an ordinary installation neither that directory nor the readme
**exists** on disk — so the hint led nowhere, and precisely for the person who
needed help most.

A second case of the same kind: a message about an optional feature advised
installing a package under a name the project **is not published under**.
Neighbouring lines in the same file spelled the name correctly — so the error was
not ignorance but the fact that nobody could verify it.

The fix for both is mechanical: links must lead outwards, and the package name
is taken from the project description so that renaming leaves no stale hints
behind.

## Why

The author writes the message while looking at their own file system, and it
**does not resemble** the recipient's. The difference is not marginal: the author
has sources, history, tooling and context; the user has an installed package and,
at best, network access.

Second: such errors are caught by neither tests nor review. A test verifies that
the string is shown; a reviewer reads it in the repository, where the path
exists. The error lives exactly in the gap between two pictures of the world —
which is why a dedicated check is needed.

Third: the cost is asymmetric. A wrong hint meets the person at the moment they
are **already stuck** — and instead of help they get a second dead end.

## In practice

- links in user-facing strings lead outwards, to an address reachable without the
  sources;
- package names, commands and paths come from a **single source** rather than
  being typed into prose;
- the check is mechanical: a string containing an internal path is a build error;
- the same rule applies to error text: "see such-and-such file" makes sense only
  if the recipient has that file.

## Where it applies

**Works** for any message leaving the team: interface, errors, emails,
installation documentation.

**Does not work** for internal diagnostic messages read by people who do have the
sources — there a path is exactly what helps.

**Sign of trouble:** the hint looks perfect when read inside the repository.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_locale_guardrails.py` (the items
on outward links and the package name), ArtVsMark/Stepik-Python-Grader#1005.