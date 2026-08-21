# Everything that can fail happens before you replace global state

**The rule.** Parsing input, validating arguments, compiling — all **before**
acquiring a resource or replacing shared state. Otherwise an exception leaves the
system replaced, and the user gets an internal error instead of their own.

## The incident

The tracer replaced standard output with a buffer to collect the solution's
output, and only then compiled the code.

Broken syntax — an everyday matter for a learner — broke that sequence twice.
Called in-process, the exception flew out **leaving the output replaced**: all
subsequent output from the process was lost. Launched as a separate process, the
loader itself crashed, and instead of a simple "syntax error on line 2" the user
got an internal error with a truncated trace through the tool's own files.

The fix is twofold. Compilation moved **before** the replacement and got its own
catch. And, more importantly, a syntax error was recognised as a **normal
outcome**: it is returned in the same result field as a runtime error rather than
counted as a failure of the tracer.

The same logic elsewhere in the same product: command-line arguments are parsed
**before** the window is created. Help and version must work where there is no
display at all, and an unknown flag must be rejected rather than ignored.

## Why

The order "acquire first, validate second" turns any input error into **two**
errors: the failure itself and corrupted state. The second is worse: it shows up
later, elsewhere, with nobody able to connect it to its cause.

Hence the order: first everything that can fail and **drags nothing behind it**;
then acquisitions, replacements and resource creation. Then a failure in the first
stage requires no rollback at all.

The second half of the rule is about **whose failure this is**. An error in the
user's input is part of the domain, not a failure of the tool. If it arrives as an
internal exception, the person sees our trace instead of their error and can fix
nothing. An expected failure must come back through the **normal result channel**,
alongside success.

## In practice

- enumerate what can fail and lift it to the front;
- acquisitions and replacements go under guaranteed restoration, even when "there
  is nothing here that can fail";
- input errors are enumerated and returned as a result field, not as an
  exception;
- the catch during input parsing is narrow and typed: a broad one at this stage
  hides a genuine breakage of the tool.

## Where it applies

**Works** for running untrusted code, parsing input, working with global state,
transactions.

**Does not work** if the input can only be validated inside the acquired resource
— there you need guaranteed rollback rather than ordering.

**Sign of a breach:** after an input error, something unrelated turns out to be
broken.

## Trace

ArtVsMark/Stepik-Python-Grader — `core/tracer.py` (#806), `launcher.py` (#1135).
Related: [067](067-cleanup-must-not-swallow-the-failure.md),
[056](056-a-signal-states-what-it-does-not-mean.md).
