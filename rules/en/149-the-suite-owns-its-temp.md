# The suite takes the shared ground over, it does not add it to the exclusions

**Area.** tests, gates

**Tier.** 3 — gates and processes

**The rule.** When a guard is noisy about a resource that the code under test and
everything else on the machine reach the same way — the system temporary
directory, the home folder, a shared cache, a fixed port — the fix is
**ownership**, not an exclusion list: for the duration of the run the suite
redirects the resource into a place it owns. An exclusion by name leaves the
ground shared and silences a real finding along with the noise.

## The incident

The guard watched that no test wrote outside its own temporary folder, and it
named as the culprit whoever it was completing when it noticed the change.

The noise came not from a neighbour on the machine but from **the product
itself**: the "Playground" section creates a private `stepik-playground-*`
directory in the shared system temp for the code it runs. It lives there
deliberately — a security decision: the interpreter puts the script's own
directory first on the module search path, so a foreign `json.py` planted in the
shared temp would shadow the standard library for the code being run. The
directory lives for a fraction of a second and is always removed.

But the guard's snapshot could land exactly inside that fraction — and then the
accusation went to an **unrelated** test. That is what happened in CI: the red
test wrote strictly inside the task folder, and a re-run of the same commit was
green.

An exclusion by prefix suggested itself — the very move that was the right
answer in another incident
([103](103-a-side-effect-guard-blames-the-wrong-suspect.md)). Here it is wrong:
there the noise came from a foreign process the suite does not control, while
here it is our own code, which is precisely what the guard exists to watch.
Adding `stepik-playground-*` to the exclusions would mean that a directory which
one day stops being removed goes unnoticed.

The opposite worked: the suite moved the system temp inside its own temporary
root. For the duration of the run there is no shared temp at all — any code that
does not name a directory writes where the guard allows writing. The product did
not change by a single line.

## Why

**An exclusion widens the blind spot permanently; a redirect does not.** A name
added to the tolerated list stops being checked in exactly the cases the guard
was written for: a leaked directory, a forgotten file, growing debris. Moving
the ground cancels no check — it relocates it onto the suite's territory, where
the suite's own cleanup applies.

**Foreign noise and your own noise have different cures.** A neighbouring
process does not obey the suite: you negotiate with it by the shape of the name.
Your own product does obey — so the shared ground can be taken from it whole,
and that is cheaper than enumerating every name it will ever create.

**A race does not reproduce, so it cannot be fixed by observation.** The red
lands on a random test, the re-run is green, and a fix aimed at the victim's
name treats the wrong end. Removing the shared ground clears the entire class at
once, regardless of whose teardown would have spotted the difference.

## In practice

- the redirect is set **twice**: in the environment variables (a subprocess sees
  those, and never the parent's module-level variable) and in the library's own
  module-level variable (which the environment can no longer reach once the
  directory is cached);
- the new root goes inside the suite's temporary root: then the same mechanism
  cleans it as everything else, and the guard counts the entry as lawful without
  a single exclusion;
- a test whose subject **is** the shared resource (path resolution, behaviour
  when temp is unavailable) drops the substitution locally: a session-wide
  redirect must not make such a test untestable;
- the product is left alone: in production the shared ground stays shared —
  otherwise the suite starts checking a different program from the one the user
  will get.

## Where it applies

**Works** for resources with a supported redirection point: the temporary
directory (`TMPDIR`/`TEMP`/`TMP`), the home folder (`HOME`), tool caches
(`XDG_CACHE_HOME`, `PIP_CACHE_DIR`), databases and settings whose path comes
from the environment.

**Does not work** where the path is hard-coded past the environment (then the
redirection point has to be added first, and that is a product change), nor
where the noise comes from a process the suite does not control — a neighbour on
the machine is handled by the shape of the name
([103](103-a-side-effect-guard-blames-the-wrong-suspect.md)), because there is
nothing to take the ground away with.

**Sign of trouble:** a name created by **your own** code shows up in the guard's
tolerated list.

## Trace

ArtVsMark/Stepik-Python-Grader — `tests/conftest.py`, the
`_system_temp_inside_basetemp` fixture: the system temp is moved inside the
pytest basetemp for the run, and `tests/test_conftest_temp_root.py` asks the
running "Playground" where its own file lives.

Related: [103](103-a-side-effect-guard-blames-the-wrong-suspect.md) — the same
guard with the opposite answer for a foreign process;
[072](072-guard-the-cause-and-the-effect.md) — guard the cause, not only the
effect.