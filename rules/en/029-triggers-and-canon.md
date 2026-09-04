# A compact trigger in the main file, the details in the canon

**Area.** documentation

**Tier.** 1 — rules and roles

**The rule.** The main file answers "do I need to go there". The specialised one
answers "how exactly". Mixing them makes the first bloat and the second go
unread.

## The incident

The main rules file kept growing: every new rule added a paragraph, every
incident added detail. It reached hundreds of lines and people stopped reading
it end to end — precisely when the most important things had arrived in it.

At the same time the specialised documents lay idle: everything needed was
"already in the main file anyway".

## The fix

A two-level layout.

**The trigger** in the main file — a short block with an explicit note:

> The full contract, tables and commands live in that document. This block is a
> compact trigger only; do not duplicate the details here.

**The canon** — the specialised document holding the detail, the history of
incidents, the tables and the commands.

The dividing test: the trigger gets what you need to know **to avoid making a
mistake right now**. Everything you need **once you are actually working on the
subject** goes to the canon.

## Why

The main file has a peculiar property: it is read **in full, at every start**.
Its size is therefore a tax on all work, paid always and used rarely.

A specialised document is read on purpose. Size does not hurt it: you came there
for this.

The note "do not duplicate the details here" is not politeness but protection
against regression: without it the next author adds the detail back, with the
best intentions.

## Where it applies

**Works** for any document hierarchy with an entry file: project rules,
onboarding, README.

**Does not work** if there are no specialised documents and no reason to create
any.

**Regression is inevitable** and is treated in review: growth of the entry file
is a reason to ask again whether this is a trigger or the canon.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md`, the "this block is a trigger only"
call-outs