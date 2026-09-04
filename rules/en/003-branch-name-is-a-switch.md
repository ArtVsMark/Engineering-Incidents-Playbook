# A branch name can be a behaviour switch, not a style convention

**Area.** pipeline

**Tier.** 2 — the pipeline and CI

**The rule.** If the pipeline reacts to a branch prefix, that belongs in the
first line of the project's rules — together with what happens under any other
name.

**Portable beyond Claude Code.** partly — the device of a name that switches behaviour carries over, but the incident and the remedy are tied to a pipeline that reads the branch prefix. Where nothing reads it, the rule guards nothing.

## The incident

Of eight open pull requests, auto-merge was enabled on three. Five green pull
requests sat for hours, two of them for **fifteen hours**, with every check
passed and no conflicts.

The cause was the branch name. The workflow that opens the pull request and
enables auto-merge only picked up branches prefixed `agent/`. Branches named
`claude/**` or `fix/**` travelled the same path and stopped at the last step,
waiting for a human.

From the outside it looked like a broken pipeline. The pipeline was working.

## Why

The chain of causes is long, and every link is invisible on its own:

1. auto-merge is enabled by a GraphQL mutation;
2. there is no REST equivalent for it;
3. the agent session's proxy blocks GraphQL entirely;
4. therefore the session **physically cannot** enable auto-merge on its own
   pull request;
5. only the workflow can — and the workflow looks at the prefix.

No single link is at fault; the result is a silent stall.

## Where it applies

**Works** wherever automation filters by branch name — which is nearly every
pipeline that opens pull requests for you.

**Does not work** as a universal convention: the specific prefix is a detail of
your setup, and carrying `agent/**` into a project without such a workflow is
pointless.

**The general conclusion does carry over:** any place where the name of an
object changes the behaviour of the system must be stated explicitly. A silent
dependency on a name produces failures you cannot search for.

## Trace

ArtVsMark/Stepik-Python-Grader#1320, ArtVsMark/Stepik-Python-Grader#1302