# Rules

One file, one rule. The shape: rule → incident → why → where it applies → trace.

| № | Rule | Area |
|---|---|---|
| [001](001-transport-rest-not-graphql.md) | Talking to GitHub: REST by default, GraphQL only where REST cannot | quotas, API |
| [002](002-rule-without-mechanism.md) | A rule without a mechanism is a promise, not a guarantee | process, CI |
| [003](003-branch-name-is-a-switch.md) | A branch name can be a behaviour switch, not a style convention | pipeline |
| [004](004-conflict-is-normal-not-outage.md) | A conflict is normal pipeline traffic, not an outage | pipeline, automation |
| [005](005-hand-written-numbers-rot.md) | A number typed by hand goes stale in silence | documentation |
| [006](006-window-lifetime.md) | An agent session lives three to five days | agent sessions |
| [007](007-blocked-window-looks-alive.md) | A session stalled on a permission prompt looks exactly like a working one | agent sessions |
| [008](008-details-is-a-stub-in-text.md) | A collapsible block reads as a stub wherever the page is consumed as text | showcases |
| [009](009-count-unique-not-total.md) | Count unique names, not records | metrics |
| [010](010-empty-checklist-is-not-green.md) | An empty list of checks means "never started", not "all clear" | CI |
| [011](011-events-not-polling.md) | Watching: events over polling, and if polling, then conditional | quotas, observation |
| [012](012-do-not-push-to-someone-elses-branch.md) | Do not push into somebody else's branch | collaboration |
| [013](013-write-escapes-to-file-not-heredoc.md) | Write code containing escapes to a file, not through a heredoc | tooling |
| [014](014-red-before-fix-needs-partial-revert.md) | "The test goes red without the fix" is proved by a partial revert, not a full one | tests |
| [015](015-agents-return-data-host-writes-files.md) | Agents return data — the host writes the files | parallel work |
| [016](016-no-silent-truncation.md) | Output is never truncated silently — only with a marker | output, reports |
| [017](017-measure-quota-do-not-guess.md) | Measure what is left of the quota instead of guessing — and look first | quotas, diagnostics |
| [018](018-cloud-checks-nodes-local-checks-chain.md) | One environment checks the nodes, the other checks the chain | environments |
| [019](019-audit-from-surfaces-not-files.md) | An audit is planned from the product's surfaces, not from its files | audit |
| [020](020-restart-only-the-delta.md) | After a failure, restart the delta, not the whole wave | parallel work |
| [021](021-split-docs-by-reader.md) | Split documentation by reader, not by topic | documentation |
| [022](022-one-canonical-document.md) | One topic, one canonical document; everything else links to it | documentation |
| [023](023-readme-is-a-storefront.md) | The README is a storefront, not a dumping ground for technical memory | showcases |
| [024](024-no-worklog-in-active-docs.md) | A live document carries no work log | documentation |
| [025](025-issue-links-by-zone.md) | A link to a task belongs in a log and hurts in an explanation | documentation |
| [026](026-rejected-findings-must-be-recorded.md) | A rejected finding is recorded together with its reason | audit |
| [027](027-empty-state-is-a-state.md) | An empty state must be declared explicitly | documentation, интерфейсы |
| [028](028-checklist-not-a-list-of-findings.md) | A complex task keeps a checklist, not a narrative | трекер |
| [029](029-triggers-and-canon.md) | A compact trigger in the main file, the details in the canon | documentation |
| [030](030-changelog-from-fragments.md) | The changelog is assembled from fragments, not written afterwards | release |
| [031](031-waves-not-salvos.md) | Parallel executors launch in waves of fixed size | parallel work |
| [032](032-role-must-run-the-product.md) | If a role's subject is observable in the running product, the role must run it | roles, audit |
| [033](033-pace-from-limit-not-desire.md) | The pace of long work is derived from the limit, not from eagerness | quotas, pace |
| [034](034-small-zone-per-executor.md) | One executor's zone must be small | parallel work |
| [035](035-version-is-never-edited-by-hand.md) | The version is never edited by hand, in any file | release |
| [036](036-expensive-window-enters-twice-and-briefly.md) | The expensive environment enters an audit twice, and briefly | audit, environments |
| [037](037-finding-status-depends-on-window.md) | A finding obtained on the wrong surface is a hypothesis | audit |
| [038](038-window-name-declares-its-environment.md) | A session's name starts with its environment, not with its task | agent sessions |
| [039](039-three-outcomes-not-two.md) | A check has three outcomes, not two | CI, reliability |
| [040](040-skip-without-reason-is-a-forgotten-test.md) | A skip without a reason is indistinguishable from a forgotten test | tests |
| [041](041-two-honest-numbers-beat-one-averaged.md) | Two honest metrics beat one averaged number | metrics |
| [042](042-decision-records-its-alternatives.md) | A decision is recorded together with the options rejected | decisions |
| [043](043-decisions-are-superseded-not-edited.md) | A decision is not edited after the fact — a new one supersedes it | decisions |
| [044](044-check-the-premise-before-fixing.md) | Verify a finding's premise before working from it | audit |
| [045](045-no-silent-fallback.md) | There is no silent fallback — failure is loud | reliability |
| [046](046-name-the-gaps-do-not-level-them.md) | Name the gap in a guarantee; do not level it on paper | documentation, security |
| [047](047-rule-change-restarts-the-windows.md) | Changing the working rules is a reason to restart the sessions, not to send a memo | agent sessions |
| [048](048-calibration-needs-a-complete-input.md) | Calibrating against an external signal requires a complete input | metrics, quotas |
| [049](049-derive-state-from-live-artifacts.md) | Derive state from live artefacts, not from a register kept by hand | pipeline, process |
| [050](050-limits-move-down-only.md) | A gate's budget only moves down | gates |
| [051](051-warn-on-likely-block-on-certain.md) | Warn about the likely, block only the certain | gates |
| [052](052-only-the-head-of-the-queue-moves.md) | Only the head of the queue updates from the shared branch | pipeline |
| [053](053-queue-order-is-a-rule-not-arrival.md) | Queue order is set by a rule, not by who went green first | pipeline |
| [054](054-collect-and-analyse-are-separate-passes.md) | Collecting and analysing are separate passes | прогоны, process |
| [055](055-your-own-expectations-are-a-hypothesis.md) | Your own reference answer is also a hypothesis | tests, audit |
| [056](056-a-signal-states-what-it-does-not-mean.md) | A signal also states what it does not mean | contracts, documentation |
| [057](057-unmechanizable-rules-are-named-explicitly.md) | A rule no machine can check is named explicitly | process |
| [058](058-when-the-quota-is-out-stop.md) | When the quota is exhausted, stop — do not retry | quotas |
| [059](059-map-the-detour-before-the-resource-runs-out.md) | Every exhaustible resource has a detour map prepared in advance | quotas, planning |
| [060](060-debrief-every-wave-quality-first.md) | Debrief after every wave, and quality matters more than mechanics | parallel work |
| [061](061-environment-bans-belong-in-the-task.md) | Environment prohibitions go into the task text, never implied | parallel work |
| [062](062-a-role-must-be-able-to-object.md) | A role is created if it can object, not merely add | roles |
| [063](063-automatic-intervention-needs-all-conditions.md) | Automatic intervention fires only when all conditions hold | automation |
| [064](064-labels-are-machine-input-not-decoration.md) | Labels are machine input, not decoration | process, pipeline |
| [065](065-the-onramp-must-speak-the-newcomers-language.md) | The newcomer's entry point speaks their language — and there is more than one | community |
| [066](066-lock-the-companion-not-the-target.md) | Lock the companion file, not the file that gets replaced wholesale | code, concurrency |
| [067](067-cleanup-must-not-swallow-the-failure.md) | Cleanup after a failure must not turn the failure into a success | code, reliability |
| [068](068-allowlist-not-denylist.md) | An allowlist, not a denylist | security |
| [069](069-write-the-field-not-the-snapshot.md) | Write the field, not the snapshot, when there are several writers | code, concurrency |
| [070](070-a-heuristic-guard-fails-open-with-a-written-risk.md) | A heuristic guard is relaxed deliberately — with the residual risk written down | security |
| [071](071-deliberate-duplication-is-signed.md) | Deliberate duplication is signed | code, architecture |
| [072](072-guard-the-cause-and-the-effect.md) | The gate catches the cause, the fixture catches the effect: you need both | tests, gates |
| [073](073-tool-version-from-one-source-with-an-upper-bound.md) | A tool's version comes from one source and has an upper bound | tooling |
| [074](074-one-shot-irreversible-steps-get-their-own-guard.md) | An irreversible step is guarded by invariants checked in advance | release, CI |
| [075](075-a-guard-that-finds-nothing-must-fail.md) | A gate that cannot find its subject must fail | gates |
| [076](076-messages-point-at-what-the-user-actually-has.md) | A message points at what the recipient actually has | interface |
| [077](077-key-parity-is-not-translation.md) | Matching keys are not a translation | localisation |
| [078](078-cancelled-is-not-an-error.md) | Cancellation is its own outcome, not a kind of error | contracts |
| [079](079-ttl-counts-from-completion.md) | Retention is counted from completion, not from enqueueing | code, resources |
| [080](080-every-new-rule-goes-into-the-catalogue.md) | A rule born in a project is recorded in the shared catalogue | process, catalogue |
| [081](081-untrusted-code-runs-in-a-private-directory.md) | Untrusted code runs from a private directory, not from the shared temp | security |
| [082](082-roles-must-cover-every-layer.md) | The role line-up covers every layer of the product, not just development | roles |
| [083](083-generated-output-is-checked-by-properties.md) | Generated output is checked by properties and by sampling, not against a reference answer | AI, quality |
| [084](084-best-effort-channels-never-block-the-main-path.md) | An optional channel neither delays nor breaks the main work | architecture |
| [085](085-content-from-the-subject-is-untrusted-input-to-the-prompt.md) | Text coming from the subject under review is untrusted input to the prompt | AI, security |
| [086](086-the-finder-does-not-grade-the-finding.md) | The severity of a finding is not set by whoever found it — but the refuter needs a scale | audit |
| [087](087-a-second-pass-needs-a-novelty-rule.md) | A second pass receives the previous findings and a ban on reopening them | audit |
| [088](088-the-critic-checks-the-method-not-the-subject.md) | The critic checks the phase's method, not the subject of the work | audit, process |
| [089](089-never-link-from-the-original-to-its-copy.md) | Never link from the original to its copy | documentation |
| [090](090-shared-helpers-move-up-not-sideways.md) | A shared helper moves up, not sideways | architecture |
| [091](091-work-sources-are-ordered-first-non-empty-wins.md) | Work sources are ordered: the first non-empty one is the plan | process |
| [092](092-findings-and-ordering-live-in-different-documents.md) | Findings and the order of work live in different documents | audit, documentation |
| [093](093-seam-early-generalisation-late.md) | Introduce the seam early, generalise on the third case | architecture |
| [094](094-a-compatibility-shim-makes-migration-permanent.md) | A compatibility shim makes the migration permanent | architecture, migrations |
| [095](095-the-default-is-chosen-for-the-user.md) | The default is chosen in the user's favour, not the product's | privacy, product |
| [096](096-storage-follows-lifecycle-not-convenience.md) | Storage is chosen by the data's lifecycle, not by convenience | architecture, data |
| [097](097-a-checker-has-two-error-types.md) | A checking tool has two errors, and each is held by its own test | tests, quality |
| [098](098-the-unit-of-splitting-follows-usage.md) | The unit of splitting follows usage, not a formal criterion | data, documentation |
| [099](099-classification-conflicts-resolve-by-consequence.md) | A classification conflict is resolved by consequence, not by correctness | taxonomy |
| [100](100-two-deadlines-start-and-work.md) | There are two deadlines: one for starting, one for working | reliability |
| [101](101-retry-only-what-can-heal-itself.md) | Retry only the failures that can pass on their own | network, reliability |
| [102](102-leniency-is-enumerated-and-switchable.md) | Leniency is enumerated in a table and switched off by a mode | comparison, quality |
| [103](103-a-side-effect-guard-blames-the-wrong-suspect.md) | A side-effect guard blames the wrong suspect — and exclusions are defined by shape | tests, gates |
| [104](104-event-driven-automation-needs-a-manual-button.md) | Event-driven automation needs a manual button | CI, automation |
| [105](105-an-outside-audit-needs-outside-eyes.md) | An outside audit is done by somebody who did not write this code | audit |
| [106](106-publicity-multiplies-both-sides.md) | Publicity multiplies both the good and the bad — do the real run first | product, release |
| [107](107-it-works-for-the-author-means-tested-on-the-authors-sample.md) | "It works for the author" means "tested on the author's sample" | borrowing |
| [108](108-a-living-document-keeps-a-fixed-window.md) | A living document keeps a fixed window; the rest moves out verbatim | documentation |
| [109](109-every-exit-from-a-transient-state-must-be-terminal.md) | Every exit from a transient state must be terminal | code, interface |
| [110](110-fail-before-you-take-anything-over.md) | Everything that can fail happens before you replace global state | code, reliability |
| [111](111-do-it-instead-of-advising-it.md) | If the tool can do it itself, it does it rather than advising | interface |
| [112](112-whatever-the-tool-created-it-must-be-able-to-delete.md) | Whatever the tool created, it must be able to delete | privacy, product |
| [113](113-a-contract-states-how-it-may-change.md) | A contract states the rules of its own evolution | contracts |
| [114](114-migrate-from-the-current-version-not-from-zero.md) | Migrate from the current version, not from zero | data, migrations |
| [115](115-config-has-one-anchor-and-a-bounded-search.md) | Settings have one anchor and a bounded search area | configuration |
| [116](116-the-collector-script-is-a-source-of-loss.md) | The collector script is also a source of loss, and it has its own reconciliation | parallel work |
| [117](117-numeric-limits-belong-in-the-task-spec.md) | An executor's brief carries numeric limits | parallel work |
| [118](118-keep-the-source-next-to-the-derived.md) | Keep the source next to the derived | data |
| [119](119-tool-artefacts-stay-outside-the-input-mask.md) | A tool's own artefacts stay outside its input mask | code, data |
| [120](120-how-to-run-a-rule-catalogue.md) | A rule catalogue runs by its own rules, and its index is generated | catalogue, process |
| [121](121-closing-the-container-is-not-closing-the-work.md) | Closing the container is not proof that the work is closed | process, audit |
| [122](122-ship-the-raw-value-next-to-the-formatted-one.md) | Ship the raw value next to the formatted one | contracts, data |
| [123](123-attribution-is-verified-on-the-final-history.md) | Attribution is verified against the final history, not against the branch commit | pipeline, history |
| [124](124-rerun-the-minimum-and-record-the-flake.md) | Re-run the minimum — but green on the second try is a finding, not a fix | CI, tests |

## How to add your own

A rule is born — the record is written the same day. The material spoils fast:
incidents a month old have to be reconstructed from documents, because nobody
remembers them any more.

Two parts are mandatory and are the ones most often skipped:

- **Where it applies** — where the rule does **not** work. Without it the
  catalogue gets copied wholesale, including what plainly belongs to somebody
  else.
- **Trace** — a link to the issue, pull request or document where the failure is
  visible. Without it, within a month the record becomes "somebody said this was
  better".

The Russian originals live in [`../ru/`](../ru/README.md). The two trees use the
same file names, so cross-references between rules resolve identically in both.
