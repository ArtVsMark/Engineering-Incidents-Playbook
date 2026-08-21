# Matching keys are not a translation

**Area.** localisation

**The rule.** Checking that the key set is complete verifies that a string was
not forgotten and says nothing about whether it was **translated**. Separate
checks are needed for properties of the text.

## The incident

The string sets in two locales matched by keys completely — the formal check was
green. Meanwhile a banner string spent **years** naming one of the sections in
Russian inside the English file, where four neighbouring keys called it in
English.

It then turned out that even a check for the alphabet used is insufficient. In
the English file, quotation marks of two traditions sat side by side, with one
and the same term quoted both ways — and quotation marks are not letters, so an
alphabet check does not see them.

The upshot: six guards, each checking its own property — completeness relative to
usage, parity of key sets between locales, absence of the foreign alphabet, a
single quotation style, the direction of links, the correctness of names.

## Why

A completeness check answers "does the string exist", while translation quality
is the question "is it the right string". Between them lies everything
translation is done for.

The reason such defects live for years is the **gradient of visibility**. A
missing key is visible at once: the identifier is shown instead of the text. An
untranslated string looks **normal** — it is legitimate text, merely in the wrong
language, and the eye of a reader of the other locale has nothing to catch on.

Hence the way to build such checks: not "check the translation" (impossible) but
decompose it into **observable properties**, each checked literally. The
properties come not from imagination but from errors that already happened.

## In practice

- one check per property, each named separately: then a failure says what exactly
  is wrong;
- the fallback for a missing translation makes the defect **visible** rather than
  hiding it: showing the identifier is more honest than silently substituting
  another language;
- the list of properties grows from incidents, not from imagination;
- an identical key set is a necessary condition and is checked too: without it
  part of the interface switches language and part does not.

## Where it applies

**Works** for localisation, email templates, message sets — anywhere several
versions of the same text are maintained in parallel.

**Does not work** for literary translation: there the properties cannot be
formalised, and a human is needed.

**Sign of trouble:** the completeness check is green and a reader of the other
locale sees a foreign language.

## Trace

ArtVsMark/Stepik-Python-Grader — `scripts/check_locale_guardrails.py`, #821,
#264. Related: [065](065-the-onramp-must-speak-the-newcomers-language.md).
