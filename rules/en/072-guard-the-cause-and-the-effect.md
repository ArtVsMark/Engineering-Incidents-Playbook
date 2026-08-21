# The gate catches the cause, the fixture catches the effect: you need both

**The rule.** One defence checks intent before the run, the other checks the
consequence after. Each is blind exactly where the other sees.

## The incident

A test passed a made-up absolute path into the product. While that parameter set
only the serving root, the path bothered nobody. When it also became the settings
root, the product started reading and **writing** through it — a directory with a
settings file appeared on the developer's disk.

Weeks later that file broke the test itself: a setting resolved to the opposite
value, and **only on the machine where the directory had appeared**. In the
shared build the test stayed green: writing to the root does not succeed there at
all.

Hence a division of labour. The fixture catches **the fact** of the file
appearing — but only where it appears, that is, on the developer's machine and
after the contamination. A separate check catches **the cause** before the run:
the argument list passed directly into the call contains no string literal
resembling an absolute path. It works even where no trace is left.

## Why

A defence "by fact" sees only what materialised in its own environment. Precisely
those environments where the breakage is harmless are the ones that show it —
while the environments where it is harmful learn of it last.

A defence "by cause" does not depend on the environment: it reads intent in the
source text. But it cannot see anything built dynamically, and so cannot be the
only one.

Hence a third observation, paid for in weeks: **the check is deliberately
narrow**. It looks only at literals standing directly in the call; a list
assembled from parts is not checked. That legitimately exempts calls to external
utilities where system paths are unavoidable and safe. Widening the scope would
produce false positives where everything is correct — and teach people to bypass
the check.

## In practice

- the pair has a stated division: one covers "before", the other "after", and
  that is written down, or the second will be taken for a duplicate and removed;
- the static check's scope is narrow and described: it says what it does **not**
  catch;
- the dynamic defence has an environment signal: it must stay honestly silent
  where it cannot fire, rather than creating the appearance of coverage;
- both name the same breach in the same words — otherwise they are taken for
  different rules.

## Where it applies

**Works** for breaches that do not manifest everywhere: platform-dependent,
rare, cumulative.

**Does not work** where the breakage reproduces identically everywhere — one
defence is enough.

**Sign that it is needed:** a test is green in the shared build and red on one
machine.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_test_isolation.py`,
`tests/conftest.py` (`_no_writes_outside_tmp`), #997.
