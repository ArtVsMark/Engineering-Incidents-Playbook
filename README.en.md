# Engineering Incidents Playbook

> **Reader:** visitor — what this is and whether to take it.

[![Project: checks, Python, OS, coverage, release and version on top; rules held by mechanisms — own and taken — and the family check below](https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook/badges/.github/badges/project.svg)](#the-project-family)

**A catalogue of <!--m:rules-->215<!--/m:rules--> rules for Claude Code and GitHub,
where every one grew out of a real failure.** Agent sessions and the project rulebook (`CLAUDE.md`), the
GitHub delivery pipeline, parallel executors, audits. Every record comes with its
history: what broke, how it surfaced, what it cost.

> 🇷🇺 [Русская версия](README.md) · Unofficial, not affiliated with Anthropic.

**Start here:** [ten rules to start with](TOP-10.md) ·
[day-one order](START.md) ·
[the whole catalogue, by area](rules/README.md)

## Two roles — for outside projects and for the family

**To an outside project the catalogue hands out rules.** Badges and the facts
contract are optional; connecting does not require them.

**Boundary** (21 October): the catalogue is rules and skills, it defines;
the [mechanisms](https://github.com/ArtVsMark/Engineering-Pipeline-Mechanisms)
are the family's platform and execute: the pipeline, badges, facts, checks. The
catalogue is moving onto it as a consumer —
[#930](https://github.com/ArtVsMark/Engineering-Incidents-Playbook/issues/930).

## Why

A list of "do this" gets copied wholesale and followed by nobody. A rule holds
only while the understanding of **why** is alive — and that understanding lives
in the incident, not in the wording.

So this is not a requirements list. It is a catalogue of post-mortems: read what
broke, recognise your own situation, take the rule together with its reason.

## How to use it

**Connecting a project** — [`CONNECT.md`](CONNECT.md): one command assembles
the answer for every rule, the channel back and the daily "inbox" run. Optional
mechanisms — actions, checks, badges, skills — are listed there, in one list.

**Starting a new project** — walk through [`START.md`](START.md): what to set up
on day one and what can wait. Boilerplate lives in [`templates/`](templates/).

**Looking for a specific fix** — see [`rules/`](rules/README.md), one file per
rule, entered by number or [by area](rules/README.md#by-area).

**Not sure where to start reading** — [`TOP-10.md`](TOP-10.md): ten rules that
travel beyond the stack they came from.

**Want to contribute** — [`CONTRIBUTING.md`](CONTRIBUTING.md): what is accepted
here, in what shape, and why a rule without an incident is not.

**Handling an incident in a Claude Code session right here** — the window's
skills in [`.claude/skills/`](.claude/skills/README.md): from the first pass
(`/incident-triage`) to the write-up after the fix (`/postmortem`), every step by
the catalogue's rules rather than from memory.

**Do not copy the catalogue wholesale.** Every rule has an "Applicability"
section stating plainly **where it does not work**. Half of what is here is
shaped by agent sessions, GitHub and rate limits; on a different stack it is
ballast.

## Record format

```
Rule            one sentence
Incident        what broke, how it surfaced, what it cost
Why             the failure mechanism, not a moral
Applicability   where it holds — and where it does NOT
Trace           the issue or PR where the failure is visible
```

**The trace is mandatory.** Without a link to evidence, a record turns into
"someone said this was better" within a month.

## How it grows

**A rule born in any project gets recorded here** — not selectively, not after
the fact. The project keeps the working wording and a link; the incident, the
reasoning and the limits of applicability live here. A rule without its own
history cannot be defended a month later, and it never travels to the next
project.

The record is written **the same day**. Material spoils fast: rules a month old
had to be reconstructed from documents, because nobody remembered them any more.

## Language

The catalogue is kept in two languages, `rules/en/` and `rules/ru/`, with
**identical file names** — so cross-references between rules resolve the same way
in both trees.

The index [`rules/README.md`](rules/README.md) is **shared between the two
languages** and generated from the files themselves. A rule added in only one
language fails the build: that is the mechanism keeping the trees from diverging.
Two separate indexes would not do this — each looks complete on its own.

## The project family

The family projects exchange contracts, and the catalogue holds them — see "Two
roles" above. Each project has its own role, and the family badge shows whether a
project agrees with the rest:

| Project | Role in the family |
|---|---|
| **Engineering-Incidents-Playbook** (`EIP`, here) | the rules and their export, the answer contract, the upstream proposals channel, the `facts.json` contract, the family summary |
| [Engineering-Pipeline-Mechanisms](https://github.com/ArtVsMark/Engineering-Pipeline-Mechanisms) (`EPM`) | pipeline steps called by a tagged address: facts, drift, automerge |
| [ArtVsMark](https://github.com/ArtVsMark/ArtVsMark) (`AVM`) | the profile showcase — reads every project's facts; the facts contract has been held by the catalogue since 2.0 |
| [Stepik-Python-Grader](https://github.com/ArtVsMark/Stepik-Python-Grader) | consumer; most of the catalogue's rules were born here |
| [Glossary-Python](https://github.com/ArtVsMark/Glossary-Python) | consumer, paired with the grader |
| [Claude-Code_Usage-Token](https://github.com/ArtVsMark/Claude-Code_Usage-Token) | consumer |

**The family badge** has segments `gives` (what the project offers), `family`
(what it takes from the publishers), `pairs` (paired links) and `ext` (the
outside world, judged from the project's own facts: a floating `…-latest`
runner label is red), with the publishers block `EIP · EPM` on the right.
Each project puts it up itself with the `family-badge` action; how to read the
colours is in the [contract](export/README.md).

## Consumers

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook/badges/.github/badges/consumers-en-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook/badges/.github/badges/consumers-en-light.svg">
  <img src="https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook/badges/.github/badges/consumers-en-dark.svg" alt="How rules are enforced across consumers" width="100%">
</picture>

Drawn by a workflow from the projects' own answers, not our assessment of them:
one row per project, the number of rules each mechanism holds, and "born" —
how many rules originated there. The full report, including "who already
solved what a neighbour holds by nothing", is in [`export/where.md`](https://raw.githubusercontent.com/ArtVsMark/Engineering-Incidents-Playbook/badges/export/where.md).

**You are not in that summary — and the catalogue will not find out on its
own.** The rules are public and taken without asking; but the other direction —
your answer for every rule, and the rules born at your project — has no address
to be read from until you give one. The catalogue neither writes outwards nor
goes looking: only the project itself can speak up, with an
[announcement](https://github.com/ArtVsMark/Engineering-Incidents-Playbook/issues/new?template=consumer-announce.yml).

## License

Records, showcase and document templates — [CC BY 4.0](LICENSE): take it,
change it, use it, keep the attribution. Scripts, workflows and executable
templates — [MIT](LICENSE-CODE): Creative Commons itself advises against its
licences for software, and the templates here are meant to be run.

Consumers' data is quoted with the project named and never relicensed; the
terms are in the [consumption contract](export/README.md).
