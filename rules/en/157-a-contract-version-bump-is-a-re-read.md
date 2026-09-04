# A contract version bump is a re-read of your answers, not just of the format

**Area.** contracts, data

**Tier.** 1 — rules and roles

**The rule.** A contract version bump requires re-reading **your answers**, not
merely checking that they still parse. The meaning of fields moves with the
number, and formal validity survives it: the records keep passing the check
while meaning something else. Separately: a version must never be checked by
comparing it against your own constant — both sides of that comparison belong
to the consumer, and a bump on the publisher's side is never noticed.

**Portable beyond Claude Code.** yes — the subject belongs to any contract
between two sides that update independently.

## The incident

The grader's answer to the catalogue sat at schema `1.0`. Its gate checked
`data['schema'] != '1.0'`, where `data` was its own file and `'1.0'` its own
constant; the rejection text meanwhile claimed "the catalogue's contract is 1.0
today" without ever looking at the catalogue.

The contract had become `1.1`, and that was not cosmetic: the word
`process-step` had split into `pipeline` · `document` · `none`, and the `where`
field had gained the requirement of a resolvable address. The records stayed
formally valid and the gate stayed green.

The cost: **52 answers out of 153** were phrased in a word the publisher no
longer maps to any level — in the consumers table the grader had zeros in three
columns out of five. Re-marking against the facts produced 24 pipelines, 26
documents and 2 "nothing"; and it also surfaced that **36 records out of 98**
called a gate something that is not one: two of the named scripts are run by no
workflow at all, their names appearing only in comments.

It was noticed not by a check but by the owner asking "why is everything a
process step here".

## Why

Compatibility of format and compatibility of meaning are different things, and
the first masks the second. The evolution rule "readers ignore unknown fields"
makes MINOR safe for **parsing**; for **meaning** it does nothing. A split word
still reads — it now just says "we did not answer".

Comparing a version against your own constant never breaks, and that is exactly
why it does not work: both of its sides are updated by the same hand. The
publisher is not in that comparison, and the publisher is who changes the
contract.

The asymmetry is in who **sees** the drift. The consumer sees a valid file. The
publisher sees a column of zeros and reads it as "that is how they work".
Neither side sees the cause until somebody asks out loud.

## In practice

- the contract version is taken **from the publisher**, never from your own
  constant;
- a MINOR bump re-reads the answers, not only their shape: a widened value list
  is a reason to walk every record where the old value stood;
- the publisher, for their part, compares the consumer's answer version against
  their own and says so — otherwise they read a lag as a choice.

## Where it applies

**Works** for any contract between sides that update independently: a
catalogue's export, a consumer's answer, an event schema, a config format.

**Does not work** inside one repository where both sides are edited by the same
change: there the drift is caught by the build, and a version adds nothing.

**Sign of violation:** the version check compares a field of your own file
against a constant in that same file, while its rejection text asserts
something about the other side.

## Trace

ArtVsMark/Stepik-Python-Grader#1400

Related: [113](113-a-contract-states-how-it-may-change.md) — a contract must
state how it changes; here you can see why that is not enough: the evolution
rules were written and followed, and the answers drifted in meaning anyway;
[114](114-migrate-from-the-current-version-not-from-zero.md) — migration starts
from the current version, and to know it you have to ask somebody;
[049](049-derive-state-from-live-artifacts.md) — state is derived from a live
artefact, and your own constant is not a live artefact of the other side.
