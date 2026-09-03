# Где действует правило · Where a rule applies

> **Этот файл собирается скриптом** `scripts/aggregate_bindings.py` из
> ответов потребителей и не правится руками. Пустая клетка означает, что
> потребитель не подключён, а не что правило им отклонено.

> **This file is generated** by `scripts/aggregate_bindings.py` from the
> consumers' answers and is never edited by hand. An empty cell means the
> consumer is not connected, not that the rule was rejected there.

## Потребители · Consumers

| Проект · Project | Состояние · State | Следов · Trails | Родил · Born | Ответов · Answers | Без ответа · Unanswered | Лишних · Stale | Действует · Active | Гейтом · Gate | Конвейером · Pipeline | Документом · Document | Ничем · Nothing | Шагом · Step | Механизмов · Mechanisms | Почему · Why |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `Engineering-Incidents-Playbook` | подключён | 34 | 26 | 175 | 0 | 0 | 133 | 92 | 6 | 24 | 11 | 0 | 83 |  |
| `Stepik-Python-Grader` | подключён | 69 | 129 | 163 | 12 | 0 | 160 | 66 | 31 | 63 | 0 | 0 | 128 |  |
| `ArtVsMark` | подключён | 16 | 10 | 165 | 10 | 0 | 89 | 52 | 11 | 12 | 13 | 0 | 34 |  |
| `Claude-Code_Usage-Token` | подключён | 9 | 10 | 162 | 13 | 0 | 43 | 30 | 0 | 7 | 1 | 5 | 27 |  |
| `Glossary-Python` | не подключён | 0 | 0 | — | — | — | — | — | — | — | — | — | — | ответ потребителя ещё не заведён |

## Чем держат другие · How others enforce it

> Слева — тот, у кого механизм есть, и его адрес. Справа — у кого это правило признано действующим и не обеспечено ничем.
> Чужой механизм не обязан подойти: стеки разные. Раздел отвечает на один вопрос — кто уже сталкивался и чем закрыл.

> On the left, whoever holds the rule and where. On the right, whoever calls it active but holds it by nothing.

| № | Держит · Held by | Ничем · By nothing |
|---|---|---|
| 006 | `Engineering-Incidents-Playbook` — документ: CLAUDE.md § Когда окно перезапускают — срок назван числом (три–пять дней) и к нему даны признаки, по которым не ждут календаря: окно перечитывает прочитанное, противоречит себе внутри смены, пересказ прошлого длиннее сегодняшней работы. ГРАНИЦА: возраст окна каталогу не виден — счётчика сессии площадка не даёт, и держится это чтением при старте, а не проверкой; `Stepik-Python-Grader` — документ: CLAUDE.md § Два окна: «Окно живёт 3–5 дней, дальше перезапуск — обязательно»; замер 764 против 81 прочитанного токена на токен выхода и шаблон эстафеты — docs/agent/environments.md; `Claude-Code_Usage-Token` — документ: CLAUDE.md § «Окно живёт 3–5 дней»; эстафета передаётся ссылками на issue, а не пересказом. | `ArtVsMark` |
| 009 | `Engineering-Incidents-Playbook` — гейт: scripts/check_charter.py и scripts/check_showcase.py считают через множество, а не по вхождениям: гейт, названный в конвейере дважды, считается одним; `Stepik-Python-Grader` — гейт: scripts/version.py считает PATCH по номерам PR и уникализирует их множеством (issue #1042), сверяет scripts/check_version_consistency.py; `Claude-Code_Usage-Token` — гейт: scripts/pr_ready.py — latest_by_name: check-runs считаются по уникальным именам, второй комплект после обновления ветки не удваивает счёт и не воскрешает вчерашнее красное. Плюс scripts/check_showcase (preflight): вопросы набора витрины считаются по уникальным id. Правило уже стоило проекту неверного вывода — CLAUDE.md, § «Как читать результат проверок»: «32 проверки» вместо шестнадцати продержались сутки. | `ArtVsMark` |
| 016 | `Engineering-Incidents-Playbook` — гейт: scripts/aggregate_bindings.py и scripts/collect_proposals.py печатают «и ещё N» вместо тихого урезания списка находок; `Stepik-Python-Grader` — гейт: scripts/check_truncation_marks.py — функция, режущая по пределу-константе, обязана оставить признак обрыва (флаг, многоточие, полную длину рядом); предел, заданный параметром, объявлен в контракте и молчанием не является; `Claude-Code_Usage-Token` — гейт: scripts/preflight.py печатает охват («просмотрено N, пропущено двоичных M»); src/claude_code_usage/transcripts.py — Coverage со строками, нечитаемыми и незнакомыми полями. Без этих чисел слепота источника неотличима от чистого результата. | `ArtVsMark` |
| 028 | `Stepik-Python-Grader` — конвейер: scripts/check_issue_checklists.py — комплексный issue от трёх находок ведёт чек-лист с исходом каждой | `Engineering-Incidents-Playbook` |
| 038 | `Stepik-Python-Grader` — документ: CLAUDE.md § Два окна: имя окна начинается с окружения ([WEB]/[LOCAL]/[CLI]), метка ставится при открытии; канон — docs/agent/environments.md | `ArtVsMark` |
| 052 | `Stepik-Python-Grader` — конвейер: scripts/move_merge_queue.py обновляет только голову очереди — из main остальные не двигаются (CLAUDE.md § Гейты: N против N(N−1)/2) | `Engineering-Incidents-Playbook` |
| 105 | `Stepik-Python-Grader` — конвейер: .github/workflows/claude-code-review.yml — ревью ведёт отдельный прогон, не то окно, что писало код; claude-review в списке обязательных проверок защиты main | `Engineering-Incidents-Playbook`, `ArtVsMark` |
| 118 | `Engineering-Incidents-Playbook` — гейт: scripts/build_rules_index.py — экспорт рядом с источником; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — файл с шапкой «СГЕНЕРИРОВАНО» называет генератор, и тот существует | `ArtVsMark` |
| 119 | `Engineering-Incidents-Playbook` — гейт: scripts/check_candidates.py исключает README.md из отбора кандидатов, scripts/check_links.py — свои производные; инструмент не обрабатывает собственный вывод; `Stepik-Python-Grader` — гейт: src/stepik_grader/core/test_loader.py — обход берёт только .py и не заходит в скрытые каталоги (_is_hidden_or_service_dir), поэтому .grader_cache/ и .grader_stats.jsonl под него не попадают; шаблон task*.py — приоритет с откатом (_solution_files_in возвращает by_pattern or files), а не жёсткий фильтр; закреплено tests/test_loader.py | `ArtVsMark` |
| 121 | `Stepik-Python-Grader` — конвейер: scripts/check_container_closure.py — ночной обход сверяет состояние эпика со счётчиком незакрытых дочерних задач: закрытый контейнер с открытой работой становится находкой с адресатом | `Engineering-Incidents-Playbook` |
| 125 | `Engineering-Incidents-Playbook` — гейт: scripts/build_rules_index.py — область и даты из источников; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — у производного файла назван живой исходник; DIGEST.md и указатель правил пересобираются генератором, а не правятся | `ArtVsMark` |
| 136 | `Engineering-Incidents-Playbook` — документ: .rules/bindings.json — вердикт о себе пишется после перебора предметов, и перебор называется в причине; гейта на полноту перебора нет; `Stepik-Python-Grader` — гейт: ответ по внешнему правилу пишется в .rules/bindings.json одним заходом: сначала перечисляются все свои предметы правила, потом вердикт; сверяется на ревью PR — гейта на полноту перечисления нет | `ArtVsMark` |
| 139 | `Stepik-Python-Grader` — документ: CONTRIBUTING.md § Когда дефект считается исправленным и чек-лист CLAUDE.md: дефект закрыт прогоном той поверхности, где найден, — браузер браузером, CLI командой; `ArtVsMark` — документ: .rules/README.md § Конвейер — каждое звено названо вместе с изменением, на котором оно отработало: механизм считается подтверждённым прогоном, а не чтением; `Claude-Code_Usage-Token` — шаг процесса: Оплачено четырьмя случаями за серию: mergeable_state «behind» без защиты ветки не появляется; в эталон попадал джоб самой очереди; очередь не просыпалась на последней позеленевшей проверке; отменённый прогон шёл впереди успешного. Ни один не был виден по зелёному набору тестов. | `Engineering-Incidents-Playbook` |
| 141 | `Engineering-Incidents-Playbook` — гейт: scripts/check_gates.py — набор «сборка указателя»: маркер и его расширение прогоняются как отдельный случай; `Stepik-Python-Grader` — гейт: scripts/check_marker_matching.py — константа-маркер не подставляется в startswith/removeprefix; префикс от маркера отличается именем, и это названо в самих константах; `Claude-Code_Usage-Token` — гейт: scripts/preflight.py — _НАБОР_ССЫЛКОЙ ищет ссылку, а не подстроку адреса; scripts/pr_check.py — _PR_EVENT не принимает pull_request_target за pull_request. Первое оплачено инцидентом: гейт остался зелёным, когда адрес ссылки подменили, а подпись оставили. | `ArtVsMark` |
| 144 | `Stepik-Python-Grader` — конвейер: scripts/check_audit_registry.py — mention_verdict берёт окно контекста абзацем, а заголовок раздела перевешивает форму строки; закреплено тестами test_check_audit_registry.py | `Engineering-Incidents-Playbook`, `ArtVsMark` |
| 146 | `Engineering-Incidents-Playbook` — гейт: scripts/aggregate_bindings.py — обязательная проверка сверяет сводку с ОТВЕТОМ на диске, а не только саму с собой; до #122 она подтверждала своё основание тем же зелёным, каким подтверждала себя. Остальное правило держится разбором при приёмке: замер живого предмета машинно не отличить от рассуждения; `Stepik-Python-Grader` — документ: docs/agent/preflight.md § Что гейты не ловят: зелёный гейт подтверждает себя, утверждение проверяется замером на живом предмете, замер пишется рядом с механизмом; `Claude-Code_Usage-Token` — шаг процесса: Мутационные прогоны: гейт признаётся работающим, только если краснеет на подделке. Две мутации за серию прошли зелёными и показали, что тестов не хватает — «пустая строка обрывает блок run» и «нечисловое значение складывается». | `ArtVsMark` |
| 153 | `Engineering-Incidents-Playbook` — документ: export/README.md § контракт — чужие решения описаны ссылкой на репозиторий потребителя, а не пересказом их устройства; .rules/consumers.json — про потребителя хранится адрес и роль, но не объяснение, почему у него так. Держится чтением при приёмке: отличить ссылку от пересказа машинно нечем; `Stepik-Python-Grader` — конвейер: docs/agent/rules/DIGEST.md собирается из каталога генератором (scripts/generate_rules_digest.py), а не переписывается руками: чужой текст здесь производное с живым исходником, и расхождение ловит check_rules_digest.py | `ArtVsMark` |
| 158 | `Stepik-Python-Grader` — документ: docs/agent/preflight.md § Что гейты не ловят: scripts/check_three_outcomes.py требует наличия третьего исхода, но не адреса отказа; признак «в сообщении есть адрес» от «есть любая подстановка» машинно не отличить; `ArtVsMark` — гейт: scripts/build_metrics.py::naming — адрес отказавшего источника прикрепляется в точке обращения, а не восстанавливается трассировкой; scripts/hold.py и scripts/check_labels.py печатают предмет отказа вместе с причиной. Правило родилось здесь: окно 31 августа дважды прогнало гейт и дважды искало, какой из двадцати источников ответил 403.; `Claude-Code_Usage-Token` — гейт: Третий исход называет предмет: scripts/shell_ascii.py печатает путь каталога, в котором не нашлось workflow; scripts/release.py — путь колеса; scripts/changelog.py — имя файла фрагмента; scripts/gh_rest.py — метод и путь запроса. | `Engineering-Incidents-Playbook` |

## Сколько держит механизм · How much each mechanism holds

> Считается путь к файлу, найденный в поле `where` ответа потребителя. Механизм, держащий много правил, — это и образец, и точка отказа.

> Counted by the file path found in the consumer's `where` field. A mechanism holding many rules is both a model to copy and a single point of failure.

| Проект · Project | Механизм · Mechanism | Держит правил · Rules held |
|---|---|---|
| `Engineering-Incidents-Playbook` | `scripts/build_rules_index.py` | 12 |
| `Engineering-Incidents-Playbook` | `.github/workflows/ci.yml` | 11 |
| `Engineering-Incidents-Playbook` | `scripts/check_gates.py` | 11 |
| `Engineering-Incidents-Playbook` | `scripts/aggregate_bindings.py` | 9 |
| `Engineering-Incidents-Playbook` | `.github/workflows/automerge.yml` | 8 |
| `Engineering-Incidents-Playbook` | `export/README.md` | 8 |
| `Engineering-Incidents-Playbook` | `.github/workflows/agent-pr.yml` | 7 |
| `Engineering-Incidents-Playbook` | `AGENTS.md` | 7 |
| `Engineering-Incidents-Playbook` | `scripts/check_bindings.py` | 7 |
| `Engineering-Incidents-Playbook` | `scripts/check_charter.py` | 7 |
| `Engineering-Incidents-Playbook` | `CONTRIBUTING.md` | 6 |
| `Engineering-Incidents-Playbook` | `scripts/check_prose.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/check_showcase.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/link_trails.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/audit_catalogue.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/check_attribution.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/check_workflows.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/collect_proposals.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/main_red.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/refresh_derived.py` | 4 |
| `Engineering-Incidents-Playbook` | `.github/labels.yml` | 3 |
| `Engineering-Incidents-Playbook` | `.rules/consumers.json` | 3 |
| `Engineering-Incidents-Playbook` | `CLAUDE.md` | 3 |
| `Engineering-Incidents-Playbook` | `HISTORY.md` | 3 |
| `Engineering-Incidents-Playbook` | `README.md` | 3 |
| `Engineering-Incidents-Playbook` | `export/rules.json` | 3 |
| `Engineering-Incidents-Playbook` | `scripts/collect_changelog.py` | 3 |
| `Engineering-Incidents-Playbook` | `scripts/history_metrics.py` | 3 |
| `Engineering-Incidents-Playbook` | `scripts/merge_ready.py` | 3 |
| `Engineering-Incidents-Playbook` | `scripts/version.py` | 3 |
| `Engineering-Incidents-Playbook` | `.github/workflows/attribution-history.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/consumers-sync.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/main-red.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.rules/bindings.json` | 2 |
| `Engineering-Incidents-Playbook` | `rules/README.md` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_links.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_own_name.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_subprocess.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/ghcli.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/pr_body.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/sync_inbox.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/sync_labels.py` | 2 |
| `Engineering-Incidents-Playbook` | `tests/test_ghcli.py` | 2 |
| `Engineering-Incidents-Playbook` | _остальные_ · _the rest_ | 40 механизмов по одному правилу; без названного адреса: 0 из 122 |
| `Stepik-Python-Grader` | `CLAUDE.md` | 38 |
| `Stepik-Python-Grader` | `docs/agent/multiagent.md` | 12 |
| `Stepik-Python-Grader` | `docs/agent/preflight.md` | 8 |
| `Stepik-Python-Grader` | `scripts/check_rule_bindings.py` | 8 |
| `Stepik-Python-Grader` | `docs/agent/environments.md` | 7 |
| `Stepik-Python-Grader` | `scripts/gh_rest.py` | 7 |
| `Stepik-Python-Grader` | `docs/agent/roles.md` | 6 |
| `Stepik-Python-Grader` | `scripts/check_docs_guardrails.py` | 6 |
| `Stepik-Python-Grader` | `scripts/check_pr_ready.py` | 6 |
| `Stepik-Python-Grader` | `scripts/preflight.py` | 6 |
| `Stepik-Python-Grader` | `.github/workflows/ci.yml` | 5 |
| `Stepik-Python-Grader` | `.rules/bindings.json` | 4 |
| `Stepik-Python-Grader` | `CHANGELOG.md` | 4 |
| `Stepik-Python-Grader` | `scripts/check_attribution.py` | 4 |
| `Stepik-Python-Grader` | `.github/workflows/tracker-guardrails.yml` | 3 |
| `Stepik-Python-Grader` | `.rules/proposals.json` | 3 |
| `Stepik-Python-Grader` | `HISTORY.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/claude-handoff.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/course-walkthrough.md` | 3 |
| `Stepik-Python-Grader` | `scripts/check_adr_records.py` | 3 |
| `Stepik-Python-Grader` | `scripts/check_work_overlap.py` | 3 |
| `Stepik-Python-Grader` | `scripts/check_workflow_guardrails.py` | 3 |
| `Stepik-Python-Grader` | `scripts/rerun_flaky_checks.py` | 3 |
| `Stepik-Python-Grader` | `src/stepik_grader/web/playground.py` | 3 |
| `Stepik-Python-Grader` | `.claude/hooks/pre_tool_use.py` | 2 |
| `Stepik-Python-Grader` | `CONTRIBUTING.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/corpus.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/glossary.md` | 2 |
| `Stepik-Python-Grader` | `scripts/check_audit_registry.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_declared_outcomes.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_gate_tests.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_generated_sources.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_locale_guardrails.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_raw_values.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_rules_digest.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_three_outcomes.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_version_consistency.py` | 2 |
| `Stepik-Python-Grader` | `scripts/generate_rules_digest.py` | 2 |
| `Stepik-Python-Grader` | `scripts/move_merge_queue.py` | 2 |
| `Stepik-Python-Grader` | `scripts/nightly_checks.py` | 2 |
| `Stepik-Python-Grader` | `src/stepik_grader/core/runner.py` | 2 |
| `Stepik-Python-Grader` | `src/stepik_grader/web/runs.py` | 2 |
| `Stepik-Python-Grader` | `templates/bindings.json` | 2 |
| `Stepik-Python-Grader` | `tests/conftest.py` | 2 |
| `Stepik-Python-Grader` | `tests/test_runner.py` | 2 |
| `Stepik-Python-Grader` | `tests/test_runs.py` | 2 |
| `Stepik-Python-Grader` | _остальные_ · _the rest_ | 82 механизмов по одному правилу; без названного адреса: 0 из 160 |
| `ArtVsMark` | `scripts/build_metrics.py` | 26 |
| `ArtVsMark` | `scripts/check_mechanisms.py` | 23 |
| `ArtVsMark` | `.github/workflows/automerge.yml` | 12 |
| `ArtVsMark` | `CLAUDE.md` | 12 |
| `ArtVsMark` | `scripts/check_labels.py` | 12 |
| `ArtVsMark` | `README.md` | 11 |
| `ArtVsMark` | `.github/workflows/open-pr.yml` | 10 |
| `ArtVsMark` | `.github/workflows/pr-check.yml` | 9 |
| `ArtVsMark` | `scripts/check_roles.py` | 9 |
| `ArtVsMark` | `.github/workflows/metrics.yml` | 8 |
| `ArtVsMark` | `scripts/check_page.py` | 7 |
| `ArtVsMark` | `.rules/README.md` | 6 |
| `ArtVsMark` | `scripts/check_author.py` | 6 |
| `ArtVsMark` | `scripts/check_bindings.py` | 6 |
| `ArtVsMark` | `scripts/checks.py` | 6 |
| `ArtVsMark` | `scripts/gh_outcome.py` | 6 |
| `ArtVsMark` | `.github/workflows/main-red.yml` | 5 |
| `ArtVsMark` | `.github/workflows/release-hold.yml` | 5 |
| `ArtVsMark` | `.github/workflows/rules-inbox.yml` | 5 |
| `ArtVsMark` | `HISTORY.md` | 5 |
| `ArtVsMark` | `scripts/hold.py` | 5 |
| `ArtVsMark` | `.rules/bindings.json` | 4 |
| `ArtVsMark` | `.rules/proposals.json` | 3 |
| `ArtVsMark` | `.rules/roles.md` | 3 |
| `ArtVsMark` | `scripts/check_journal.py` | 3 |
| `ArtVsMark` | `pr-check.yml` | 2 |
| `ArtVsMark` | `projects.json` | 2 |
| `ArtVsMark` | _остальные_ · _the rest_ | 7 механизмов по одному правилу; без названного адреса: 0 из 76 |
| `Claude-Code_Usage-Token` | `CLAUDE.md` | 7 |
| `Claude-Code_Usage-Token` | `scripts/changelog.py` | 7 |
| `Claude-Code_Usage-Token` | `scripts/pr_check.py` | 7 |
| `Claude-Code_Usage-Token` | `scripts/preflight.py` | 6 |
| `Claude-Code_Usage-Token` | `scripts/check_pr_metadata.py` | 4 |
| `Claude-Code_Usage-Token` | `scripts/merge_queue.py` | 3 |
| `Claude-Code_Usage-Token` | `scripts/pr_ready.py` | 3 |
| `Claude-Code_Usage-Token` | `scripts/release.py` | 3 |
| `Claude-Code_Usage-Token` | `scripts/shell_ascii.py` | 3 |
| `Claude-Code_Usage-Token` | `src/claude_code_usage/whitelist.py` | 3 |
| `Claude-Code_Usage-Token` | `.rules/proposals.json` | 2 |
| `Claude-Code_Usage-Token` | `.rules/showcase.json` | 2 |
| `Claude-Code_Usage-Token` | `docs/labels.md` | 2 |
| `Claude-Code_Usage-Token` | `docs/spec.md` | 2 |
| `Claude-Code_Usage-Token` | `scripts/gh_rest.py` | 2 |
| `Claude-Code_Usage-Token` | _остальные_ · _the rest_ | 12 механизмов по одному правилу; без названного адреса: 7 из 42 |

## Правила · Rules

| № | `Engineering-Incidents-Playbook` | `Stepik-Python-Grader` | `ArtVsMark` | `Claude-Code_Usage-Token` |
|---|---|---|---|---|
| 001 | нет предмета | действует | действует | действует |
| 002 | действует | действует | действует | действует |
| 003 | действует | действует | нет предмета | действует |
| 004 | действует | действует | нет предмета | действует |
| 005 | действует | действует | действует | действует |
| 006 | действует | действует | действует | действует |
| 007 | нет предмета | действует | нет предмета | не рассмотрено |
| 008 | действует | нет предмета | действует | не рассмотрено |
| 009 | действует | действует | действует | действует |
| 010 | действует | действует | действует | не рассмотрено |
| 011 | действует | действует | действует | действует |
| 012 | действует | действует | нет предмета | не рассмотрено |
| 013 | действует | действует | нет предмета | не рассмотрено |
| 014 | действует | действует | действует | не рассмотрено |
| 015 | нет предмета | действует | нет предмета | не рассмотрено |
| 016 | действует | действует | действует | действует |
| 017 | нет предмета | действует | нет предмета | действует |
| 018 | действует | действует | нет предмета | не рассмотрено |
| 019 | нет предмета | действует | нет предмета | не рассмотрено |
| 020 | отклонено | действует | нет предмета | не рассмотрено |
| 021 | действует | действует | действует | не рассмотрено |
| 022 | действует | действует | действует | действует |
| 023 | действует | действует | действует | не рассмотрено |
| 024 | действует | действует | отклонено | не рассмотрено |
| 025 | действует | действует | действует | не рассмотрено |
| 026 | действует | действует | нет предмета | не рассмотрено |
| 027 | действует | действует | действует | действует |
| 028 | действует | действует | нет предмета | не рассмотрено |
| 029 | действует | действует | нет предмета | не рассмотрено |
| 030 | действует | действует | нет предмета | действует |
| 031 | отклонено | действует | нет предмета | не рассмотрено |
| 032 | нет предмета | действует | действует | не рассмотрено |
| 033 | нет предмета | действует | нет предмета | не рассмотрено |
| 034 | отклонено | действует | нет предмета | не рассмотрено |
| 035 | действует | действует | нет предмета | отклонено |
| 036 | нет предмета | действует | нет предмета | не рассмотрено |
| 037 | нет предмета | действует | нет предмета | действует |
| 038 | нет предмета | действует | действует | не рассмотрено |
| 039 | действует | действует | действует | действует |
| 040 | действует | действует | нет предмета | не рассмотрено |
| 041 | действует | действует | действует | не рассмотрено |
| 042 | действует | действует | нет предмета | действует |
| 043 | действует | действует | нет предмета | не рассмотрено |
| 044 | действует | действует | действует | не рассмотрено |
| 045 | действует | действует | действует | действует |
| 046 | действует | действует | действует | действует |
| 047 | действует | действует | действует | не рассмотрено |
| 048 | нет предмета | нет предмета | нет предмета | действует |
| 049 | действует | действует | действует | действует |
| 050 | нет предмета | действует | действует | не рассмотрено |
| 051 | действует | действует | действует | действует |
| 052 | действует | действует | нет предмета | не рассмотрено |
| 053 | действует | действует | нет предмета | не рассмотрено |
| 054 | действует | действует | нет предмета | не рассмотрено |
| 055 | действует | действует | нет предмета | действует |
| 056 | действует | действует | действует | не рассмотрено |
| 057 | действует | действует | действует | не рассмотрено |
| 058 | нет предмета | действует | нет предмета | не рассмотрено |
| 059 | нет предмета | действует | нет предмета | не рассмотрено |
| 060 | отклонено | действует | нет предмета | не рассмотрено |
| 061 | отклонено | действует | нет предмета | не рассмотрено |
| 062 | действует | действует | действует | не рассмотрено |
| 063 | действует | действует | действует | не рассмотрено |
| 064 | действует | действует | действует | действует |
| 065 | действует | действует | действует | не рассмотрено |
| 066 | нет предмета | действует | нет предмета | не рассмотрено |
| 067 | действует | действует | нет предмета | не рассмотрено |
| 068 | действует | действует | действует | действует |
| 069 | нет предмета | действует | нет предмета | не рассмотрено |
| 070 | нет предмета | действует | нет предмета | не рассмотрено |
| 071 | действует | действует | нет предмета | не рассмотрено |
| 072 | действует | действует | нет предмета | не рассмотрено |
| 073 | нет предмета | действует | действует | не рассмотрено |
| 074 | действует | действует | действует | действует |
| 075 | действует | действует | действует | действует |
| 076 | нет предмета | действует | нет предмета | не рассмотрено |
| 077 | действует | действует | нет предмета | действует |
| 078 | нет предмета | действует | нет предмета | действует |
| 079 | действует | нет предмета | нет предмета | не рассмотрено |
| 080 | действует | действует | действует | действует |
| 081 | нет предмета | действует | нет предмета | не рассмотрено |
| 082 | действует | действует | действует | не рассмотрено |
| 083 | нет предмета | действует | нет предмета | не рассмотрено |
| 084 | действует | действует | нет предмета | не рассмотрено |
| 085 | нет предмета | действует | нет предмета | не рассмотрено |
| 086 | действует | действует | нет предмета | не рассмотрено |
| 087 | нет предмета | действует | нет предмета | не рассмотрено |
| 088 | действует | действует | нет предмета | не рассмотрено |
| 089 | действует | действует | действует | не рассмотрено |
| 090 | действует | действует | действует | не рассмотрено |
| 091 | действует | действует | действует | не рассмотрено |
| 092 | нет предмета | действует | нет предмета | не рассмотрено |
| 093 | действует | действует | нет предмета | не рассмотрено |
| 094 | нет предмета | действует | нет предмета | не рассмотрено |
| 095 | нет предмета | действует | нет предмета | не рассмотрено |
| 096 | действует | действует | нет предмета | действует |
| 097 | действует | действует | действует | действует |
| 098 | действует | действует | нет предмета | не рассмотрено |
| 099 | действует | действует | нет предмета | не рассмотрено |
| 100 | действует | действует | действует | не рассмотрено |
| 101 | нет предмета | действует | нет предмета | не рассмотрено |
| 102 | нет предмета | действует | нет предмета | не рассмотрено |
| 103 | нет предмета | действует | нет предмета | не рассмотрено |
| 104 | действует | действует | действует | действует |
| 105 | действует | действует | действует | не рассмотрено |
| 106 | действует | действует | нет предмета | не рассмотрено |
| 107 | действует | действует | действует | не рассмотрено |
| 108 | действует | действует | действует | не рассмотрено |
| 109 | действует | действует | нет предмета | не рассмотрено |
| 110 | нет предмета | действует | нет предмета | не рассмотрено |
| 111 | действует | действует | действует | не рассмотрено |
| 112 | нет предмета | действует | нет предмета | не рассмотрено |
| 113 | действует | действует | нет предмета | не рассмотрено |
| 114 | действует | действует | нет предмета | не рассмотрено |
| 115 | нет предмета | действует | нет предмета | не рассмотрено |
| 116 | отклонено | действует | нет предмета | не рассмотрено |
| 117 | отклонено | действует | нет предмета | не рассмотрено |
| 118 | действует | действует | действует | не рассмотрено |
| 119 | действует | действует | действует | не рассмотрено |
| 120 | действует | действует | нет предмета | не рассмотрено |
| 121 | действует | действует | нет предмета | не рассмотрено |
| 122 | действует | действует | нет предмета | не рассмотрено |
| 123 | действует | действует | действует | не рассмотрено |
| 124 | действует | действует | нет предмета | не рассмотрено |
| 125 | действует | действует | действует | не рассмотрено |
| 126 | действует | действует | действует | не рассмотрено |
| 127 | действует | действует | действует | не рассмотрено |
| 128 | действует | действует | действует | действует |
| 129 | действует | действует | действует | не рассмотрено |
| 130 | действует | действует | нет предмета | не рассмотрено |
| 131 | действует | действует | действует | нет предмета |
| 132 | действует | действует | действует | не рассмотрено |
| 133 | действует | действует | действует | не рассмотрено |
| 134 | действует | действует | действует | действует |
| 135 | действует | действует | действует | не рассмотрено |
| 136 | действует | действует | действует | не рассмотрено |
| 137 | нет предмета | действует | действует | не рассмотрено |
| 138 | действует | действует | действует | не рассмотрено |
| 139 | действует | действует | действует | действует |
| 140 | действует | действует | действует | действует |
| 141 | действует | действует | действует | действует |
| 142 | действует | действует | действует | не рассмотрено |
| 144 | действует | действует | действует | не рассмотрено |
| 145 | действует | действует | действует | действует |
| 146 | действует | действует | действует | действует |
| 147 | действует | действует | действует | не рассмотрено |
| 148 | действует | действует | действует | не рассмотрено |
| 149 | нет предмета | действует | действует | не рассмотрено |
| 150 | действует | действует | действует | действует |
| 151 | действует | действует | действует | не рассмотрено |
| 152 | действует | действует | действует | не рассмотрено |
| 153 | действует | действует | действует | не рассмотрено |
| 154 | действует | действует | действует | действует |
| 155 | действует | действует | нет предмета | нет предмета |
| 156 | действует | действует | действует | нет предмета |
| 157 | действует | действует | действует | не рассмотрено |
| 158 | действует | действует | действует | действует |
| 159 | действует | действует | действует | действует |
| 160 | действует | действует | действует | отклонено |
| 161 | действует | действует | действует | не рассмотрено |
| 162 | действует | действует | действует | не рассмотрено |
| 163 | действует | действует | нет предмета | нет предмета |
| 164 | действует | действует | действует | — |
| 165 | действует | — | действует | — |
| 166 | действует | — | действует | — |
| 167 | действует | — | — | — |
| 168 | действует | — | — | — |
| 169 | действует | — | — | — |
| 170 | действует | — | — | — |
| 171 | действует | — | — | — |
| 172 | действует | — | — | — |
| 173 | действует | — | — | — |
| 174 | действует | — | — | — |
| 175 | действует | — | — | — |
| 176 | действует | — | — | — |
