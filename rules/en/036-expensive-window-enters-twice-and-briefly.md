# The expensive environment enters an audit twice, and briefly

**The rule.** An audit runs in three phases: a short snapshot of reality
**before** the mass work, all the mass work in the cheap environment, and a
short confirmation against an accumulated checklist **at the end**. The
expensive environment does not repeat the cheap one.

## The incident

Two obvious schemes were tried in succession, and both were wrong.

The first: "run everything in the cloud, then do the same again locally". A
second pass over the same slices produced the same findings — a second run paid
for, nothing new gained.

The second: "the local phase at the end, if time allows". In the 2026-08-10
audit the browser was not opened until the fifth phase, and by the fifth phase
the limit was spent. Whatever is deferred to "if there is time" does not happen
at all.

## Why

The expensive environment is needed not for **repetition** but for what
**becomes observable there for the first time**. Everything observable in the
cheap one stays there.

Hence three phases, not two:

- **Phase 0** (expensive environment, minutes) — not defect hunting but
  collecting what the cheap environment cannot invent: the shape and volume of
  real data, real names, the OS version and launch method, diagnostic output
  with no secrets. From then on the waves work against the shape of the real
  thing rather than a fantasy: a fixture built from real names and volumes
  catches what a synthetic one misses.
- **Phases 1..N** (cheap environment) — all the mass work: reading code, role
  slices, runs, browser, document generation, tracker, verification.
- **Phase L** (expensive environment, hours) — executes **the accumulated
  checklist and nothing beyond it**.

The phase-L checklist is kept **from the first wave**, not assembled at the end.
An executor blocked by a missing entry point must produce not "skipped" but a
task line for the expensive environment. Then the final phase is an hour against
a ready list, not a second audit.

## In practice

- phase L always has at least one item — the full end-to-end scenario — so it is
  never empty;
- the reverse prohibition is just as hard: **mass work never moves into the
  expensive environment** — otherwise it stops being short;
- phase-L findings are fixed in the cheap environment; acceptance is expensive
  again but **targeted**: the same checklist, not the whole audit. One cycle,
  not an iteration;
- the gate that unblocks phase L is closing the issues whose fixes change
  **behaviour at run time**. Documentation issues do not block: a run does not
  read the README. Error messages and interface strings do count as code — they
  are visible in a run.

## Where it applies

**Works** where two environments differ by access to the real thing rather than
by power, and the expensive one is bounded by a person's time.

**Does not work** if both environments are equally available — then phasing is
bureaucracy.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/environments.md` § running an audit
across two environments
