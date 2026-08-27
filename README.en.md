# Engineering Incidents Playbook

[![Release](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FArtVsMark%2Fclaude-code-playbook%2Fbadges%2F.github%2Fbadges%2Frelease.json&cacheSeconds=300)](https://github.com/ArtVsMark/claude-code-playbook/releases)
[![Version](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FArtVsMark%2Fclaude-code-playbook%2Fbadges%2F.github%2Fbadges%2Fversion.json&cacheSeconds=300)](VERSIONING.md)
[![Rules in the catalogue](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FArtVsMark%2Fclaude-code-playbook%2Fmain%2F.github%2Fbadges%2Frules-en.json)](rules/README.md)

**A catalogue of <!--m:rules-->146<!--/m:rules--> rules for Claude Code and GitHub,
where every one grew out of a real failure.** Agent sessions and the project rulebook (`CLAUDE.md`), the
GitHub delivery pipeline, parallel executors, audits. Every record comes with its
history: what broke, how it surfaced, what it cost.

> 🇷🇺 [Русская версия](README.md) · Unofficial, not affiliated with Anthropic.

**Start here:** [ten rules to start with](TOP-10.md) ·
[day-one order](START.md) ·
[the whole catalogue, by area](rules/README.md)

## Why

A list of "do this" gets copied wholesale and followed by nobody. A rule holds
only while the understanding of **why** is alive — and that understanding lives
in the incident, not in the wording.

So this is not a requirements list. It is a catalogue of post-mortems: read what
broke, recognise your own situation, take the rule together with its reason.

## How to use it

**Starting a new project** — walk through [`START.md`](START.md): what to set up
on day one and what can wait. Boilerplate lives in [`templates/`](templates/).

**Looking for a specific fix** — see [`rules/`](rules/README.md), one file per
rule, entered by number or [by area](rules/README.md#by-area).

**Not sure where to start reading** — [`TOP-10.md`](TOP-10.md): ten rules that
travel beyond the stack they came from.

**Want to contribute** — [`CONTRIBUTING.md`](CONTRIBUTING.md): what is accepted
here, in what shape, and why a rule without an incident is not.

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

## License

[CC BY 4.0](LICENSE) — take it, change it, use it, keep the attribution.
