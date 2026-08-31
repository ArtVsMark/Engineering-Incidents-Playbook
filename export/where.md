# Где действует правило · Where a rule applies

> **Этот файл собирается скриптом** `scripts/aggregate_bindings.py` из
> ответов потребителей и не правится руками. Пустая клетка означает, что
> потребитель не подключён, а не что правило им отклонено.

> **This file is generated** by `scripts/aggregate_bindings.py` from the
> consumers' answers and is never edited by hand. An empty cell means the
> consumer is not connected, not that the rule was rejected there.

## Потребители · Consumers

| Проект · Project | Состояние · State | Следов · Trails | Ответов · Answers | Без ответа · Unanswered | Лишних · Stale | Действует · Active | Гейтом · Gate | Конвейером · Pipeline | Документом · Document | Ничем · Nothing | Шагом · Step | Механизмов · Mechanisms | Почему · Why |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `claude-code-playbook` | подключён | 24 | 153 | 0 | 0 | 111 | 55 | 3 | 14 | 39 | 0 | 48 |  |
| `Stepik-Python-Grader` | подключён | 67 | 153 | 0 | 0 | 150 | 98 | 0 | 0 | 0 | 52 | 108 |  |
| `ArtVsMark` | подключён | 12 | 153 | 0 | 0 | 79 | 46 | 6 | 11 | 16 | 0 | 32 |  |
| `claude-code-usage` | не подключён | 1 | — | — | — | — | — | — | — | — | — | — | ответ потребителя ещё не заведён |
| `Glossary-Python` | не подключён | 0 | — | — | — | — | — | — | — | — | — | — | ответ потребителя ещё не заведён |

## Чем держат другие · How others enforce it

> Слева — тот, у кого механизм есть, и его адрес. Справа — у кого это правило признано действующим и не обеспечено ничем.
> Чужой механизм не обязан подойти: стеки разные. Раздел отвечает на один вопрос — кто уже сталкивался и чем закрыл.

> On the left, whoever holds the rule and where. On the right, whoever calls it active but holds it by nothing.

| № | Держит · Held by | Ничем · By nothing |
|---|---|---|
| 005 | `Stepik-Python-Grader` — гейт: scripts/check_docs_guardrails.py — числа тестов, покрытия и глоссария живут бейджами, а не текстом; CLAUDE.md § Метрики: «числом здесь не фиксируется»; `ArtVsMark` — гейт: scripts/build_metrics.py::patch_readme — числа только между маркерами m:ключ; scripts/build_metrics.py::render_featured — числа баннера тоже измерены, а не вписаны: они приходят из project_stats и попадают в подпись картинки той же сборкой; scripts/build_metrics.py::project_badges — версия, состояние CI, покрытие и версия пакета измеряются сборкой и рисуются ею же: чужих бейджей на витрине не осталось, а значит не осталось и второго источника тех же чисел; подпись «data as of» под плитками пишется сборкой, а не рукой: scripts/build_metrics.py::render_projects. Это день, когда числа последний раз ИЗМЕНИЛИСЬ, и .github/workflows/metrics.yml исключает саму подпись из сравнения — иначе прогон открывал бы изменение ежедневно, и «числа изменились» перестало бы что-либо значить | `claude-code-playbook` |
| 006 | `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Два окна: «Окно живёт 3–5 дней, дальше перезапуск — обязательно»; замер 764 против 81 прочитанного токена на токен выхода и шаблон эстафеты — docs/agent/environments.md | `claude-code-playbook`, `ArtVsMark` |
| 008 | `ArtVsMark` — гейт: scripts/check_page.py::audit_page — сворачиваемый блок на витрине отвергается дословным вхождением тега: он либо есть, либо нет, гадать не о чем. До 27 августа запрет держался абзацем в CLAUDE.md, хотя раздел под ним четыре обзора подряд назвали «обещанием без продолжения». README.md — блоков нет | `claude-code-playbook` |
| 009 | `claude-code-playbook` — гейт: scripts/check_charter.py и scripts/check_showcase.py считают через множество, а не по вхождениям: гейт, названный в конвейере дважды, считается одним; `Stepik-Python-Grader` — гейт: scripts/version.py считает PATCH по номерам PR и уникализирует их множеством (issue #1042), сверяет scripts/check_version_consistency.py | `ArtVsMark` |
| 012 | `Stepik-Python-Grader` — гейт: .claude/hooks/pre_tool_use.py — пуш в ветку, отличную от текущей, отвергается до вызова git; CI такое поймать не может, он видит артефакт, а не действие | `claude-code-playbook` |
| 014 | `Stepik-Python-Grader` — шаг процесса: CONTRIBUTING.md § Когда дефект считается исправленным: краснота доказывается полу-откатом — новые имена оставить, убрать только поведение; откат всего src/ даёт ImportError; `ArtVsMark` — гейт: HISTORY.md § Гейты, проверенные тем, что они обязаны отвергнуть — каждый гейт нарочно ломался обратно в свой исходный дефект при сохранённых именах, и самопроверка обязана была покраснеть. Меняется ровно одна переменная: поведение убрано, имена на месте. ПОДНЯТО ДО ГЕЙТА 28 августа: scripts/check_mechanisms.py::audit_voice требует отрицательный набор у КАЖДОГО скрипта, способного отвергнуть, а ::audit_harness — чтобы .github/workflows/pr-check.yml этот набор ЗВАЛ. Раньше здесь стояло «мутации прогоняются рукой при заведении гейта, в конвейере их нет» — и цена этого измерена в тот же день: scripts/checks.py получил самопроверку и в прогон вписан не был, что заметилось глазами. Мутация по-прежнему рукой: подменить поведение при сохранённых именах машина не умеет, и это остаток правила, а не всё оно | `claude-code-playbook` |
| 016 | `claude-code-playbook` — гейт: scripts/aggregate_bindings.py и scripts/collect_proposals.py печатают «и ещё N» вместо тихого урезания списка находок; `Stepik-Python-Grader` — гейт: scripts/check_truncation_marks.py — функция, режущая по пределу-константе, обязана оставить признак обрыва (флаг, многоточие, полную длину рядом); предел, заданный параметром, объявлен в контракте и молчанием не является | `ArtVsMark` |
| 021 | `Stepik-Python-Grader` — гейт: docs/ разложена по направлениям use/dev/agent/archive, полноту индексов и разбиение проверяет scripts/check_docs_guardrails.py; две документные роли разделены по аудитории — docs/agent/roles.md; `ArtVsMark` — гейт: CLAUDE.md § Язык артефактов делит по читателю: README.md посетителю профиля, .rules/README.md, .rules/roles.md, HISTORY.md и сам CLAUDE.md — владельцу и окну. Прежнее «делить нечего» считало три файла там, где их восемь; scripts/check_page.py::audit_service и ::audit_page — язык проверяется долей кириллицы, порог 50% и он не выдуман: замер 27 августа дал 6% у витрины и 70–94% у служебных файлов, то есть нарушение даёт значение у другого края, а не рядом с порогом. Отдельно проверяется наличие русского раздела: без него страница перестаёт быть двуязычной, а это обещание свода | `claude-code-playbook` |
| 025 | `Stepik-Python-Grader` — гейт: scripts/check_docs_guardrails.py — issue-tail policy: номер задачи допустим в журнале и запрещён в объясняющих документах; `ArtVsMark` — гейт: scripts/check_page.py::NUMBERED_TRACKER — ссылка на НОМЕРНУЮ задачу или изменение в тексте витрины отвергается: номер ничего не говорит постороннему читателю и устаревает вместе с задачей. Адрес трекера целиком законен и проверяется отдельным случаем набора — запрещён номер, а не адрес. README.md — номерных ссылок нет | `claude-code-playbook` |
| 028 | `Stepik-Python-Grader` — гейт: scripts/check_issue_checklists.py — комплексный issue от трёх находок ведёт чек-лист с исходом каждой | `claude-code-playbook` |
| 035 | `Stepik-Python-Grader` — гейт: версия динамическая из git-тегов (setuptools-scm), дрейф ловит scripts/check_version_consistency.py | `claude-code-playbook` |
| 038 | `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Два окна: имя окна начинается с окружения ([WEB]/[LOCAL]/[CLI]), метка ставится при открытии; канон — docs/agent/environments.md | `ArtVsMark` |
| 040 | `Stepik-Python-Grader` — гейт: scripts/skip_inventory.py | `claude-code-playbook` |
| 043 | `Stepik-Python-Grader` — гейт: scripts/check_adr_records.py | `claude-code-playbook` |
| 044 | `Stepik-Python-Grader` — шаг процесса: docs/agent/roles.md: оценка 🔍 Аудитора едет как заявка и проходит через ⚖️ Верификатора с установкой «опровергай по умолчанию» — по находке не работают, пока её премиса не проверена; `ArtVsMark` — гейт: scripts/check_bindings.py — премиса вердикта проверяется до того, как ему поверят: каждое «чем держится» и каждое «этого у нас нет» есть утверждение о текущем коде, и каждая ссылка в них сверяется с файлом и объявленным именем; отказ от чужих бейджей — та же премиса: утверждение, которое из окна не проверить, витрина на себя не берёт (прокси не пускает img.shields.io, и живой бейдж от опечатки в ссылке неотличим); scripts/build_metrics.py::verify_absence — премиса отказа по показателю проверяется до того, как её покажут: «релизов нет» у каталога правил оказалось неверным, релиз был помечен предварительным и не попадал в latest | `claude-code-playbook` |
| 047 | `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Гейты: смена правил транспорта требует перезапуска активных окон — настройки читаются при старте сессии; `ArtVsMark` — документ: CLAUDE.md § Окно — прямой цитатой: сменились правила работы, окна перезапускаются. Этот файл читается один раз, при старте | `claude-code-playbook` |
| 052 | `Stepik-Python-Grader` — гейт: scripts/move_merge_queue.py обновляет только голову очереди — из main остальные не двигаются (CLAUDE.md § Гейты: N против N(N−1)/2) | `claude-code-playbook` |
| 054 | `Stepik-Python-Grader` — шаг процесса: docs/agent/course-walkthrough.md: на шаге сбора ничего не анализируется — прогнать, записать сырое; разбор на границе главы | `claude-code-playbook` |
| 055 | `Stepik-Python-Grader` — шаг процесса: docs/agent/course-walkthrough.md § Внешний судья вердикта: свои ожидания в каталоге мутаций не доказывают ничего, сверка идёт со Stepik; каталог мутаций — docs/dev/corpus.md | `claude-code-playbook` |
| 062 | `Stepik-Python-Grader` — шаг процесса: docs/agent/roles.md § критерий приёмки новой роли: свой вопрос, свой артефакт, своё возражение конкретной роли — иначе это раздел документации; `ArtVsMark` — гейт: .rules/roles.md § Кто за что — у каждой роли свой вопрос, свой артефакт и своё возражение; профили заведены профилями именно потому, что своего возражения у них нет; scripts/check_roles.py держит это гейтом: у файла есть ведущий, а у строки — артефакт, и обе стороны проверяются перебором | `claude-code-playbook` |
| 077 | `Stepik-Python-Grader` — гейт: scripts/check_locale_guardrails.py | `claude-code-playbook` |
| 084 | `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Архитектурные инварианты, п. 3: rich опционален, весь вывод через _console с graceful fallback; AI-подсказка отказывает молча и не задерживает проверку | `claude-code-playbook` |
| 086 | `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Режим ответов (🔍 не ставит окончательную тяжесть — его оценка заявка; ⚖️ доказывает) и docs/agent/multiagent.md § адверсариальный верификатор со шкалой на примерах | `claude-code-playbook` |
| 088 | `Stepik-Python-Grader` — шаг процесса: docs/agent/roles.md § Роль 27 — Критик метода: вход — след фазы, вопрос о методе, а не о продукте | `claude-code-playbook` |
| 089 | `Stepik-Python-Grader` — гейт: scripts/check_showcase_links.py — данные карточек, локали и разметка веб-слоя не содержат ссылки на внешнюю витрину; объяснения в комментариях и docstring разрешены; `ArtVsMark` — документ: README.md — ссылки ведут только в источники, обратных из проектов сюда нет | `claude-code-playbook` |
| 093 | `Stepik-Python-Grader` — шаг процесса: ADR-0006: протокол Runner введён швом до server mode — минимальная обратимая точка расширения вместо обобщения по первому случаю | `claude-code-playbook` |
| 098 | `Stepik-Python-Grader` — шаг процесса: docs/dev/glossary.md § Одна концепция — одна карточка: парные протоколы намеренно остаются бандлами, а поиск чинится keywords, а не разбиением | `claude-code-playbook` |
| 105 | `Stepik-Python-Grader` — гейт: .github/workflows/claude-code-review.yml — ревью ведёт отдельный прогон, не то окно, что писало код; claude-review в списке обязательных проверок защиты main | `claude-code-playbook`, `ArtVsMark` |
| 106 | `Stepik-Python-Grader` — шаг процесса: HISTORY.md: решение владельца — не показывать широко, пока не пройден настоящий курс и вердикты не сошлись с платформой; протокол прогона — docs/agent/course-walkthrough.md | `claude-code-playbook` |
| 111 | `claude-code-playbook` — гейт: конвейер делает сам, а не советует: .github/workflows/agent-pr.yml открывает изменение, .github/workflows/automerge.yml включает слияние, .github/workflows/labels-sync.yml расставляет метки; `Stepik-Python-Grader` — шаг процесса: CLAUDE.md § Гейты: может сделать сам — делает, а не советует; прецедент — gh_rest.py edit-pr вместо совета проставить Closes руками | `ArtVsMark` |
| 118 | `claude-code-playbook` — гейт: scripts/build_rules_index.py — экспорт рядом с источником; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — файл с шапкой «СГЕНЕРИРОВАНО» называет генератор, и тот существует | `ArtVsMark` |
| 119 | `claude-code-playbook` — гейт: scripts/check_candidates.py исключает README.md из отбора кандидатов, scripts/check_links.py — свои производные; инструмент не обрабатывает собственный вывод; `Stepik-Python-Grader` — гейт: src/stepik_grader/core/test_loader.py — маска входа принимает только task*.py, поэтому свои артефакты (.grader_cache/, .grader_stats.jsonl, StepikTasks/) под неё не попадают; закреплено tests/test_test_loader.py | `ArtVsMark` |
| 120 | `Stepik-Python-Grader` — гейт: указатель правил и дайджест генерируются (scripts/generate_rules_index.py, scripts/generate_rules_digest.py), а scripts/check_rules_digest.py не даёт им разойтись с ответом проекта | `claude-code-playbook` |
| 121 | `Stepik-Python-Grader` — гейт: scripts/check_container_closure.py — ночной обход сверяет состояние эпика со счётчиком незакрытых дочерних задач: закрытый контейнер с открытой работой становится находкой с адресатом | `claude-code-playbook` |
| 124 | `Stepik-Python-Grader` — гейт: scripts/rerun_flaky_checks.py: список разрешённых к автоперезапуску закрыт, попытка ровно одна, а зелёное со второго раза записывается находкой в docs/agent/flaky-runs.md | `claude-code-playbook` |
| 125 | `claude-code-playbook` — гейт: scripts/build_rules_index.py — область и даты из источников; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — у производного файла назван живой исходник; DIGEST.md и указатель правил пересобираются генератором, а не правятся | `ArtVsMark` |
| 127 | `Stepik-Python-Grader` — гейт: scripts/check_docs_guardrails.py — число в прозе живёт только внутри генерируемого блока с маркером; вписанное руками отклоняется; `ArtVsMark` — гейт: scripts/build_metrics.py::patch_readme — маркер, сборка и падение при пропаже маркера | `claude-code-playbook` |
| 130 | `Stepik-Python-Grader` — гейт: scripts/link_rules_to_issues.py — новое правило приходит вместе со списком кандидатов из нашего трекера | `claude-code-playbook` |
| 132 | `Stepik-Python-Grader` — гейт: scripts/check_work_overlap.py показывает, кто ещё трогает те же файлы, а check_pr_ready.py требует объявить все задачи сборного изменения (Closes #N либо «Часть #N»); `ArtVsMark` — документ: CLAUDE.md § Критические запреты — не везти в одном PR несколько тем; .github/pull_request_template.md — тот же вопрос критику. Гейта нет намеренно: число затронутых зон сборности не доказывает, а ложный отказ на широкой теме дороже пропуска. Правило само требует предупреждения, а не отказа, — а предупреждать здесь некому | `claude-code-playbook` |
| 133 | `Stepik-Python-Grader` — гейт: граница PR проверяется пересечением файлов: scripts/check_work_overlap.py считает его по git diff --name-only, а не по числу задач; `ArtVsMark` — документ: CLAUDE.md § Критические запреты — оговорка к запрету на несколько тем: пересечение файлов сильнее темы. У витрины общие файлы почти у каждой правки — HISTORY.md и .rules/bindings.json, — поэтому изменения идут по одному, и встречи на общем файле не случается | `claude-code-playbook` |
| 135 | `Stepik-Python-Grader` — гейт: scripts/check_pr_ready.py отказывает мержить PR, открытый ботом (squash записал бы его автором в main), а scripts/check_attribution.py --check-branch сверяет подпись коммитов ветки до слияния — обе проверки узнают личность окна записью, а не опросом; `ArtVsMark` — гейт: .rules/README.md § Из окна не пишут — личность этого окна установлена пробой того же класса, а не опросом токена, и результат годен только для него: следующее окно проверяет заново. scripts/check_author.py — то, что окно подписалось не тем именем, теперь выясняется записью и проверкой, а не памятью | `claude-code-playbook` |
| 136 | `claude-code-playbook` — документ: .rules/bindings.json — вердикт о себе пишется после перебора предметов, и перебор называется в причине; гейта на полноту перебора нет; `Stepik-Python-Grader` — шаг процесса: ответ по внешнему правилу пишется в .rules/bindings.json одним заходом: сначала перечисляются все свои предметы правила, потом вердикт; сверяется на ревью PR — гейта на полноту перечисления нет | `ArtVsMark` |
| 138 | `Stepik-Python-Grader` — шаг процесса: docs/agent/environments.md — решение оседает задачей или комментарием сразу, эстафета передаётся ссылками; шаблон стартового сообщения окна там же; `ArtVsMark` — гейт: CLAUDE.md § Журнал изменений — журнал пополняется тем же заходом, что и правка, а не перед выпуском; решение оседает записью в HISTORY.md сразу; scripts/check_journal.py держит это гейтом: изменение, правящее scripts/ или .github/workflows/, обязано нести строку в HISTORY.md. Замер, из-за которого гейт завёлся, а не опасение: по 71 первопредку общей ветки 30 изменений правили поведение, и 3 приехали без записи — одно из них настоящее решение на 48 строк в прогоне очереди правил (#53), где отложенная запись означает, что следующее окно разбирает тот же вопрос заново. У отказа есть НАЗВАННЫЙ выход: строка «Журнал: не требуется — причина» в сообщении коммита снимает требование и остаётся в истории. Без выхода гейт обходили бы пустой записью, а пустая запись хуже отсутствующей — она выглядит как память. Содержание записи гейт не судит: отличить решение от опечатки машина не может, и обе стороны границы названы | `claude-code-playbook` |
| 139 | `Stepik-Python-Grader` — шаг процесса: CONTRIBUTING.md § Когда дефект считается исправленным и чек-лист CLAUDE.md: дефект закрыт прогоном той поверхности, где найден, — браузер браузером, CLI командой; `ArtVsMark` — документ: .rules/README.md § Конвейер — каждое звено названо вместе с изменением, на котором оно отработало: механизм считается подтверждённым прогоном, а не чтением | `claude-code-playbook` |
| 141 | `claude-code-playbook` — гейт: scripts/check_gates.py — набор «сборка указателя»: маркер и его расширение прогоняются как отдельный случай; `Stepik-Python-Grader` — гейт: scripts/check_marker_matching.py — константа-маркер не подставляется в startswith/removeprefix; префикс от маркера отличается именем, и это названо в самих константах | `ArtVsMark` |
| 144 | `Stepik-Python-Grader` — гейт: scripts/check_audit_registry.py — mention_verdict берёт окно контекста абзацем, а заголовок раздела перевешивает форму строки; закреплено тестами test_check_audit_registry.py | `claude-code-playbook`, `ArtVsMark` |
| 146 | `claude-code-playbook` — гейт: scripts/aggregate_bindings.py — обязательная проверка сверяет сводку с ОТВЕТОМ на диске, а не только саму с собой; до #122 она подтверждала своё основание тем же зелёным, каким подтверждала себя. Остальное правило держится разбором при приёмке: замер живого предмета машинно не отличить от рассуждения; `Stepik-Python-Grader` — шаг процесса: docs/agent/preflight.md § Что гейты не ловят: зелёный гейт подтверждает себя, утверждение проверяется замером на живом предмете, замер пишется рядом с механизмом | `ArtVsMark` |
| 147 | `Stepik-Python-Grader` — гейт: scripts/check_orphan_branches.py | `claude-code-playbook`, `ArtVsMark` |
| 148 | `claude-code-playbook` — конвейер: .github/workflows/automerge.yml ждёт появления коммита в общей ветке, а не поля merged записи изменения; разбор отказа начинается со сверки метки времени записи с проверками на голове; `Stepik-Python-Grader` — гейт: scripts/check_pr_ready.py читает проверки по sha головы PR, а не по полю записи, и отдельно смотрит прогон main: пустой список проверок трактуется как «CI не стартовал», а не «зелено» | `ArtVsMark` |
| 152 | `Stepik-Python-Grader` — гейт: scripts/check_workflow_guardrails.py; `ArtVsMark` — документ: правило родилось ЗДЕСЬ и уехало в каталог обратным каналом — .rules/proposals.json, слаг pinning-callee-without-caller. Инцидент: .github/workflows/automerge.yml брал scripts/gh_outcome.py с общей ветки ради того, чтобы не выполнять при личном токене владельца код из изменения. Защита нулевая — на событии pull_request площадка берёт из изменения САМ ФАЙЛ ПРОГОНА, и переписать шаг целиком дешевле, чем править вызываемое. Плюс цена: на изменении, которое скрипт вводит, на main его ещё нет, и шаг упал с кодом 2 на несуществующем файле. Закрепление снято, причина записана комментарием у шага, чтобы следующее окно не вернуло «безопасность» обратно. ГРАНИЦА: на pull_request_target и workflow_run рассуждение переворачивается — там файл прогона берётся с общей ветки, и закреплять вызываемое обязательно; ОБРАТНАЯ СТОРОНА ТОГО ЖЕ, замерена 28 августа: правка вызываемого (scripts/checks.py вынесен выше гейтов) оборвала точечную выборку у .github/workflows/release-hold.yml. Закреплять callee не надо было — надо было посмотреть на caller, и теперь за этим следит scripts/check_mechanisms.py::audit_sparse | `claude-code-playbook` |
| 153 | `claude-code-playbook` — документ: export/README.md § контракт — чужие решения описаны ссылкой на репозиторий потребителя, а не пересказом их устройства; .rules/consumers.json — про потребителя хранится адрес и роль, но не объяснение, почему у него так. Держится чтением при приёмке: отличить ссылку от пересказа машинно нечем; `Stepik-Python-Grader` — гейт: docs/agent/rules/DIGEST.md собирается из каталога генератором (scripts/generate_rules_digest.py), а не переписывается руками: чужой текст здесь производное с живым исходником, и расхождение ловит check_rules_digest.py | `ArtVsMark` |

## Сколько держит механизм · How much each mechanism holds

> Считается путь к файлу, найденный в поле `where` ответа потребителя. Механизм, держащий много правил, — это и образец, и точка отказа.

> Counted by the file path found in the consumer's `where` field. A mechanism holding many rules is both a model to copy and a single point of failure.

| Проект · Project | Механизм · Mechanism | Держит правил · Rules held |
|---|---|---|
| `claude-code-playbook` | `scripts/check_gates.py` | 9 |
| `claude-code-playbook` | `export/README.md` | 7 |
| `claude-code-playbook` | `.github/workflows/automerge.yml` | 6 |
| `claude-code-playbook` | `.github/workflows/agent-pr.yml` | 5 |
| `claude-code-playbook` | `.github/workflows/ci.yml` | 5 |
| `claude-code-playbook` | `scripts/aggregate_bindings.py` | 5 |
| `claude-code-playbook` | `scripts/build_rules_index.py` | 5 |
| `claude-code-playbook` | `scripts/check_charter.py` | 5 |
| `claude-code-playbook` | `scripts/check_bindings.py` | 4 |
| `claude-code-playbook` | `scripts/link_trails.py` | 4 |
| `claude-code-playbook` | `scripts/main_red.py` | 4 |
| `claude-code-playbook` | `scripts/refresh_derived.py` | 4 |
| `claude-code-playbook` | `.rules/consumers.json` | 3 |
| `claude-code-playbook` | `CONTRIBUTING.md` | 3 |
| `claude-code-playbook` | `scripts/collect_proposals.py` | 3 |
| `claude-code-playbook` | `.github/labels.yml` | 2 |
| `claude-code-playbook` | `.github/workflows/consumers-sync.yml` | 2 |
| `claude-code-playbook` | `.github/workflows/main-red.yml` | 2 |
| `claude-code-playbook` | `.rules/bindings.json` | 2 |
| `claude-code-playbook` | `HISTORY.md` | 2 |
| `claude-code-playbook` | `README.md` | 2 |
| `claude-code-playbook` | `export/rules.json` | 2 |
| `claude-code-playbook` | `scripts/audit_catalogue.py` | 2 |
| `claude-code-playbook` | `scripts/check_attribution.py` | 2 |
| `claude-code-playbook` | `scripts/check_showcase.py` | 2 |
| `claude-code-playbook` | `scripts/check_workflows.py` | 2 |
| `claude-code-playbook` | `scripts/collect_changelog.py` | 2 |
| `claude-code-playbook` | `scripts/ghcli.py` | 2 |
| `claude-code-playbook` | `scripts/sync_labels.py` | 2 |
| `claude-code-playbook` | `tests/test_ghcli.py` | 2 |
| `claude-code-playbook` | _остальные_ · _the rest_ | 18 механизмов по одному правилу; без названного адреса: 0 из 72 |
| `Stepik-Python-Grader` | `CLAUDE.md` | 28 |
| `Stepik-Python-Grader` | `docs/agent/multiagent.md` | 12 |
| `Stepik-Python-Grader` | `docs/agent/environments.md` | 7 |
| `Stepik-Python-Grader` | `scripts/gh_rest.py` | 7 |
| `Stepik-Python-Grader` | `docs/agent/roles.md` | 6 |
| `Stepik-Python-Grader` | `scripts/check_docs_guardrails.py` | 6 |
| `Stepik-Python-Grader` | `scripts/check_pr_ready.py` | 6 |
| `Stepik-Python-Grader` | `docs/agent/preflight.md` | 5 |
| `Stepik-Python-Grader` | `scripts/check_rule_bindings.py` | 5 |
| `Stepik-Python-Grader` | `.rules/bindings.json` | 3 |
| `Stepik-Python-Grader` | `CHANGELOG.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/claude-handoff.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/course-walkthrough.md` | 3 |
| `Stepik-Python-Grader` | `scripts/check_work_overlap.py` | 3 |
| `Stepik-Python-Grader` | `scripts/check_workflow_guardrails.py` | 3 |
| `Stepik-Python-Grader` | `scripts/rerun_flaky_checks.py` | 3 |
| `Stepik-Python-Grader` | `src/stepik_grader/web/playground.py` | 3 |
| `Stepik-Python-Grader` | `.claude/hooks/pre_tool_use.py` | 2 |
| `Stepik-Python-Grader` | `.github/workflows/ci.yml` | 2 |
| `Stepik-Python-Grader` | `CONTRIBUTING.md` | 2 |
| `Stepik-Python-Grader` | `HISTORY.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/corpus.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/glossary.md` | 2 |
| `Stepik-Python-Grader` | `scripts/check_adr_records.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_attribution.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_audit_registry.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_declared_outcomes.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_gate_tests.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_generated_sources.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_locale_guardrails.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_raw_values.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_rules_digest.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_version_consistency.py` | 2 |
| `Stepik-Python-Grader` | `scripts/generate_rules_digest.py` | 2 |
| `Stepik-Python-Grader` | `scripts/move_merge_queue.py` | 2 |
| `Stepik-Python-Grader` | `scripts/nightly_checks.py` | 2 |
| `Stepik-Python-Grader` | `src/stepik_grader/core/runner.py` | 2 |
| `Stepik-Python-Grader` | `src/stepik_grader/web/runs.py` | 2 |
| `Stepik-Python-Grader` | `tests/conftest.py` | 2 |
| `Stepik-Python-Grader` | `tests/test_runner.py` | 2 |
| `Stepik-Python-Grader` | `tests/test_runs.py` | 2 |
| `Stepik-Python-Grader` | _остальные_ · _the rest_ | 67 механизмов по одному правилу; без названного адреса: 5 из 150 |
| `ArtVsMark` | `scripts/build_metrics.py` | 22 |
| `ArtVsMark` | `scripts/check_mechanisms.py` | 17 |
| `ArtVsMark` | `CLAUDE.md` | 11 |
| `ArtVsMark` | `scripts/check_labels.py` | 11 |
| `ArtVsMark` | `.github/workflows/automerge.yml` | 10 |
| `ArtVsMark` | `README.md` | 10 |
| `ArtVsMark` | `scripts/check_roles.py` | 8 |
| `ArtVsMark` | `.github/workflows/open-pr.yml` | 7 |
| `ArtVsMark` | `scripts/check_page.py` | 7 |
| `ArtVsMark` | `.github/workflows/metrics.yml` | 6 |
| `ArtVsMark` | `.github/workflows/pr-check.yml` | 6 |
| `ArtVsMark` | `.rules/README.md` | 6 |
| `ArtVsMark` | `scripts/check_bindings.py` | 6 |
| `ArtVsMark` | `scripts/gh_outcome.py` | 6 |
| `ArtVsMark` | `.github/workflows/rules-inbox.yml` | 5 |
| `ArtVsMark` | `scripts/check_author.py` | 5 |
| `ArtVsMark` | `.github/workflows/main-red.yml` | 4 |
| `ArtVsMark` | `.github/workflows/release-hold.yml` | 4 |
| `ArtVsMark` | `HISTORY.md` | 4 |
| `ArtVsMark` | `scripts/checks.py` | 4 |
| `ArtVsMark` | `.rules/proposals.json` | 3 |
| `ArtVsMark` | `.rules/roles.md` | 3 |
| `ArtVsMark` | `.rules/bindings.json` | 2 |
| `ArtVsMark` | `projects.json` | 2 |
| `ArtVsMark` | _остальные_ · _the rest_ | 8 механизмов по одному правилу; без названного адреса: 1 из 63 |

## Правила · Rules

| № | `claude-code-playbook` | `Stepik-Python-Grader` | `ArtVsMark` |
|---|---|---|---|
| 001 | нет предмета | действует | действует |
| 002 | действует | действует | действует |
| 003 | действует | действует | нет предмета |
| 004 | действует | действует | нет предмета |
| 005 | действует | действует | действует |
| 006 | действует | действует | действует |
| 007 | нет предмета | действует | нет предмета |
| 008 | действует | нет предмета | действует |
| 009 | действует | действует | действует |
| 010 | действует | действует | действует |
| 011 | действует | действует | действует |
| 012 | действует | действует | нет предмета |
| 013 | действует | действует | нет предмета |
| 014 | действует | действует | действует |
| 015 | нет предмета | действует | нет предмета |
| 016 | действует | действует | действует |
| 017 | нет предмета | действует | нет предмета |
| 018 | действует | действует | нет предмета |
| 019 | нет предмета | действует | нет предмета |
| 020 | отклонено | действует | нет предмета |
| 021 | действует | действует | действует |
| 022 | действует | действует | действует |
| 023 | действует | действует | действует |
| 024 | действует | действует | отклонено |
| 025 | действует | действует | действует |
| 026 | действует | действует | нет предмета |
| 027 | действует | действует | действует |
| 028 | действует | действует | нет предмета |
| 029 | действует | действует | нет предмета |
| 030 | действует | действует | нет предмета |
| 031 | отклонено | действует | нет предмета |
| 032 | нет предмета | действует | действует |
| 033 | нет предмета | действует | нет предмета |
| 034 | отклонено | действует | нет предмета |
| 035 | действует | действует | нет предмета |
| 036 | нет предмета | действует | нет предмета |
| 037 | нет предмета | действует | нет предмета |
| 038 | нет предмета | действует | действует |
| 039 | действует | действует | действует |
| 040 | действует | действует | нет предмета |
| 041 | действует | действует | действует |
| 042 | действует | действует | нет предмета |
| 043 | действует | действует | нет предмета |
| 044 | действует | действует | действует |
| 045 | действует | действует | действует |
| 046 | действует | действует | действует |
| 047 | действует | действует | действует |
| 048 | нет предмета | нет предмета | нет предмета |
| 049 | действует | действует | действует |
| 050 | нет предмета | действует | действует |
| 051 | действует | действует | действует |
| 052 | действует | действует | нет предмета |
| 053 | действует | действует | нет предмета |
| 054 | действует | действует | нет предмета |
| 055 | действует | действует | нет предмета |
| 056 | действует | действует | действует |
| 057 | действует | действует | действует |
| 058 | нет предмета | действует | нет предмета |
| 059 | нет предмета | действует | нет предмета |
| 060 | отклонено | действует | нет предмета |
| 061 | отклонено | действует | нет предмета |
| 062 | действует | действует | действует |
| 063 | действует | действует | действует |
| 064 | действует | действует | действует |
| 065 | действует | действует | действует |
| 066 | нет предмета | действует | нет предмета |
| 067 | действует | действует | нет предмета |
| 068 | действует | действует | действует |
| 069 | нет предмета | действует | нет предмета |
| 070 | нет предмета | действует | нет предмета |
| 071 | действует | действует | нет предмета |
| 072 | действует | действует | нет предмета |
| 073 | нет предмета | действует | действует |
| 074 | действует | действует | действует |
| 075 | действует | действует | действует |
| 076 | нет предмета | действует | нет предмета |
| 077 | действует | действует | нет предмета |
| 078 | нет предмета | действует | нет предмета |
| 079 | действует | нет предмета | нет предмета |
| 080 | действует | действует | действует |
| 081 | нет предмета | действует | нет предмета |
| 082 | действует | действует | действует |
| 083 | нет предмета | действует | нет предмета |
| 084 | действует | действует | нет предмета |
| 085 | нет предмета | действует | нет предмета |
| 086 | действует | действует | нет предмета |
| 087 | нет предмета | действует | нет предмета |
| 088 | действует | действует | нет предмета |
| 089 | действует | действует | действует |
| 090 | действует | действует | действует |
| 091 | действует | действует | действует |
| 092 | нет предмета | действует | нет предмета |
| 093 | действует | действует | нет предмета |
| 094 | нет предмета | действует | нет предмета |
| 095 | нет предмета | действует | нет предмета |
| 096 | действует | действует | нет предмета |
| 097 | действует | действует | действует |
| 098 | действует | действует | нет предмета |
| 099 | действует | действует | нет предмета |
| 100 | действует | действует | действует |
| 101 | нет предмета | действует | нет предмета |
| 102 | нет предмета | действует | нет предмета |
| 103 | нет предмета | действует | нет предмета |
| 104 | действует | действует | действует |
| 105 | действует | действует | действует |
| 106 | действует | действует | нет предмета |
| 107 | действует | действует | действует |
| 108 | действует | действует | действует |
| 109 | действует | действует | нет предмета |
| 110 | нет предмета | действует | нет предмета |
| 111 | действует | действует | действует |
| 112 | нет предмета | действует | нет предмета |
| 113 | действует | действует | нет предмета |
| 114 | действует | действует | нет предмета |
| 115 | нет предмета | действует | нет предмета |
| 116 | отклонено | действует | нет предмета |
| 117 | отклонено | действует | нет предмета |
| 118 | действует | действует | действует |
| 119 | действует | действует | действует |
| 120 | действует | действует | нет предмета |
| 121 | действует | действует | нет предмета |
| 122 | действует | действует | нет предмета |
| 123 | действует | действует | действует |
| 124 | действует | действует | нет предмета |
| 125 | действует | действует | действует |
| 126 | действует | действует | действует |
| 127 | действует | действует | действует |
| 128 | действует | действует | действует |
| 129 | действует | действует | действует |
| 130 | действует | действует | нет предмета |
| 131 | действует | действует | действует |
| 132 | действует | действует | действует |
| 133 | действует | действует | действует |
| 134 | действует | действует | действует |
| 135 | действует | действует | действует |
| 136 | действует | действует | действует |
| 137 | нет предмета | действует | действует |
| 138 | действует | действует | действует |
| 139 | действует | действует | действует |
| 140 | действует | действует | действует |
| 141 | действует | действует | действует |
| 142 | действует | действует | действует |
| 144 | действует | действует | действует |
| 145 | действует | действует | действует |
| 146 | действует | действует | действует |
| 147 | действует | действует | действует |
| 148 | действует | действует | действует |
| 149 | нет предмета | действует | действует |
| 150 | действует | действует | действует |
| 151 | действует | действует | действует |
| 152 | действует | действует | действует |
| 153 | действует | действует | действует |
| 154 | действует | действует | действует |
