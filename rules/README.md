# Правила · Rules

Один файл — одно правило, одинаковое имя в обоих деревьях.
One file, one rule, the same file name in both trees.

Формат: правило → инцидент → почему → применимость → след.
Shape: rule → incident → why → where it applies → trace.

> **Этот файл собирается скриптом** `scripts/build_rules_index.py` и не правится
> руками. Правило, добавленное только на одном языке, не пройдёт сборку — это и
> есть механизм, который не даёт деревьям разойтись.
>
> **This file is generated** by `scripts/build_rules_index.py` and is never
> edited by hand. A rule added in only one language fails the build — that is the
> mechanism keeping the two trees from diverging.

Всего правил · rules in total: **124**

| № | Правило | Rule | Файлы · Files | Область · Area |
|---|---|---|---|---|
| 001 | Транспорт к GitHub: REST по умолчанию, GraphQL только там, где REST не умеет | Talking to GitHub: REST by default, GraphQL only where REST cannot | [ru](ru/001-transport-rest-not-graphql.md) [en](en/001-transport-rest-not-graphql.md) |  |
| 002 | Правило без механизма — обещание, а не гарантия | A rule without a mechanism is a promise, not a guarantee | [ru](ru/002-rule-without-mechanism.md) [en](en/002-rule-without-mechanism.md) |  |
| 003 | Имя ветки может быть переключателем поведения, а не соглашением о стиле | A branch name can be a behaviour switch, not a style convention | [ru](ru/003-branch-name-is-a-switch.md) [en](en/003-branch-name-is-a-switch.md) |  |
| 004 | Конфликт — штатная ситуация конвейера, а не авария | A conflict is normal pipeline traffic, not an outage | [ru](ru/004-conflict-is-normal-not-outage.md) [en](en/004-conflict-is-normal-not-outage.md) |  |
| 005 | Число, вписанное руками, устаревает молча | A number typed by hand goes stale in silence | [ru](ru/005-hand-written-numbers-rot.md) [en](en/005-hand-written-numbers-rot.md) |  |
| 006 | Агентское окно живёт три–пять дней | An agent session lives three to five days | [ru](ru/006-window-lifetime.md) [en](en/006-window-lifetime.md) |  |
| 007 | Окно, зависшее на разрешении, снаружи неотличимо от работающего | A session stalled on a permission prompt looks exactly like a working one | [ru](ru/007-blocked-window-looks-alive.md) [en](en/007-blocked-window-looks-alive.md) |  |
| 008 | Сворачиваемый блок выглядит обрубком там, где страницу читают текстом | A collapsible block reads as a stub wherever the page is consumed as text | [ru](ru/008-details-is-a-stub-in-text.md) [en](en/008-details-is-a-stub-in-text.md) |  |
| 009 | Считайте уникальные имена, а не записи | Count unique names, not records | [ru](ru/009-count-unique-not-total.md) [en](en/009-count-unique-not-total.md) |  |
| 010 | Пустой список проверок означает «не стартовало», а не «всё хорошо» | An empty list of checks means "never started", not "all clear" | [ru](ru/010-empty-checklist-is-not-green.md) [en](en/010-empty-checklist-is-not-green.md) |  |
| 011 | Наблюдение: событие вместо опроса, а если опрос — то условный | Watching: events over polling, and if polling, then conditional | [ru](ru/011-events-not-polling.md) [en](en/011-events-not-polling.md) |  |
| 012 | В чужую ветку не пушить | Do not push into somebody else's branch | [ru](ru/012-do-not-push-to-someone-elses-branch.md) [en](en/012-do-not-push-to-someone-elses-branch.md) |  |
| 013 | Код с экранированием писать файлом, а не heredoc'ом | Write code containing escapes to a file, not through a heredoc | [ru](ru/013-write-escapes-to-file-not-heredoc.md) [en](en/013-write-escapes-to-file-not-heredoc.md) |  |
| 014 | «Тест краснеет до фикса» доказывается полу-откатом, а не откатом всего | "The test goes red without the fix" is proved by a partial revert, not a full one | [ru](ru/014-red-before-fix-needs-partial-revert.md) [en](en/014-red-before-fix-needs-partial-revert.md) |  |
| 015 | Агенты возвращают данные — файлы правит хост | Agents return data — the host writes the files | [ru](ru/015-agents-return-data-host-writes-files.md) [en](en/015-agents-return-data-host-writes-files.md) |  |
| 016 | Обрезать вывод молча нельзя — только с маркером обрыва | Output is never truncated silently — only with a marker | [ru](ru/016-no-silent-truncation.md) [en](en/016-no-silent-truncation.md) |  |
| 017 | Остаток лимита мерить, а не угадывать — и смотреть первым шагом | Measure what is left of the quota instead of guessing — and look first | [ru](ru/017-measure-quota-do-not-guess.md) [en](en/017-measure-quota-do-not-guess.md) |  |
| 018 | Одно окружение проверяет узлы, другое — цепочку | One environment checks the nodes, the other checks the chain | [ru](ru/018-cloud-checks-nodes-local-checks-chain.md) [en](en/018-cloud-checks-nodes-local-checks-chain.md) |  |
| 019 | Аудит планируется от поверхностей продукта, а не от файлов | An audit is planned from the product's surfaces, not from its files | [ru](ru/019-audit-from-surfaces-not-files.md) [en](en/019-audit-from-surfaces-not-files.md) |  |
| 020 | После сбоя перезапускать дельту, а не всю волну | After a failure, restart the delta, not the whole wave | [ru](ru/020-restart-only-the-delta.md) [en](en/020-restart-only-the-delta.md) |  |
| 021 | Документацию делят по читателю, а не по теме | Split documentation by reader, not by topic | [ru](ru/021-split-docs-by-reader.md) [en](en/021-split-docs-by-reader.md) |  |
| 022 | Одна тема — один канонический документ, остальные ссылаются | One topic, one canonical document; everything else links to it | [ru](ru/022-one-canonical-document.md) [en](en/022-one-canonical-document.md) |  |
| 023 | README — витрина, а не свалка технической памяти | The README is a storefront, not a dumping ground for technical memory | [ru](ru/023-readme-is-a-storefront.md) [en](en/023-readme-is-a-storefront.md) |  |
| 024 | В действующем документе нет журнала работ | A live document carries no work log | [ru](ru/024-no-worklog-in-active-docs.md) [en](en/024-no-worklog-in-active-docs.md) |  |
| 025 | Ссылка на задачу уместна в журнале и вредна в объяснении | A link to a task belongs in a log and hurts in an explanation | [ru](ru/025-issue-links-by-zone.md) [en](en/025-issue-links-by-zone.md) |  |
| 026 | Отклонённая находка фиксируется с причиной | A rejected finding is recorded together with its reason | [ru](ru/026-rejected-findings-must-be-recorded.md) [en](en/026-rejected-findings-must-be-recorded.md) |  |
| 027 | Пустое состояние надо объявлять явно | An empty state must be declared explicitly | [ru](ru/027-empty-state-is-a-state.md) [en](en/027-empty-state-is-a-state.md) |  |
| 028 | Комплексная задача ведёт чек-лист, а не перечисление | A complex task keeps a checklist, not a narrative | [ru](ru/028-checklist-not-a-list-of-findings.md) [en](en/028-checklist-not-a-list-of-findings.md) |  |
| 029 | Компактный триггер в главном файле, детали — в каноне | A compact trigger in the main file, the details in the canon | [ru](ru/029-triggers-and-canon.md) [en](en/029-triggers-and-canon.md) |  |
| 030 | Журнал изменений собирается из фрагментов, а не пишется задним числом | The changelog is assembled from fragments, not written afterwards | [ru](ru/030-changelog-from-fragments.md) [en](en/030-changelog-from-fragments.md) |  |
| 031 | Параллельные исполнители запускаются волнами фиксированного размера | Parallel executors launch in waves of fixed size | [ru](ru/031-waves-not-salvos.md) [en](en/031-waves-not-salvos.md) |  |
| 032 | Если предмет роли наблюдаем в работающем продукте — роль обязана его запустить | If a role's subject is observable in the running product, the role must run it | [ru](ru/032-role-must-run-the-product.md) [en](en/032-role-must-run-the-product.md) |  |
| 033 | Темп длинной работы считается от лимита, а не от желания | The pace of long work is derived from the limit, not from eagerness | [ru](ru/033-pace-from-limit-not-desire.md) [en](en/033-pace-from-limit-not-desire.md) |  |
| 034 | Зона одного исполнителя должна быть маленькой | One executor's zone must be small | [ru](ru/034-small-zone-per-executor.md) [en](en/034-small-zone-per-executor.md) |  |
| 035 | Версия не правится руками ни в одном файле | The version is never edited by hand, in any file | [ru](ru/035-version-is-never-edited-by-hand.md) [en](en/035-version-is-never-edited-by-hand.md) |  |
| 036 | Дорогое окружение входит в аудит дважды и коротко | The expensive environment enters an audit twice, and briefly | [ru](ru/036-expensive-window-enters-twice-and-briefly.md) [en](en/036-expensive-window-enters-twice-and-briefly.md) |  |
| 037 | Находка, полученная не на той поверхности, — гипотеза | A finding obtained on the wrong surface is a hypothesis | [ru](ru/037-finding-status-depends-on-window.md) [en](en/037-finding-status-depends-on-window.md) |  |
| 038 | Имя окна начинается с окружения, а не с задачи | A session's name starts with its environment, not with its task | [ru](ru/038-window-name-declares-its-environment.md) [en](en/038-window-name-declares-its-environment.md) |  |
| 039 | У проверки три исхода, а не два | A check has three outcomes, not two | [ru](ru/039-three-outcomes-not-two.md) [en](en/039-three-outcomes-not-two.md) |  |
| 040 | Пропуск без причины неотличим от забытого теста | A skip without a reason is indistinguishable from a forgotten test | [ru](ru/040-skip-without-reason-is-a-forgotten-test.md) [en](en/040-skip-without-reason-is-a-forgotten-test.md) |  |
| 041 | Две честные метрики лучше одной усреднённой | Two honest metrics beat one averaged number | [ru](ru/041-two-honest-numbers-beat-one-averaged.md) [en](en/041-two-honest-numbers-beat-one-averaged.md) |  |
| 042 | Решение записывается вместе с отвергнутыми вариантами | A decision is recorded together with the options rejected | [ru](ru/042-decision-records-its-alternatives.md) [en](en/042-decision-records-its-alternatives.md) |  |
| 043 | Решение не правится задним числом — его отменяет новое | A decision is not edited after the fact — a new one supersedes it | [ru](ru/043-decisions-are-superseded-not-edited.md) [en](en/043-decisions-are-superseded-not-edited.md) |  |
| 044 | Премиса находки проверяется прежде, чем по ней работают | Verify a finding's premise before working from it | [ru](ru/044-check-the-premise-before-fixing.md) [en](en/044-check-the-premise-before-fixing.md) |  |
| 045 | Тихого запасного пути нет — отказ громкий | There is no silent fallback — failure is loud | [ru](ru/045-no-silent-fallback.md) [en](en/045-no-silent-fallback.md) |  |
| 046 | Пробел в гарантии называется поимённо, а не выравнивается на бумаге | Name the gap in a guarantee; do not level it on paper | [ru](ru/046-name-the-gaps-do-not-level-them.md) [en](en/046-name-the-gaps-do-not-level-them.md) |  |
| 047 | Смена правил работы — повод перезапустить окна, а не рассылка | Changing the working rules is a reason to restart the sessions, not to send a memo | [ru](ru/047-rule-change-restarts-the-windows.md) [en](en/047-rule-change-restarts-the-windows.md) |  |
| 048 | Калибровка по внешнему сигналу требует полноты входа | Calibrating against an external signal requires a complete input | [ru](ru/048-calibration-needs-a-complete-input.md) [en](en/048-calibration-needs-a-complete-input.md) |  |
| 049 | Состояние выводится из живых артефактов, а не из реестра, который ведут руками | Derive state from live artefacts, not from a register kept by hand | [ru](ru/049-derive-state-from-live-artifacts.md) [en](en/049-derive-state-from-live-artifacts.md) |  |
| 050 | Бюджет ограничителя двигают только вниз | A gate's budget only moves down | [ru](ru/050-limits-move-down-only.md) [en](en/050-limits-move-down-only.md) |  |
| 051 | Предупреждают о вероятном, запрещают достоверное | Warn about the likely, block only the certain | [ru](ru/051-warn-on-likely-block-on-certain.md) [en](en/051-warn-on-likely-block-on-certain.md) |  |
| 052 | Из общей ветки обновляется только голова очереди | Only the head of the queue updates from the shared branch | [ru](ru/052-only-the-head-of-the-queue-moves.md) [en](en/052-only-the-head-of-the-queue-moves.md) |  |
| 053 | Порядок очереди задаётся правилом, а не готовностью | Queue order is set by a rule, not by who went green first | [ru](ru/053-queue-order-is-a-rule-not-arrival.md) [en](en/053-queue-order-is-a-rule-not-arrival.md) |  |
| 054 | Сбор и разбор — разные проходы | Collecting and analysing are separate passes | [ru](ru/054-collect-and-analyse-are-separate-passes.md) [en](en/054-collect-and-analyse-are-separate-passes.md) |  |
| 055 | Собственный эталон — тоже гипотеза | Your own reference answer is also a hypothesis | [ru](ru/055-your-own-expectations-are-a-hypothesis.md) [en](en/055-your-own-expectations-are-a-hypothesis.md) |  |
| 056 | У сигнала пишут и то, чего он не означает | A signal also states what it does not mean | [ru](ru/056-a-signal-states-what-it-does-not-mean.md) [en](en/056-a-signal-states-what-it-does-not-mean.md) |  |
| 057 | Правило, которое нельзя проверить машиной, называется явно | A rule no machine can check is named explicitly | [ru](ru/057-unmechanizable-rules-are-named-explicitly.md) [en](en/057-unmechanizable-rules-are-named-explicitly.md) |  |
| 058 | Исчерпав квоту — остановиться, а не повторять | When the quota is exhausted, stop — do not retry | [ru](ru/058-when-the-quota-is-out-stop.md) [en](en/058-when-the-quota-is-out-stop.md) |  |
| 059 | У каждого исчерпаемого ресурса есть заранее составленная карта обхода | Every exhaustible resource has a detour map prepared in advance | [ru](ru/059-map-the-detour-before-the-resource-runs-out.md) [en](en/059-map-the-detour-before-the-resource-runs-out.md) |  |
| 060 | Разбор после каждой волны, и качество важнее механики | Debrief after every wave, and quality matters more than mechanics | [ru](ru/060-debrief-every-wave-quality-first.md) [en](en/060-debrief-every-wave-quality-first.md) |  |
| 061 | Запреты окружения пишутся в задании, а не подразумеваются | Environment prohibitions go into the task text, never implied | [ru](ru/061-environment-bans-belong-in-the-task.md) [en](en/061-environment-bans-belong-in-the-task.md) |  |
| 062 | Роль заводится, если способна возразить, а не дополнить | A role is created if it can object, not merely add | [ru](ru/062-a-role-must-be-able-to-object.md) [en](en/062-a-role-must-be-able-to-object.md) |  |
| 063 | Автоматическое вмешательство включается по всем условиям сразу | Automatic intervention fires only when all conditions hold | [ru](ru/063-automatic-intervention-needs-all-conditions.md) [en](en/063-automatic-intervention-needs-all-conditions.md) |  |
| 064 | Метки — вход механизма, а не украшение | Labels are machine input, not decoration | [ru](ru/064-labels-are-machine-input-not-decoration.md) [en](en/064-labels-are-machine-input-not-decoration.md) |  |
| 065 | Точка входа для новичка пишется на его языке — и не одна | The newcomer's entry point speaks their language — and there is more than one | [ru](ru/065-the-onramp-must-speak-the-newcomers-language.md) [en](en/065-the-onramp-must-speak-the-newcomers-language.md) |  |
| 066 | Блокировку берут на спутника, а не на файл, который заменяется целиком | Lock the companion file, not the file that gets replaced wholesale | [ru](ru/066-lock-the-companion-not-the-target.md) [en](en/066-lock-the-companion-not-the-target.md) |  |
| 067 | Уборка после сбоя не превращает сбой в успех | Cleanup after a failure must not turn the failure into a success | [ru](ru/067-cleanup-must-not-swallow-the-failure.md) [en](en/067-cleanup-must-not-swallow-the-failure.md) |  |
| 068 | Список разрешённого, а не список запрещённого | An allowlist, not a denylist | [ru](ru/068-allowlist-not-denylist.md) [en](en/068-allowlist-not-denylist.md) |  |
| 069 | Пишем поле, а не снимок, если писателей несколько | Write the field, not the snapshot, when there are several writers | [ru](ru/069-write-the-field-not-the-snapshot.md) [en](en/069-write-the-field-not-the-snapshot.md) |  |
| 070 | Эвристическая защита ослабляется осознанно — с записью остаточного риска | A heuristic guard is relaxed deliberately — with the residual risk written down | [ru](ru/070-a-heuristic-guard-fails-open-with-a-written-risk.md) [en](en/070-a-heuristic-guard-fails-open-with-a-written-risk.md) |  |
| 071 | Намеренный дубль подписывается | Deliberate duplication is signed | [ru](ru/071-deliberate-duplication-is-signed.md) [en](en/071-deliberate-duplication-is-signed.md) |  |
| 072 | Причину ловит гейт, факт — фикстура: нужны обе | The gate catches the cause, the fixture catches the effect: you need both | [ru](ru/072-guard-the-cause-and-the-effect.md) [en](en/072-guard-the-cause-and-the-effect.md) |  |
| 073 | Версия инструмента — из одного источника и с верхней границей | A tool's version comes from one source and has an upper bound | [ru](ru/073-tool-version-from-one-source-with-an-upper-bound.md) [en](en/073-tool-version-from-one-source-with-an-upper-bound.md) |  |
| 074 | Необратимый шаг проверяется инвариантами заранее | An irreversible step is guarded by invariants checked in advance | [ru](ru/074-one-shot-irreversible-steps-get-their-own-guard.md) [en](en/074-one-shot-irreversible-steps-get-their-own-guard.md) |  |
| 075 | Гейт, не нашедший предмета проверки, обязан упасть | A gate that cannot find its subject must fail | [ru](ru/075-a-guard-that-finds-nothing-must-fail.md) [en](en/075-a-guard-that-finds-nothing-must-fail.md) |  |
| 076 | Сообщение ссылается на то, что есть у получателя | A message points at what the recipient actually has | [ru](ru/076-messages-point-at-what-the-user-actually-has.md) [en](en/076-messages-point-at-what-the-user-actually-has.md) |  |
| 077 | Совпадение ключей — ещё не перевод | Matching keys are not a translation | [ru](ru/077-key-parity-is-not-translation.md) [en](en/077-key-parity-is-not-translation.md) |  |
| 078 | Отмена — отдельный исход, а не разновидность ошибки | Cancellation is its own outcome, not a kind of error | [ru](ru/078-cancelled-is-not-an-error.md) [en](en/078-cancelled-is-not-an-error.md) |  |
| 079 | Срок хранения отсчитывается от завершения, а не от постановки | Retention is counted from completion, not from enqueueing | [ru](ru/079-ttl-counts-from-completion.md) [en](en/079-ttl-counts-from-completion.md) |  |
| 080 | Правило, родившееся в проекте, записывается в общий каталог | A rule born in a project is recorded in the shared catalogue | [ru](ru/080-every-new-rule-goes-into-the-catalogue.md) [en](en/080-every-new-rule-goes-into-the-catalogue.md) |  |
| 081 | Чужой код запускают из приватного каталога, а не из общего временного | Untrusted code runs from a private directory, not from the shared temp | [ru](ru/081-untrusted-code-runs-in-a-private-directory.md) [en](en/081-untrusted-code-runs-in-a-private-directory.md) |  |
| 082 | Состав ролей покрывает все пласты продукта, а не только разработку | The role line-up covers every layer of the product, not just development | [ru](ru/082-roles-must-cover-every-layer.md) [en](en/082-roles-must-cover-every-layer.md) |  |
| 083 | Сгенерированное проверяют свойствами и выборкой, а не эталонным ответом | Generated output is checked by properties and by sampling, not against a reference answer | [ru](ru/083-generated-output-is-checked-by-properties.md) [en](en/083-generated-output-is-checked-by-properties.md) |  |
| 084 | Необязательный канал не задерживает и не роняет основную работу | An optional channel neither delays nor breaks the main work | [ru](ru/084-best-effort-channels-never-block-the-main-path.md) [en](en/084-best-effort-channels-never-block-the-main-path.md) |  |
| 085 | Текст, пришедший от проверяемого, — недоверенный вход в промпт | Text coming from the subject under review is untrusted input to the prompt | [ru](ru/085-content-from-the-subject-is-untrusted-input-to-the-prompt.md) [en](en/085-content-from-the-subject-is-untrusted-input-to-the-prompt.md) |  |
| 086 | Тяжесть находки ставит не тот, кто её нашёл — но опровергателю нужна шкала | The severity of a finding is not set by whoever found it — but the refuter needs a scale | [ru](ru/086-the-finder-does-not-grade-the-finding.md) [en](en/086-the-finder-does-not-grade-the-finding.md) |  |
| 087 | Повторный проход получает на вход прошлые находки и запрет их переоткрывать | A second pass receives the previous findings and a ban on reopening them | [ru](ru/087-a-second-pass-needs-a-novelty-rule.md) [en](en/087-a-second-pass-needs-a-novelty-rule.md) |  |
| 088 | Критик проверяет метод фазы, а не предмет работы | The critic checks the phase's method, not the subject of the work | [ru](ru/088-the-critic-checks-the-method-not-the-subject.md) [en](en/088-the-critic-checks-the-method-not-the-subject.md) |  |
| 089 | Из оригинала в его копию не ссылаются | Never link from the original to its copy | [ru](ru/089-never-link-from-the-original-to-its-copy.md) [en](en/089-never-link-from-the-original-to-its-copy.md) |  |
| 090 | Общий хелпер поднимают вверх, а не втягивают вбок | A shared helper moves up, not sideways | [ru](ru/090-shared-helpers-move-up-not-sideways.md) [en](en/090-shared-helpers-move-up-not-sideways.md) |  |
| 091 | Источники работы упорядочены: первый непустой и есть план | Work sources are ordered: the first non-empty one is the plan | [ru](ru/091-work-sources-are-ordered-first-non-empty-wins.md) [en](en/091-work-sources-are-ordered-first-non-empty-wins.md) |  |
| 092 | Находки и порядок разбора — разные документы | Findings and the order of work live in different documents | [ru](ru/092-findings-and-ordering-live-in-different-documents.md) [en](en/092-findings-and-ordering-live-in-different-documents.md) |  |
| 093 | Шов вводят рано, обобщение — по третьему случаю | Introduce the seam early, generalise on the third case | [ru](ru/093-seam-early-generalisation-late.md) [en](en/093-seam-early-generalisation-late.md) |  |
| 094 | Переходная заглушка делает миграцию вечной | A compatibility shim makes the migration permanent | [ru](ru/094-a-compatibility-shim-makes-migration-permanent.md) [en](en/094-a-compatibility-shim-makes-migration-permanent.md) |  |
| 095 | Умолчание выбирается в пользу пользователя, а не продукта | The default is chosen in the user's favour, not the product's | [ru](ru/095-the-default-is-chosen-for-the-user.md) [en](en/095-the-default-is-chosen-for-the-user.md) |  |
| 096 | Хранилище выбирается по жизненному циклу данных, а не по удобству | Storage is chosen by the data's lifecycle, not by convenience | [ru](ru/096-storage-follows-lifecycle-not-convenience.md) [en](en/096-storage-follows-lifecycle-not-convenience.md) |  |
| 097 | У проверяющего инструмента две ошибки, и каждая держится своим тестом | A checking tool has two errors, and each is held by its own test | [ru](ru/097-a-checker-has-two-error-types.md) [en](en/097-a-checker-has-two-error-types.md) |  |
| 098 | Единица дробления определяется употреблением, а не формальным признаком | The unit of splitting follows usage, not a formal criterion | [ru](ru/098-the-unit-of-splitting-follows-usage.md) [en](en/098-the-unit-of-splitting-follows-usage.md) |  |
| 099 | Конфликт классификации разрешается по последствию, а не по правильности | A classification conflict is resolved by consequence, not by correctness | [ru](ru/099-classification-conflicts-resolve-by-consequence.md) [en](en/099-classification-conflicts-resolve-by-consequence.md) |  |
| 100 | Дедлайнов два: на запуск и на работу | There are two deadlines: one for starting, one for working | [ru](ru/100-two-deadlines-start-and-work.md) [en](en/100-two-deadlines-start-and-work.md) |  |
| 101 | Повторяют только те отказы, которые могут пройти сами | Retry only the failures that can pass on their own | [ru](ru/101-retry-only-what-can-heal-itself.md) [en](en/101-retry-only-what-can-heal-itself.md) |  |
| 102 | Снисхождение перечисляется таблицей и отключается режимом | Leniency is enumerated in a table and switched off by a mode | [ru](ru/102-leniency-is-enumerated-and-switchable.md) [en](en/102-leniency-is-enumerated-and-switchable.md) |  |
| 103 | Сторож побочных эффектов обвиняет не виновника — и исключения задаются формой | A side-effect guard blames the wrong suspect — and exclusions are defined by shape | [ru](ru/103-a-side-effect-guard-blames-the-wrong-suspect.md) [en](en/103-a-side-effect-guard-blames-the-wrong-suspect.md) |  |
| 104 | У событийной автоматики должна быть ручная кнопка | Event-driven automation needs a manual button | [ru](ru/104-event-driven-automation-needs-a-manual-button.md) [en](en/104-event-driven-automation-needs-a-manual-button.md) |  |
| 105 | Внешний аудит делает тот, кто не писал этот код | An outside audit is done by somebody who did not write this code | [ru](ru/105-an-outside-audit-needs-outside-eyes.md) [en](en/105-an-outside-audit-needs-outside-eyes.md) |  |
| 106 | Огласка умножает и хорошее, и плохое — сначала настоящий прогон | Publicity multiplies both the good and the bad — do the real run first | [ru](ru/106-publicity-multiplies-both-sides.md) [en](en/106-publicity-multiplies-both-sides.md) |  |
| 107 | «У автора работает» означает «проверено на выборке автора» | "It works for the author" means "tested on the author's sample" | [ru](ru/107-it-works-for-the-author-means-tested-on-the-authors-sample.md) [en](en/107-it-works-for-the-author-means-tested-on-the-authors-sample.md) |  |
| 108 | Живой документ держит фиксированное окно, остальное переезжает дословно | A living document keeps a fixed window; the rest moves out verbatim | [ru](ru/108-a-living-document-keeps-a-fixed-window.md) [en](en/108-a-living-document-keeps-a-fixed-window.md) |  |
| 109 | Каждый выход из переходного состояния обязан быть терминальным | Every exit from a transient state must be terminal | [ru](ru/109-every-exit-from-a-transient-state-must-be-terminal.md) [en](en/109-every-exit-from-a-transient-state-must-be-terminal.md) |  |
| 110 | Всё, что может отказать, делается до подмены глобального состояния | Everything that can fail happens before you replace global state | [ru](ru/110-fail-before-you-take-anything-over.md) [en](en/110-fail-before-you-take-anything-over.md) |  |
| 111 | Если инструмент может сделать сам — он делает, а не советует | If the tool can do it itself, it does it rather than advising | [ru](ru/111-do-it-instead-of-advising-it.md) [en](en/111-do-it-instead-of-advising-it.md) |  |
| 112 | Что инструмент создал — он обязан уметь удалить | Whatever the tool created, it must be able to delete | [ru](ru/112-whatever-the-tool-created-it-must-be-able-to-delete.md) [en](en/112-whatever-the-tool-created-it-must-be-able-to-delete.md) |  |
| 113 | Контракт описывает правила собственной эволюции | A contract states the rules of its own evolution | [ru](ru/113-a-contract-states-how-it-may-change.md) [en](en/113-a-contract-states-how-it-may-change.md) |  |
| 114 | Миграция идёт от текущей версии, а не от нуля | Migrate from the current version, not from zero | [ru](ru/114-migrate-from-the-current-version-not-from-zero.md) [en](en/114-migrate-from-the-current-version-not-from-zero.md) |  |
| 115 | У настроек один якорь и ограниченная зона поиска | Settings have one anchor and a bounded search area | [ru](ru/115-config-has-one-anchor-and-a-bounded-search.md) [en](en/115-config-has-one-anchor-and-a-bounded-search.md) |  |
| 116 | Сборщик результатов — тоже источник потерь, и у него своя сверка | The collector script is also a source of loss, and it has its own reconciliation | [ru](ru/116-the-collector-script-is-a-source-of-loss.md) [en](en/116-the-collector-script-is-a-source-of-loss.md) |  |
| 117 | У задания исполнителя есть числовые границы | An executor's brief carries numeric limits | [ru](ru/117-numeric-limits-belong-in-the-task-spec.md) [en](en/117-numeric-limits-belong-in-the-task-spec.md) |  |
| 118 | Исходник хранится рядом с производным | Keep the source next to the derived | [ru](ru/118-keep-the-source-next-to-the-derived.md) [en](en/118-keep-the-source-next-to-the-derived.md) |  |
| 119 | Свои артефакты держат вне маски входа | A tool's own artefacts stay outside its input mask | [ru](ru/119-tool-artefacts-stay-outside-the-input-mask.md) [en](en/119-tool-artefacts-stay-outside-the-input-mask.md) |  |
| 120 | Каталог правил ведётся по своим правилам, а указатель к нему генерируется | A rule catalogue runs by its own rules, and its index is generated | [ru](ru/120-how-to-run-a-rule-catalogue.md) [en](en/120-how-to-run-a-rule-catalogue.md) |  |
| 121 | Закрытие контейнера — не доказательство закрытия работы | Closing the container is not proof that the work is closed | [ru](ru/121-closing-the-container-is-not-closing-the-work.md) [en](en/121-closing-the-container-is-not-closing-the-work.md) |  |
| 122 | Рядом с отформатированным значением отдают сырое | Ship the raw value next to the formatted one | [ru](ru/122-ship-the-raw-value-next-to-the-formatted-one.md) [en](en/122-ship-the-raw-value-next-to-the-formatted-one.md) |  |
| 123 | Атрибуция проверяется в конечной истории, а не в коммите ветки | Attribution is verified against the final history, not against the branch commit | [ru](ru/123-attribution-is-verified-on-the-final-history.md) [en](en/123-attribution-is-verified-on-the-final-history.md) |  |
| 124 | Перезапускать минимум, но зелёное со второго раза — находка, а не починка | Re-run the minimum — but green on the second try is a finding, not a fix | [ru](ru/124-rerun-the-minimum-and-record-the-flake.md) [en](en/124-rerun-the-minimum-and-record-the-flake.md) |  |

---

## Как добавить своё

Правило рождается — запись в тот же день. Материал портится быстро: инциденты
месячной давности приходится восстанавливать по документам, потому что в памяти
их уже нет. Заготовка — [`templates/rule-template.md`](../templates/rule-template.md).

Обязательны две части, которые чаще всего пропускают:

- **Применимость** — где правило **не** работает. Без неё каталог скопируют
  целиком, включая заведомо чужое.
- **След** — ссылка на issue, PR или документ, где поломка видна. Без неё запись
  за месяц превращается в «кто-то говорил, что так лучше».

Запись делается **на обоих языках сразу**. Не потому что так аккуратнее, а
потому что иначе она не пройдёт сборку указателя.

## How to add your own

A rule is born — the record is written the same day. The material spoils fast:
incidents a month old have to be reconstructed from documents, because nobody
remembers them any more. Boilerplate:
[`templates/rule-template.md`](../templates/rule-template.md).

Two parts are mandatory and are the ones most often skipped:

- **Where it applies** — where the rule does **not** work. Without it the
  catalogue gets copied wholesale, including what plainly belongs to somebody
  else.
- **Trace** — a link to the issue, pull request or document where the failure is
  visible. Without it, within a month the record becomes "somebody said this was
  better".

The record is written **in both languages at once**. Not out of tidiness, but
because otherwise it will not pass the index build.
