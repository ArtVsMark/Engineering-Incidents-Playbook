# There are two deadlines: one for starting, one for working

**The rule.** A time limit on execution does not cover **startup**. You can hang
before the first line, and that needs its own, short deadline. Raising it locally
is allowed; the default stays short.

## The incident

The time limit covered the work of an **already started** process. It turned out
you can block earlier — in spawning the process itself, while reading the service
channel after launch. The calling thread stays blocked **forever**: the work never
began, so its limit is not yet in force.

A separate startup deadline appeared: twenty seconds, while a healthy start takes
milliseconds even on a slow machine.

Then the second lesson. On slow build machines spawning a process consistently
took tens of seconds, and **three different tests went red for that single
reason**: what failed was not the code but the interpreter's launch. The solution
was an environment variable raising the limit for that particular machine.

The default was **deliberately not raised**. Twenty seconds distinguishes "hung
forever" from "the system is under load"; raising it to a minute and a half would
force everybody to wait that long during a genuine hang.

## Why

A time limit always covers a **phase**, not the whole operation. There are
usually more phases than you think: connection, handshake, startup, work,
shutdown. The hole forms between phases — where the previous limit has ended and
the next has not begun — and that hole is what produces an eternal hang.

Second: **the default and the ceiling are different quantities**. The default
answers "how quickly to report a hang", the ceiling answers "how long to wait in
the worst known case". Merged into one number, you must choose between false
positives on a slow machine and eternal waiting on a healthy one. Split, both
problems are solved: the default is short, and the ceiling is raised where the
environment is known to be slow.

## In practice

- enumerate the phases of the operation and make sure each is covered by a limit;
- the startup deadline is orders of magnitude shorter than the working one: it
  catches a hang, not slowness;
- it is raised **locally** — by an environment variable or a setting — and that
  does not change the default for everyone;
- junk in the setting's value (empty, non-numeric, zero, negative) is read as "not
  set": a check that fails because of a typo in the configuration is worse than
  no check;
- the message on firing names the phase: "never saw it start" and "the work ran
  too long" lead to different actions.

## Where it applies

**Works** for spawning processes, network requests, database connections,
external calls.

**Does not work** for operations with no distinct phases — there one limit is
everything.

**Sign of a hole:** a hang in which no deadline fired.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/use/configuration.md` § the deadline on
process LAUNCH itself (`STEPIK_GRADER_LAUNCH_TIMEOUT_S`).
