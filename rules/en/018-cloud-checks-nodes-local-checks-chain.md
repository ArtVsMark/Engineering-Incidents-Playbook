# One environment checks the nodes, the other checks the chain

**Area.** environments

**The rule.** Every check has an environment where it is meaningful. A check in
the wrong environment yields a false green.

## The incident

The project grew in two environments: a cloud session with a fresh clone and
synthetic data, and a local machine with real credentials, real user data and a
graphical shell.

Some checks kept "passing" in the cloud and failing for the user. The end-to-end
scenario — download, solve, check, history recorded, summary correct — cannot be
reproduced in the cloud **in principle**: there is no live network to the
service, no accumulated history, no display.

Planning such a check into the cloud means arranging a false green in advance.

## Why

Environments differ **not in power but in access to the real thing**. The cloud
checks nodes beautifully: parsing, layout, logic over fabricated data. It cannot
check the whole chain — not because of restrictions, but because half its links
are missing.

The reverse is true too: a local machine gives you neither an OS matrix nor a
clean environment.

Hence a practical consequence: **each slice of work gets its environment
assigned up front**, during planning. Otherwise a surface drops out silently —
nobody notices that nobody checked it.

## Where it applies

**Works** anywhere there is more than one environment: local versus CI, staging
versus production, emulator versus device.

The generalisation: **green in an environment missing the necessary links is not
proof.** A test that could not have failed has checked nothing.

**Does not work** where the single environment is complete: then the split is
overhead.

## Trace

ArtVsMark/Stepik-Python-Grader — `docs/agent/environments.md`