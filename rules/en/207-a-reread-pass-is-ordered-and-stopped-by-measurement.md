# A re-read pass is ordered and stopped by measurement, not by intuition

**Area.** catalogue

**Tier.** 1 — rules and roles

**The rule.** A pass of re-reading answers goes in an order set by
**measurement**, and it ends on a **measured yield** — the share of edits on the
band just read has dropped, and a sample from the following bands has not refuted
that — rather than when the list runs out. Which metric to order by is the
project's own decision, calibrated on its own corpus: what transfers is the
requirement to measure, not someone else's formula. Answers left unread are
declared **unread**, not correct ([039](039-three-outcomes-not-two.md)).

**Portable beyond Claude Code.** yes — the subject exists for any corpus of
answers that is re-read wholesale and rarely: a conformance map to an external
standard, a debt inventory, a documentation audit.

## The incident

**The neighbour's measurement, from which the proposal came** (the mechanisms
project, 2026-09-17): of 203 answers to the catalogue, **93 had not been touched
since 9 September** — written before the export began carrying the text of the
requirement, so nearly half the corpus was answering the rule's TITLE. Reading 93
in a row meant several shifts, and reading quality drops towards the end exactly
where it is needed most.

The answers were sorted by the stem overlap between the rule's requirement and
their own answer. Yield by band: **0–10% overlap — 29 read, 19 edits (66%);
10–20% — 6 read, 1 edit (17%), and that one cosmetic; 20% and above — a sample of
5, zero edits.** Of the nineteen, seven "not applicable" answers rested on ONE
false premise that a command could have checked on the day they were written.
Until that day the queue was picked by intuition, and the result is measured:
seven false "not applicable" answers lived for months and surfaced once the order
became mechanical.

**OUR MEASUREMENT WITH THE SAME METRIC BEHAVES DIFFERENTLY** (2026-09-17, 205 of
the catalogue's answers about itself). The same formula — stem overlap between the
rule's requirement and our `where`+`why`:

| band | answers | of them "not applicable" |
|---|---|---|
| 0–10% | 127 | 9 (7%) |
| 10–20% | 63 | 15 (23%) |
| 20% and above | 15 | 5 (33%) |

Here the suspect answers concentrate in the HIGH bands, not the low ones.

**A THIRD MEASUREMENT, AND IT IS ABOUT THIS MECHANISM ITSELF.** A re-read pass is
not only reading YOUR OWN answers: an outside look reading changes does exactly
the same over a different corpus. During the shift of 2026-09-17, **19 changes**
were merged into the shared branch, and the outside look kept producing findings
to the very end: four, three, one on the last three, with one pass still running.
The yield did NOT drop — so by this rule's own criterion stopping was not allowed,
and it did not stop.

**AND THE PASS'S YIELD CANNOT BE RECONSTRUCTED FROM OUR TREE AT ALL.** Measured:
`git log --since=<start of shift> --format=%b` over the shared branch returns
**zero** "Разобрано" lines — clearing a finding lives in the change's body on the
platform, and squashing leaves only the subject and trailers in the tree. So the
very number this rule says to stop by is stored nowhere in our tree. That is the
live price of the requirement "the measurement is stored beside the corpus, not in
a window's memory": here it is stored nowhere.

**THE CAVEAT WITHOUT WHICH THE BAND NUMBERS LIE, AND IT IS PART OF THE
INCIDENT:** we measured different things. The neighbour measured EDIT YIELD — how many answers
had to be fixed; we measured WHERE the "not applicable" answers sit, and "not
applicable" is not a synonym for "wrong". Testing their metric honestly on our
corpus takes a reading pass with recorded yield, and that has not been done. The
conclusion this forces is the content of the rule: **what transfers is the
requirement to measure, not someone else's formula.**

## Why

**Intuition produces a long pass with falling quality.** A corpus of two hundred
answers takes several shifts, and the last fifty are read worse than the first —
while defects are not distributed in number order.

**"Read everything" is not a goal, it is a way of not thinking about yield.** The
goal is to remove defects; once a band stops producing them, continuing spends a
shift confirming what is already confirmed. Stopping on a measurement is cheaper
than stopping on fatigue and, unlike it, can be checked.

**Silent unread is worse than named unread.** A pass that ended halfway with no
number leaves the corpus in a state of "we sort of looked": the next person does
not know where the read boundary is and either starts over or does not start.

**Someone else's metric is a hypothesis about your corpus, not knowledge of it.**
Our measurement showed exactly that: the same formula on a different tree gave a
different shape. Taking it as given would have ordered the pass by a signal that
predicts nothing here.

## Practical limits

- the ordering metric is your own and **calibrated on your own corpus**: an
  external one is taken as a hypothesis and checked before anything leans on it;
- the stop is verified by a **sample from the following bands**, not by a feeling:
  without the sample, "the yield dropped" is indistinguishable from "we got
  tired";
- what is unread is **counted and printed as a number** — how many answers remain
  and in which bands; silence here is the defect;
- a pass with no recorded yield is **not called finished**: it is called
  interrupted, which is a legitimate state, but a named one;
- the yield measurement is stored beside the corpus, not in a window's memory:
  the next pass starts from it rather than from zero.

## Where it applies

**Works** where the corpus of answers is large, re-reading is expensive, and
defects are not distributed in record order: a conformance map, a registry of
answers to an external rulebook, a debt inventory.

**Does not work** for small corpora — up to two or three dozen records — where a
full sweep is cheaper than measuring and sampling. There the ordering becomes a
ritual: counting bands takes longer than reading everything. **Nor does it work**
where the re-read is triggered by a pinpoint event ("one mechanism changed"): the
subject is set by the event, and the queue follows from it directly.

**Sign of violation:** a re-read pass is declared finished with no number beside
it — neither how much was read, nor how much remains, nor what the yield was.

## Trace

ArtVsMark/Engineering-Pipeline-Mechanisms — `docs/decisions/030-the-answer-audit-stops-on-a-measured-yield.md`

Related: [177](177-unfinished-rule-work-comes-first.md) — unfinished rule work
comes first; that is about the PRIORITY of the queue, this about the order within
it;
[157](157-a-contract-version-bump-is-a-re-read.md) — a contract bump requires
re-reading answers; that is the pass's TRIGGER, this is its course and its end;
[039](039-three-outcomes-not-two.md) — the third outcome: the unread is not passed off as
clean;
[146](146-a-green-gate-does-not-verify-its-premise.md) — someone else's metric is
a claim about the world and is checked by measurement, not taken on faith.
