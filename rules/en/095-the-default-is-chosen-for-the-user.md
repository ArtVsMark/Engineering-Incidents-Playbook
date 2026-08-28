# The default is chosen in the user's favour, not the product's

**Area.** privacy, product

**The rule.** When data collection benefits the product and the user does not
need it, the default is **off**. You compensate not by turning it on but by
making it easy to enable, plus an unobtrusive reminder.

## The incident

Recording a history of runs makes the product smarter: the more accumulates, the
better the recommendations. The direct route is to enable it by default so that
it fills up on its own.

The opposite was chosen: **off by default**, plus a convenient toggle in the menu
and a gentle nudge. The product fills up more slowly as a result — and that is an
accepted price, not an oversight.

A third option was rejected separately, the one that looks most honest: **ask on
first launch**. The arguments were recorded: extra friction at the start, it
breaks non-interactive scenarios and automation, it complicates the tests. In
other words "just ask" is not a neutral decision but a shifting of cost onto
everybody, including those launching the product from a script.

Tellingly, the web shell has a different default — there the session is
interactive by nature. The default is chosen **per scenario**, not once for the
whole product.

## Why

A default is a decision made **on behalf of** the user, and that is its whole
power: the overwhelming majority use it. So the question is not "what suits us"
but "what would this person choose if they knew" — and where their data is
concerned, the answer is known in advance.

Second: the cost of error is asymmetric. Data not collected is a missed benefit,
recoverable. Data collected without knowledge is lost trust, unrecoverable — and
people usually learn about it from somebody other than us.

Third, on "just ask": an interactive question looks like a compromise, but it has
an invisible victim — **non-interactive scenarios**. A launch from a script, from
a pipeline, from a test cannot answer the question and either hangs or receives
an arbitrary default.

## In practice

- off by default, enabled **in one gesture** rather than by hunting through a
  config;
- the nudge is gentle and finite: a one-off hint, not a recurring banner;
- the default may differ per scenario, and the difference is explained rather
  than implied;
- asking on first launch is a separate decision with its own price: it breaks
  automation and requires a "no answer" path.

## Where it applies

**Works** for data collection, telemetry, sending things outward, auto-updates.

**Does not work** for anything without which the product does not deliver what it
promises — there an off default turns the feature into a hidden one.

**Sign of error:** the default is justified by benefit to the product rather than
to the person using it.

## Trace

ArtVsMark/Stepik-Python-Grader — ADR-0002 (history opt-in in the CLI, default-on
in the web). Related: [045](045-no-silent-fallback.md).