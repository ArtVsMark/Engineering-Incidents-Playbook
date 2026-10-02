# A run names whose code it is checking, not only what it was launched with

**Area.** runs, environments

**Tier.** 3 — gates and processes

**The rule.** A run whose code under test may come from somewhere other than
the working tree names the source of that code and says so out loud when the
source is not the tree. The source is asked of the runtime — where the package
is actually imported from — not derived from the run's root: the root knows
nothing about the installation. This is a warning on the first line of the
report, not a refusal: a setup where code and tree diverge can be legitimate.

**Portable beyond Claude Code.** yes — the subject exists in any project where
the package is installed in editable mode and work goes on in several working
trees or clones: for a person with two terminals as much as for parallel agent
windows.

## The incident

**The grader, one session, two opposite outcomes**
(ArtVsMark/Stepik-Python-Grader#1521). The package was installed into the
interpreter in editable mode (`pip install -e`) from the main clone. Work ran
in several working trees of one repository (`git worktree`), a setup adopted
for parallel tasks. The run takes tests and scripts by path from the current
tree, while `import stepik_grader` from a working tree leads back to the main
clone:

```
$ cd /home/user/wt-1517
$ python -c "import stepik_grader, pathlib; print(pathlib.Path(stepik_grader.__file__).parent)"
/home/user/Stepik-Python-Grader/src/stepik_grader
```

- **False green.** The fix for #1517 sat in the working tree, and the run kept
  showing the old verdict: `AC` instead of `OLE`. The core change took no part
  in the run. From outside this reads as "the fix does not work", and the next
  step is to repair working code.
- **False red.** Branch #1510 changed only `scripts/` and failed on
  `tests/test_output_comparison.py::test_truncated_output_says_so`: its test
  expected `WA`, while the main clone sat on a third branch, #1517, where the
  verdict was already `OLE`. The failure had nothing to do with #1510.

The checked state existed in no branch at all: the run honestly executed a
hybrid of "my tests against someone else's code". The cause took three
commands to find (`import`, `pgrep`, comparing paths), and only because the
divergence was suspected. The run itself said nothing.

**What did not fit.** Both first answers would have removed the symptom at the
cost of the setup. Forbidding working trees cancels the parallel work they
exist for, though for `scripts/`, `tests/` and documentation they are correct.
Reinstalling the package before every run costs minutes per run and breaks
neighbouring runs: there is one installation per interpreter. The grader took
a third way (#1528): the first line of the report prints where the package
came from, and says so plainly when it diverges from the run's root.

## Why

**A run knows what it was launched with, not what it is checking.** A gate's
report naturally names the interpreter, the root and the set of steps — its
inputs. The code under test is not on that list: the import machinery decides
its path, not the run. While code and tree coincide there is no difference.
They diverge quietly: an editable install is bound to one clone for the whole
interpreter, while working trees can be many.

**Both errors lead to fixing the wrong thing.** A false green sends you to
repair a fix that works; a false red, to look for the cause in a change that
has nothing to do with it. Either costs a round of investigation; a line in
the report costs one `import` at the start of the run.

**Ask the runtime, do not derive from the root.** The path "run root + `src/`"
always points at the current tree and therefore always matches. It says where
the code SHOULD have come from, not where it did. Only the importer knows:
`package.__file__`.

**A warning, not a refusal** ([051](051-warn-on-likely-block-on-certain.md)).
The divergence is legitimate: a test change in a working tree against the
main clone's code is exactly what is wanted. A gate that goes red on a correct
setup gets removed at the first edit. It is enough that the substitution is
visible before the investigation, not after it.

## In practice

- the source of the code under test is printed on the first line of the
  report: the run's other answers only mean something after it;
- the source comes from the import (`package.__file__`), not from the run's
  root and not from `pip show`: the latter talks about the installation, not
  about what was loaded;
- what is compared is the TREE holding that file against the run's root; a
  path in `site-packages` is not a tree — a regular install gets no warning;
- on divergence from the run's root both paths are printed — where the code
  lies and where it was taken from;
- the window's document names which changes are legitimate in a working tree
  and which are made where the package is installed from; before a run in a
  working tree the main clone sits on the shared branch, otherwise a third
  branch leaks into the run.

## Where it applies

**Works** where the code under test reaches the run from ANOTHER SOURCE
TREE: an editable install (`pip install -e`) or a `PYTHONPATH` pointing at a
neighbouring clone or working tree — with several trees, clones or windows on
one machine. The tree that holds `package.__file__` is compared with the
run's root; equal — silence, different — a warning.

**Does not work** for a regular, non-editable install: `package.__file__` is
always in `site-packages` there, a copy rather than a tree, and the warning
would fire on every run with no signal — exactly what
[051](051-warn-on-likely-block-on-certain.md) stands against here. Whether the
installed copy is fresh is another question, and 216 does not answer it. It
does not work where the code is taken by path from the run's own root: tests
put the scripts directory of their own tree on `sys.path`, and the code has no
other source. It does not work for CI with one checkout per runner and any
installation made from that same checkout: the run has a single source tree. It does
not work for the REFERENCE a change is compared against — that is
[171](171-the-reference-set-comes-from-the-tree-under-test.md); this rule is
about the code under test itself.

**Sign of a violation:** the run's report names the interpreter and the root
but not where the package under test was imported from, while
`package.__file__` taken from a working tree lies in ANOTHER source tree — a
neighbouring clone or working tree. A path in `site-packages` is not a sign:
that is a regular install, and 216 says nothing about it.

## Trace

ArtVsMark/Stepik-Python-Grader#1521

Related: [171](171-the-reference-set-comes-from-the-tree-under-test.md) — the
reference comes from the change's tree; here, the code under test itself;
[037](037-finding-status-depends-on-window.md) — green taken on the wrong
surface stays a hypothesis; here the surface is swapped silently, and the rule
makes the swap visible; [051](051-warn-on-likely-block-on-certain.md) — why
this is a warning and not a refusal.
