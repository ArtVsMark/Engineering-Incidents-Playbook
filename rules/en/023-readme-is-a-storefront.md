# The README is a storefront, not a dumping ground for technical memory

**The rule.** The README holds only what a person needs in the first five
minutes. Everything else is behind a link.

## The incident

The README grew the natural way: every new capability added a paragraph, every
settled question added an "and what if…" section.

By the time anyone noticed, the page answered dozens of questions at once — and
therefore none of them quickly. Someone arriving to install the tool was
scrolling past descriptions of internal contracts.

## What stays

- what the project is, plus the badges;
- quick start and installation;
- the main modes of operation;
- **links** to the detailed documentation.

Everything else moves into documentation arranged by reader.

## Why

A README has two incompatible jobs: **attracting** someone who has not decided
yet, and **serving** someone already working. The first needs brevity, the
second needs completeness.

They cannot be combined, and the choice must favour the first: serving is easier
from a dedicated document, while attracting has nothing else to work with — the
project has no second front page.

Separately: **numbers do not belong in prose**. Test counts, coverage, data
volume live in badges that are recomputed, not in text that goes stale silently.

## Where it applies

**Works** for any public project.

**Does not work** for tiny ones: if the whole documentation is three paragraphs,
they are the README.

**Regression is inevitable:** the README grows again. Checking it while
reviewing every documentation change is cheaper than clearing it out twice a
year.

## Trace

ArtVsMark/Stepik-Python-Grader — `CONTRIBUTING.md` § the README as a storefront
