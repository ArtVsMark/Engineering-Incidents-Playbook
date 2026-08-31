# A tool you ship is named at the entrance, not in the changelog

**Area.** contracts, documentation

**The rule.** If a project ships **mechanisms** and not only text — an
onboarding command, an action, a ready-to-run job — then the entrance is
described with them: "connect with a command, not by copying". The list of
tools is **one**, and the entry documents link to it instead of keeping their
own. Copying is not forbidden; it is named as the fallback, with a reason —
who cannot use the tool and why.

**Portable beyond Claude Code.** yes — the subject belongs to any project that
has both documentation and tools meant for other projects: a library with a
CLI, a platform with actions, a shared rulebook with a generator.

## The incident

Measured on 31 August, when the owner said: entering a project can be done with
tools rather than by copying rules — and our documentation is not quite right.

- `scripts/onboard_consumer.py` — **the very command a project connects
  with** — was mentioned neither in `README.md`, nor in `START.md`, nor in the
  contract. The single place it appeared was `CHANGELOG.md`, on the day it was
  built.
- `main_red.py` and `link_trails.py` had been lifted out of the catalogue's own
  jobs with the explicit words "now available to consumers" — and were named
  nowhere in the consumer-facing documents; at home they figure only as our own
  self-tests.
- `START.md`, "the order of the first day of a new project", consisted of **ten
  links to templates and not a single command**.

The price shows up in the registry: of five declared consumers, three are
connected. The tool existed, worked and was ready — and all that time a new
project walked the only path described to it, copying by hand.

## Why

The tool and the entrance are written by different heads at different times.
The tool is written by whoever knows what they built; the entrance is read by
someone who knows nothing. Between them sits the changelog — a **third**
reader's document, answering "what changed" rather than "how to start"; a
newcomer never opens it ([022](022-one-canonical-document.md)).

Copying, meanwhile, is the default path, not a choice. Naming no tool, the
document leaves the reader nothing but doing it by hand — and earns a second
implementation of one algorithm that drifts from the first at the first edit
([090](090-shared-helpers-move-up-not-sideways.md)).

Hence the shape of the mechanism: a tool **declares itself** with a marker
rather than being guessed from words. That a script is "for consumers" is the
author's decision, not a property of the code: a catalogue gate also talks
about consumers while remaining a gate. Guessing from text would produce false
refusals, and those train people to skip red
([051](051-warn-on-likely-block-on-certain.md)).

## In practice

- one list of tools, and the entry documents **link** to it: a second list
  drifts from the first silently;
- a named address must exist — a promise people act on costs more than silence;
- the version in the connection example is pinned by the build
  ([035](035-version-is-never-edited-by-hand.md)): an entrance teaching a stale
  tag is worse than one with no example;
- copying is named outright, with a reason and an address for the templates: a
  ban with no alternative reads as "we don't want those without CI".

## Where it applies

**Works** for a project that ships mechanisms: a catalogue with an onboarding
generator, a library with a CLI, a platform with ready actions, a shared
rulebook with jobs for participants.

**Does not work** where only text is shipped: there is nothing to name, and the
requirement becomes an empty section. It also does not work for a project with
a single entry page: a separate connection document would be ceremony there —
the tool list lives in that same README, and the rule collapses into "name
them".

**Sign of violation:** a newcomer does by hand what a command already does — or
a tool is mentioned only in the changelog and in its own docstring.

## Trace

ArtVsMark/claude-code-playbook#148

Related: [155](155-a-template-you-dont-use-drifts.md) — a template you don't
use yourself drifts from practice; 163 covers the neighbouring gap: a tool you
do use yourself is not named to the people it was built for;
[022](022-one-canonical-document.md) — one canonical document, here the single
list of tools; [021](021-split-docs-by-reader.md) — the entrance is split by
reader, and someone connecting is a reader of their own, not a section of the
README; [090](090-shared-helpers-move-up-not-sideways.md) — a shared technique
moves up; copying instead of using the tool is its violation, invited by the
document.
