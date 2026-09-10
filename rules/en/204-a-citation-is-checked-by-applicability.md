# A citation of a rule is checked against its applicability, not against a fitting phrase

**Area.** catalogue, documentation

**Tier.** 1 — rules and roles

**The rule.** Citing a rule is a claim that the rule **applies** to the case at
hand, and that claim is checked against the cited rule's "Where it applies"
section — never against a well-fitting phrase from its letter. A rule whose
"Does not work" clause covers your case does not become grounds. A near miss is
named an **analogy** in so many words rather than presented as grounds; and when
no rule fits at all, that is what gets written: the requirement rests on nothing.

**Portable beyond Claude Code.** yes — the subject exists in any body of rules
whose records cite one another as grounds and whose records state their limits.

## The incident

On 10 September, within a single hour, **three citations in a row in one
paragraph** of one changelog entry. Every one of them was caught by an outside
reader; none by the author.

**The first was 128** — "half-filled looks filled, and that is worse than
empty". The phrase fit word for word. 128's own applicability narrows it: the
subject of the required field must be a **set**, and what is checked there is the
completeness of an enumeration. A word-plus-reason pair has no set at all.

**The second was 154**, replacing the first. Its applicability says outright: "it
does not work for statuses where a reason is already required… it extends the
same requirement to `active` + `none`, and **does not found a second case**". The
case under discussion — an answer of "held by a document" — was that second case.

**The third was 182**, replacing the second. The rule did fit, but the paragraph
described the **neighbouring** one of the gate's two conditions: 182 holds "the
word is missing", 154 holds "the word is there, the reason is not". The code, in
its two rejection messages, kept them apart correctly; the prose merged them.

**What was tried first, and why it failed.** After the first miss I wrote myself
an order of operations: "applicability first, citation second". I missed twice
more. A written intention is read by the same person who wrote it, and precisely
at the moment when the phrase already looks like a fit; the third miss happened
inside a change **announced as the fix for the second**.

## Why

**A letter is quotable; limits are not.** A rule is written so its letter can be
quoted in one line: it is general, and it sounds convincing in any neighbouring
context. The "Does not work" section is unquotable by construction — it
enumerates particulars, and it is opened rather than quoted. Anyone looking for
support finds the letter and stops there: it already fits.

**The cost is asymmetric, and that sets the form.** A citation that misses does
not look like an error — it looks like **reinforcement**. The next reader follows
the number, fails to find their case there, and concludes the record is about
something else rather than that the citation is wrong. Worse: an ungrounded
requirement acquires the appearance of a grounded one — "NNN says so" — and
arguing with it now means arguing with the catalogue.

**The absence of a fitting rule is an answer too.** A requirement for which no
rule was found rests on nothing; that is a legitimate state and it has its own
words ([057](057-unmechanizable-rules-are-named-explicitly.md)). Substituting the
nearest phrase hides the emptiness in exactly the place the catalogue insists it
be named.

## In practice

- the subject is a citation used as **grounds**: "NNN says so", "(NNN)" after a
  claim. A mention — "related", "see also", a back-reference — asserts nothing
  and is outside the rule;
- what gets opened is the **cited** rule's applicability, not one's own
  recollection of it: all three misses were made from memory of the letter, and
  all three were undone by reading the section;
- a rule that almost fits is called an analogy in so many words — "the same
  device as in NNN" — and that is a different claim, not a softer one;
- **there is no machine half for the fit itself**: whether a rule applies is a
  matter of reading. What is checkable is only that the number exists, and that
  is a different, weaker claim
  ([182](182-an-unmechanisable-answer-is-split-in-two.md): the half is named
  rather than passed off as an absent subject).

## Where it applies

**Works** in a body of rules whose records state their limits and cite one
another as grounds: a rules catalogue, a decision register, a standards manual.

**Does not work** where rules declare no limits: there is nothing to check
against, and the requirement degenerates into "read carefully" — that is, into a
preference.

**Does not work** for mentions and back-references: they assert no applicability,
and demanding a check of them means going red on correct work
([051](051-warn-on-likely-block-on-certain.md)).

**Sign of violation:** the cited rule, opened at its applicability section, names
your case among the things it does NOT cover. A second sign: the citation in one
paragraph has changed twice in a row.

## Trace

ArtVsMark/Engineering-Incidents-Playbook#473

Related: [183](183-a-claim-about-the-mechanism-is-checked-against-it.md) — a
claim about a mechanism is checked against the mechanism; this is the same thing
for a claim about a rule, and the subject of the check is the same: the record,
not the memory of it. [184](184-an-answer-of-not-applicable-is-split-in-two.md)
names the mistake "read the letter and missed the generalisation"; here it is
mirrored — the letter fit, and the limits went unasked.
[120](120-how-to-run-a-rule-catalogue.md) — how the catalogue is run, where
citations between records are already load-bearing.
