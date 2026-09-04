# The newcomer's entry point speaks their language — and there is more than one

**Area.** community

**Tier.** 5 — everything else

**The rule.** Tasks marked as an entry point for new contributors are written in
the language of the audience the label exists for. And there must be more than
one such label: a newcomer's path does not end at the first contribution.

## The incident

The project's front page is bilingual — it deliberately brings in an
English-speaking reader. The "good first issue" and "help wanted" labels are
exactly where that reader lands. And the task bodies were Russian only.

So the funnel broke off at precisely the point it was built for: the reader was
led to a task and cut off there — the very audience the label exists to serve.

The second observation mattered just as much. There are **two** labels, and both
must be translated: whoever finishes the first task goes looking for a second
and runs into the next label. One bilingual label does not remove the barrier,
it **moves it one step** — and the second barrier stings more, because the person
has already invested.

The rule applies to taking things off the shelf too: if you attach such a label
to an existing Russian-only task, write the translation first.

## Why

An on-ramp is a chain, and its throughput equals its narrowest link. A bilingual
front page with monolingual tasks is not "half the way" but zero: nobody reaches
the end.

Second: a barrier met **after** effort has been invested repels more strongly
than one at the entrance. Somebody who finished the first task has already spent
an evening; hitting a wall after that stings more than never starting.

Third: the rule must cover **changes of state**, not only creation. Labels are
more often attached to existing things, and a rule written only for new tasks
circumvents itself.

## In practice

- fixed format: the main text, a separator, the translation — in one body, not
  as two tasks;
- the rule applies at the moment the label is **attached**, not when the task is
  created;
- do not attach the label to something beyond a newcomer: bait leading to a dead
  end is worse than no bait;
- the check is soft — this is tracker state, not a code defect: a warning, not a
  rejection.

## Where it applies

**Works** for projects with an audience that does not speak the development
language.

**Does not work** with a single-language audience — there translation is wasted
work.

**Sign of trouble:** the front page is in two languages and everything it leads
to is in one.

## Trace

ArtVsMark/Stepik-Python-Grader — `CLAUDE.md` § labels when raising an issue,
`CONTRIBUTING.md` § "good first issue" and "help wanted" are raised bilingually.
Related: [051](051-warn-on-likely-block-on-certain.md).