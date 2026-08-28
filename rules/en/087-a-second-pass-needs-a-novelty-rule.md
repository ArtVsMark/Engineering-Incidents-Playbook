# A second pass receives the previous findings and a ban on reopening them

**Area.** audit

**The rule.** A second audit of the same subject starts from the first one's
findings file and from a novelty rule: what is already found does not count as a
finding — it can only be deepened or discarded.

## The incident

Without that rule the second pass **reopens 60% of the first** and wastes an
entire limit window.

The mechanism is clear and unavoidable: the executor of the second pass does not
remember the first. It walks the same code with the same eyes and finds the same
things — and finds them honestly, with reproduction and location. Telling that
result from new work by the report alone is impossible: it looks like a full
audit.

The novelty rule changes the input, not the diligence: the previous pass's
collection is fed in, and exactly three outcomes are permitted for anything
already known — **a new consequence**, **a new reproduction path**, **actual
command output instead of an assumption**. Everything else is discarded.

## Why

A second pass is valuable only for its increment. The increment cannot be measured
if the executor cannot see the boundary of the already known — and it cannot see
that by construction: it has no memory of the previous pass.

Second: without a novelty rule the money is spent **in inverse proportion to
value**. The most visible defects are found first and reopened most eagerly,
while the expensive rare ones stay unfound because the budget never reaches them.

Third, less obviously: the novelty rule turns the second pass into **a check on
the first**. "Deepen" means bringing a previous finding to reproduction;
"discard" means declaring it wrong. Both operations are more useful than a fresh
list of the same things.

## In practice

- the previous pass's collection is fed **as input**, not handed over at the end
  for comparison;
- the three permitted outcomes for the known are named literally, or "deepened"
  becomes a synonym for "reworded";
- the share of genuinely new findings is measured and printed: without a number
  the rule is unverified;
- the same applies to comparison with an external report: somebody else's
  findings are also already known.

## Where it applies

**Works** for repeat audits, regular reviews, comparison with external reports.

**Does not work** if the subject changed so much that previous findings no longer
apply — but even that is established by comparison, not by assumption.

**Sign of a breach:** the second report is about as long as the first.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/multiagent.md` § additionally for
audits (the novelty rule). Related: [020](020-restart-only-the-delta.md),
[026](026-rejected-findings-must-be-recorded.md).