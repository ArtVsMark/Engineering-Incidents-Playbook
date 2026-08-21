# Write code containing escapes to a file, not through a heredoc

**The rule.** Escape sequences pass through the shell and change on the way. A
file is the only reliable carrier.

## The incident

A `\n` inside Python code written through a bash heredoc turned into a real
newline **twice**. The result:

```
SyntaxError: unterminated string literal
```

Diagnosis took time precisely because the source text looked correct: the error
happened on the path from text to file, not in the code itself.

## Why

A heredoc is not "insert this text as it stands". Between your characters and
the file sits a shell, and it interprets whatever it considers its own:
escaping, variable substitution, line continuation.

Part of that behaviour depends on whether the delimiter is quoted (`<<EOF`
versus `<<'EOF'`), and part on the shell itself. So the same text produces
different files in different environments.

## Where it applies

**Works** for any generated code containing `\n`, `\t`, `\\`, `$` or backticks —
that is, nearly everything except plain prose.

**Does not work** as a ban on heredocs in general: for text without escapes they
are convenient, and a quoted delimiter removes most of the risk.

**Generalisation:** passing text through an intermediate interpreter always
risks silent substitution. The fewer layers between source and file, the fewer
surprises.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/preflight.md` § what the gates miss
