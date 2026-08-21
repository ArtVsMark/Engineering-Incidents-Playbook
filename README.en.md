# engineering-incidents

**Rules that grew out of failures.** Each one comes with its history: what
broke, how it surfaced, what it cost.

> 🇷🇺 [Русская версия](README.md) · Field notes from running Claude Code agent
> sessions and a GitHub delivery pipeline. Unofficial, not affiliated with
> Anthropic.

## Why

A list of "do this" gets copied wholesale and followed by nobody. A rule holds
only while the understanding of **why** is alive — and that understanding lives
in the incident, not in the wording.

So this is not a requirements list. It is a catalogue of post-mortems: read what
broke, recognise your own situation, take the rule together with its reason.

## How to use it

**Starting a new project** — walk through [`START.md`](START.md): what to set up
on day one and what can wait. Boilerplate lives in [`templates/`](templates/).

**Looking for a specific fix** — see [`rules/`](rules/), one file per rule.

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

## Language

Records are in Russian; the front page is bilingual. Translation of individual
rules is in progress — open an issue if you need a specific one.

## License

[CC BY 4.0](LICENSE) — take it, change it, use it, keep the attribution.
