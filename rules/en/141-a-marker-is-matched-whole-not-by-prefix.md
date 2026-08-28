# A marker is matched whole, not by prefix

**Area.** gates, code

**The rule.** A structural marker — a heading, a label name, a key, a branch
prefix — is matched against the **whole line**, not against its beginning.
Prefix matching silently accepts a neighbouring marker that happens to start
with the one being checked, and it errs towards "passed". If matching by prefix
is deliberate, say so next to the code: the next reader will otherwise fix it
as a defect.

## The incident

The catalogue's index build checks that a record carries its mandatory
sections:

```python
missing = [h for h in SHAPE[lang]
           if not re.search("^" + re.escape(h), text, re.M)]
```

The mandatory section is `## След` ("Trace"). Rule 002 carries a neighbouring
heading, `## Следствие второго порядка` ("A second-order effect"). It begins
with `## След`.

Two failures follow at once, both silent.

**First: a record without the mandatory section passes the check.** Any heading
starting with "След" is enough. The gate is green, the section is absent.

**Second: the trace is parsed from the wrong offset.** The same function takes
`text[text.index(head) + len(head):]` — that is, from "Следствие", sweeping up
everything between it and the real trace. A run against a fixture showed it
literally: instead of `['1']` the parse returned `['999', '1']` — someone
else's issue, mentioned in prose above, arrived as this record's trace.

**Reading could not catch this.** Both lines read correctly: `^` and `index` do
exactly what they say. The defect is not in them but in the fact that the set of
markers turned out not to be prefix-free — and that is a property of the
**corpus**, not of the code, so the code does not show it.

It surfaced indirectly: a second checker written with the same idiom produced a
false finding on 002, reporting that its trace did not resolve when in fact it
did.

## Why

**The error is one-sided, and its side is the worse one.** Prefix matching never
produces a false rejection — only a false "passed". A false rejection arrives and
complains; a false pass looks like healthy operation, and the longer it stands
the more it is trusted ([097](097-a-checker-has-two-error-types.md)).

**One change plants the defect, another detonates it.** When the check is
written there is no collision: the "Следствие" heading does not exist yet. It
appears months later, in someone else's record — and silently switches the check
off for that record alone. The two changes cannot be linked by symptom, because
there is no symptom.

**Asymmetry of cost.** Adding the end anchor costs one character. Omitting it
costs a check that switches itself off and tells no one.

## In practice

- match the whole line: `^marker$`, allowing trailing spaces — not `startswith`
  and not a bare `^marker`;
- test it on the subject: the marker and its extension belong in the gate's case
  set, or "matched whole" stays a promise
  ([140](140-a-gate-is-tested-by-what-it-must-reject.md));
- if prefix matching is deliberate, record that next to the code and name the
  set on which it is legitimate;
- revisit when the marker set stops being prefix-free: add `область` next to
  `областьX` and the check comes back on the agenda.

## Where it applies

**Works** wherever the marker is structural and the comparison textual: section
headings, label and key names, branches, configuration fields, parsing another
tool's output.

**Does not work** where the prefix is itself the contract: label zones `area/*`,
namespaces, `refs/heads/`. There, matching by beginning is the point, and an end
anchor would break it.

**Sign of the violation:** the check uses `startswith` or `^marker` with no end
anchor, and the marker set contains a pair where one starts with the other.

## Trace

ArtVsMark/claude-code-playbook#69 — both failures and the run that returned
`['999', '1']` instead of `['1']`.

Related: [097](097-a-checker-has-two-error-types.md) — the checker's two errors
and why this one is invisible;
[140](140-a-gate-is-tested-by-what-it-must-reject.md) — a claim about a check is
confirmed by the subject it rejects;
[103](103-a-side-effect-guard-blames-the-wrong-suspect.md) — exclusions are
defined by the shape of a name, and shapes too run wider than intended.