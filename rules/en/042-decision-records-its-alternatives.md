# A decision is recorded together with the options rejected

**Area.** decisions

**The rule.** A decision record consists of context, the decision itself, **the
alternatives considered**, and the consequences. Without alternatives it is not
a decision but an announcement.

## The incident

Major forks — the direction towards a server mode, changing the execution
mechanism, the boundary between layers — first lived in issues and discussions.
From there they vanished: the issue closed, the discussion scrolled away, and a
month later nobody could say why it was done this way rather than another.

Then the same thing kept repeating: somebody proposed an option already
rejected, and the analysis started over — without the original arguments,
because they had not been saved.

A telling case: a shared interface over two similar content providers was
discussed, and the decision was **not to introduce it** until a third appeared.
The decision was written down with its reason — and future proposals of "let us
have a shared provider after all" could be declined with a link rather than a
fresh argument.

## Why

The rejected option is the most valuable part of the record. The accepted
decision is visible in the code; **what is invisible is exactly what was
considered and not chosen**, and that is precisely what comes back to the
discussion.

Second: an alternative records the **price**. "We chose A" says nothing; "we
chose A because B requires rewriting process launching by hand and C blocks new
contributors" says both what was decided and under what changed conditions it
should be revisited.

Third: the record answers "why", not "how". The specification lives separately
and changes; a decision record is dated and does not change at all.

## In practice

- fixed sections: context · decision · alternatives · consequences (plus
  migration, if the decision is phased);
- one record, one decision; a numbered file with a short slug;
- **a retrospective record is normal**: if a decision was long since made in
  code but never written down, write it after the fact and mark it honestly as
  retrospective;
- every alternative names the drawback that ruled it out;
- a refusal ("we do not introduce X until a third case appears") is also a
  decision and is also recorded: an unrecorded refusal comes back.

## Where it applies

**Works** for forks with a switching cost: architecture, data format,
dependency, platform.

**Does not work** for decisions reversible in one commit — there the record
costs more than the decision.

**Sign that a record is needed:** the question "why did we not do it the other
way?" is asked a second time.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/dev/adr/README.md`, ADR-0010 (the refusal
to generalise prematurely is recorded in writing).