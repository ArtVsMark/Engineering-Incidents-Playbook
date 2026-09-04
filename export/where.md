# Где действует правило · Where a rule applies

> **Этот файл собирается скриптом** `scripts/aggregate_bindings.py` из
> ответов потребителей и не правится руками. Пустая клетка означает, что
> потребитель не подключён, а не что правило им отклонено.

> **This file is generated** by `scripts/aggregate_bindings.py` from the
> consumers' answers and is never edited by hand. An empty cell means the
> consumer is not connected, not that the rule was rejected there.

## Потребители · Consumers

| Проект · Project | Состояние · State | Следов · Trails | Родил · Born | Ответов · Answers | Без ответа · Unanswered | Лишних · Stale | Действует · Active | Гейтом · Gate | Конвейером · Pipeline | Документом · Document | Ничем · Nothing | Механизмов · Mechanisms | Почему · Why |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `Engineering-Incidents-Playbook` | подключён | 35 | 27 | 179 | 0 | 0 | 141 | 104 | 8 | 25 | 4 | 91 |  |
| `Stepik-Python-Grader` | подключён | 69 | 129 | 175 | 4 | 0 | 172 | 71 | 37 | 64 | 0 | 139 |  |
| `ArtVsMark` | подключён | 16 | 10 | 176 | 3 | 0 | 101 | 60 | 11 | 13 | 15 | 34 |  |
| `Claude-Code_Usage-Token` | подключён | 12 | 13 | 175 | 4 | 0 | 145 | 84 | 5 | 36 | 20 | 61 |  |
| `Glossary-Python` | не подключён | 0 | 0 | — | — | — | — | — | — | — | — | — | ответ потребителя ещё не заведён |

## Чем держат другие · How others enforce it

> Слева — тот, у кого механизм есть, и его адрес. Справа — у кого это правило признано действующим и не обеспечено ничем.
> Чужой механизм не обязан подойти: стеки разные. Раздел отвечает на один вопрос — кто уже сталкивался и чем закрыл.

> On the left, whoever holds the rule and where. On the right, whoever calls it active but holds it by nothing.

| № | Держит · Held by | Ничем · By nothing |
|---|---|---|
| 006 | `Engineering-Incidents-Playbook` — документ: CLAUDE.md § Когда окно перезапускают — срок назван числом (три–пять дней) и к нему даны признаки, по которым не ждут календаря: окно перечитывает прочитанное, противоречит себе внутри смены, пересказ прошлого длиннее сегодняшней работы. ГРАНИЦА: возраст окна каталогу не виден — счётчика сессии площадка не даёт, и держится это чтением при старте, а не проверкой; `Stepik-Python-Grader` — документ: CLAUDE.md § Два окна: «Окно живёт 3–5 дней, дальше перезапуск — обязательно»; замер 764 против 81 прочитанного токена на токен выхода и шаблон эстафеты — docs/agent/environments.md; `Claude-Code_Usage-Token` — документ: CLAUDE.md § «Окно живёт 3–5 дней»; эстафета передаётся ссылками на issue, а не пересказом. | `ArtVsMark` |
| 009 | `Engineering-Incidents-Playbook` — гейт: scripts/check_charter.py и scripts/check_showcase.py считают через множество, а не по вхождениям: гейт, названный в конвейере дважды, считается одним; `Stepik-Python-Grader` — гейт: scripts/version.py считает PATCH по номерам PR и уникализирует их множеством (issue #1042), сверяет scripts/check_version_consistency.py; `Claude-Code_Usage-Token` — гейт: scripts/pr_ready.py — latest_by_name: check-runs считаются по уникальным именам, второй комплект после обновления ветки не удваивает счёт и не воскрешает вчерашнее красное. Плюс scripts/check_showcase (preflight): вопросы набора витрины считаются по уникальным id. Правило уже стоило проекту неверного вывода — CLAUDE.md, § «Как читать результат проверок»: «32 проверки» вместо шестнадцати продержались сутки. | `ArtVsMark` |
| 012 | `Engineering-Incidents-Playbook` — гейт: .claude/hooks/push_guard.py — хук PreToolUse, объявленный в .claude/settings.json: толчок в ветку, отличную от текущей головы, отвергается ДО вызова git. Конвейер такого не ловит — он видит артефакт, а не действие, и к его запуску ветка уже сдвинута. Приём взят у грейдера — у него это тоже хук перед вызовом инструмента, — а файл нет: его запрет шире и собран под его конвейер. Разрешены толчок без имени ветки, толчок текущей и явная ссылка HEAD:<ветка>. Набор — tests/test_push_guard.py; живая проба состоялась при постройке: хук отверг толчок в несуществующую ветку и на ней же нашлась своя поломка — `2>&1` считалось именем ветки. ГРАНИЦА: ЧЬЯ ветка, сторож по-прежнему не знает — он знает только, что она не та, на которой стоит окно; `Stepik-Python-Grader` — гейт: .claude/hooks/pre_tool_use.py — пуш в ветку, отличную от текущей, отвергается до вызова git; CI такое поймать не может, он видит артефакт, а не действие | `Claude-Code_Usage-Token` |
| 013 | `Engineering-Incidents-Playbook` — конвейер: .github/workflows/agent-pr.yml передаёт заголовок и тело файлами (`--body-file`), а не строкой в оболочке; то же в .github/workflows/automerge.yml; `Stepik-Python-Grader` — гейт: .claude/hooks/pre_tool_use.py — heredoc без кавычек в делимитере с экранированием в теле отвергается до записи файла | `Claude-Code_Usage-Token` |
| 016 | `Engineering-Incidents-Playbook` — гейт: scripts/aggregate_bindings.py и scripts/collect_proposals.py печатают «и ещё N» вместо тихого урезания списка находок; `Stepik-Python-Grader` — гейт: scripts/check_truncation_marks.py — функция, режущая по пределу-константе, обязана оставить признак обрыва (флаг, многоточие, полную длину рядом); предел, заданный параметром, объявлен в контракте и молчанием не является; `Claude-Code_Usage-Token` — гейт: scripts/preflight.py печатает охват («просмотрено N, пропущено двоичных M»); src/claude_code_usage/transcripts.py — Coverage со строками, повторами ответа и незнакомыми полями; scripts/subprocess_encoding.py и scripts/utf8_output.py — «разобрано файлов N, пропущено M» и «проверено N, не предмет M»; scripts/rules_answer.py — «записей N, с адресом M». | `ArtVsMark` |
| 028 | `Stepik-Python-Grader` — конвейер: scripts/check_issue_checklists.py — комплексный issue от трёх находок ведёт чек-лист с исходом каждой; `Claude-Code_Usage-Token` — документ: .github/pull_request_template.md — восемь пунктов галочками, а не прозой; CLAUDE.md § «Перед PR» — тот же чек-лист, исполняемый одной командой scripts/preflight.py. Состояние задачи не вычисляется чтением: у каждого пункта либо галочка, либо её нет. | `Engineering-Incidents-Playbook` |
| 033 | `Engineering-Incidents-Playbook` — гейт: scripts/check_schedules.py + .rules/schedules.json — цена прогона объявляется числом, а гейт СЧИТАЕТ: сколько вызовов наружу расписания просят в худший час и укладывается ли сумма по всем расписаниям этого часа в объявленную долю часового лимита; `Stepik-Python-Grader` — документ: docs/agent/multiagent.md § арифметика интервала между стартами; CLAUDE.md § Гейты — порог остатка квоты и интервал опроса статусов | `Claude-Code_Usage-Token` |
| 038 | `Stepik-Python-Grader` — документ: CLAUDE.md § Два окна: имя окна начинается с окружения ([WEB]/[LOCAL]/[CLI]), метка ставится при открытии; канон — docs/agent/environments.md | `ArtVsMark`, `Claude-Code_Usage-Token` |
| 047 | `Engineering-Incidents-Playbook` — документ: CLAUDE.md § Когда окно перезапускают — сменились правила работы, окна перезапускают, а не рассылают им письма: свод и ядро читаются ОДИН раз, при старте, и правка живому окну не видна вовсе. ГРАНИЦА: реестра живых окон нет и не будет — рассылка потребовала бы знать, кто сейчас открыт; `Stepik-Python-Grader` — документ: CLAUDE.md § Гейты: смена правил транспорта требует перезапуска активных окон — настройки читаются при старте сессии; `ArtVsMark` — документ: CLAUDE.md § Окно — прямой цитатой: сменились правила работы, окна перезапускаются. Этот файл читается один раз, при старте | `Claude-Code_Usage-Token` |
| 059 | `Stepik-Python-Grader` — документ: docs/agent/preflight.md § Маршрут при исчерпании лимитов: что недоступно, что работает и чем занять время до сброса квоты | `Claude-Code_Usage-Token` |
| 065 | `Engineering-Incidents-Playbook` — документ: CONTRIBUTING.md, раздел «Путь новичка»: обе метки входа объявлены в .github/labels.yml, тело задачи ведётся на двух языках, и правило действует в момент навешивания метки. Двуязычие тела не проверяется ничем — метку вешает человек; `Stepik-Python-Grader` — конвейер: scripts/check_good_first_issues_bilingual.py — good first issue и help wanted ведутся на двух языках, и меток именно две: путь участника не кончается первым вкладом; `ArtVsMark` — документ: README.md § Contributions welcome — витрина двуязычна, и задачи по ссылке ведутся на двух языках | `Claude-Code_Usage-Token` |
| 086 | `Engineering-Incidents-Playbook` — гейт: scripts/collect_proposals.py::check_verdicts — оценку находке ставит НЕ нашедший: проект присылает предложение БЕЗ номера (форма запрещает поле прямо), а вердикт выносит принимающая сторона, и гейт требует у каждого предложения статус из закрытого набора, у принятого — существующий номер правила, у отклонённого — причину. Номер не переиспользуется: два предложения под одним отвергаются. ГРАНИЦА, И ОНА ПОЛОВИНА ПРАВИЛА: вторая половина — «шкала опровергателя калибруется примерами» — не держится ничем, и предмета для неё пока нет: вердиктов семь, все «принято», ни одного отказа. Гейт на калибровку отказа мерил бы пустоту (075), и заводить его стоит с первым же отклонённым предложением. У соседа калибровка держится документом — шкалой на примерах в своде (162); `Stepik-Python-Grader` — документ: CLAUDE.md § Режим ответов (🔍 не ставит окончательную тяжесть — его оценка заявка; ⚖️ доказывает) и docs/agent/multiagent.md § адверсариальный верификатор со шкалой на примерах | `Claude-Code_Usage-Token` |
| 088 | `Engineering-Incidents-Playbook` — документ: AGENTS.md § Границы прохода — на границе фазы спрашивают о МЕТОДЕ, а не о продукте, и обе границы каталога названы с их вопросами: «построил гейт → приёмка» (отвергает ли он предмет правила, а не свою границу; прогонялся ли объявленный третий исход; не подтверждает ли он сам себя) и «закрыл тир очереди → замер» (сколько закрыто работой, а сколько переклассификацией). Там же сказано, что вопрос задаёт не тот, кто делал фазу, и что у окна это означает отдельный заход после отчёта, а не абзац в конце того же. Роль «критик метода» стоит в карте направлений со своим возражением, и полноту карты держит гейт ролей. У соседа это тоже документ — роль отдельным разделом (162). ГРАНИЦА: что вопрос был ЗАДАН, машинно не видно; карта держит существование роли, а не её работу; `Stepik-Python-Grader` — документ: docs/agent/roles.md § Роль 27 — Критик метода: вход — след фазы, вопрос о методе, а не о продукте | `Claude-Code_Usage-Token` |
| 091 | `Engineering-Incidents-Playbook` — гейт: свод перечисляет источники работы по порядку, нулевым — красное на общей ветке; статусы живут только в трекере, и .github/workflows/main-red.yml заводит задачу туда же; `Stepik-Python-Grader` — документ: CLAUDE.md § Открытая работа: порядок обращения сверху вниз — issue, docs/audit/, docs/agent/claude-handoff.md, CHANGELOG.md; первый непустой источник и есть план; `ArtVsMark` — документ: CLAUDE.md § Открытая работа — три источника по порядку, первый непустой и есть план; пустой трекер объявлен нормальным состоянием, иначе порядок ломается на первом шаге | `Claude-Code_Usage-Token` |
| 092 | `Stepik-Python-Grader` — документ: CLAUDE.md § Открытая работа: аудит даёт находки (docs/audit/), очередь задаёт порядок (docs/agent/claude-handoff.md) — два документа, смешивать нельзя | `Claude-Code_Usage-Token` |
| 105 | `Stepik-Python-Grader` — конвейер: .github/workflows/claude-code-review.yml — ревью ведёт отдельный прогон, не то окно, что писало код; claude-review в списке обязательных проверок защиты main | `Engineering-Incidents-Playbook`, `ArtVsMark`, `Claude-Code_Usage-Token` |
| 108 | `Engineering-Incidents-Playbook` — гейт: scripts/audit_catalogue.py — у растущей части HISTORY.md есть предел, выраженный числом, и вышедшее за окно гейт называет поимённо, старшими вперёд. Дословность переноса в архив машинно не проверяется, и это сказано в самом скрипте; `Stepik-Python-Grader` — гейт: scripts/check_docs_guardrails.py не даёт CHANGELOG.md держать больше трёх версионных заголовков: старое переезжает дословно в docs/archive/changelog-archive.md; `ArtVsMark` — гейт: scripts/build_metrics.py::check_focus_limit — потолок «Current focus» в пять строк | `Claude-Code_Usage-Token` |
| 118 | `Engineering-Incidents-Playbook` — гейт: scripts/build_rules_index.py — экспорт рядом с источником; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — файл с шапкой «СГЕНЕРИРОВАНО» называет генератор, и тот существует; `Claude-Code_Usage-Token` — гейт: src/claude_code_usage/whitelist.py и scripts/preflight.py — ровно тот случай, который правило выводит из-под общего требования: исходник хранить нельзя. Выгрузка реестра несёт содержимое сессий, CLAUDE.md § «Данные» запрещает ему попадать в замер, и рядом с производным лежит не исходник, а МИНИМУМ, ДОСТАТОЧНЫЙ ДЛЯ ПРОВЕРКИ: complete и sessions (полна ли была выгрузка и из скольких сессий сложено), source (реестр или транскрипт). Держится обеими сторонами — whitelist.build_sample требует эти поля при сборке, а гейт «секреты и замеры в диффе» в scripts/preflight.py не пускает в этот репозиторий сами замеры. | `ArtVsMark` |
| 119 | `Engineering-Incidents-Playbook` — гейт: scripts/check_candidates.py исключает README.md из отбора кандидатов, scripts/check_links.py — свои производные; инструмент не обрабатывает собственный вывод; `Stepik-Python-Grader` — гейт: src/stepik_grader/core/test_loader.py — обход берёт только .py и не заходит в скрытые каталоги (_is_hidden_or_service_dir), поэтому .grader_cache/ и .grader_stats.jsonl под него не попадают; шаблон task*.py — приоритет с откатом (_solution_files_in возвращает by_pattern or files), а не жёсткий фильтр; закреплено tests/test_loader.py; `Claude-Code_Usage-Token` — гейт: scripts/preflight.py и scripts/changelog.py. Инструментов, которые читают и пишут в одном каталоге, здесь два, и оба свой вывод из маски входа исключают. Сборка changelog читает changelog.d/*.md и пропускает README.md явным условием, а свод складывает в корень — не в тот каталог, который перечитывает следующим прогоном. Гейт секретов собирает входы через git ls-files --others, то есть видит и неотслеженное; клон чужого каталога правил, который делает прогон входящих, назван в .gitignore именно поэтому — иначе чужие исходники попали бы под нашу маску и покраснели бы на чужих правилах. | `ArtVsMark` |
| 121 | `Stepik-Python-Grader` — конвейер: scripts/check_container_closure.py — ночной обход сверяет состояние эпика со счётчиком незакрытых дочерних задач: закрытый контейнер с открытой работой становится находкой с адресатом; `Claude-Code_Usage-Token` — конвейер: .github/workflows/rules-inbox.yml и scripts/rules_answer.py. Контейнер здесь — задача #74 «разобрать очередь порциями», единицы — правила каталога, и закрытие контейнера доказывается СЧЁТЧИКОМ незакрытых единиц, а не тем, что порции кончились: прогон входящих печатает в задачу-указатель, сколько правил разобрано и у скольких статус unreviewed, а гейт ответа печатает, сколько всего записей и у скольких назван разрешимый адрес. Обе цифры собираются машиной из данных, а не ведутся руками, — отстать они не могут. | `Engineering-Incidents-Playbook` |
| 123 | `Engineering-Incidents-Playbook` — гейт: .github/workflows/ci.yml — коммиты ветки на pull_request; .github/workflows/attribution-history.yml — первопредки main на push; долг прошлой истории виден числом, а не подрезан; `Stepik-Python-Grader` — документ: CLAUDE.md § Формат коммитов: идентичность окна согласована до слияния, после squash подпись не переписать; смотрит scripts/check_attribution.py --check-branch, который не зовёт ни прогон, ни preflight; `ArtVsMark` — гейт: предметов три, перебраны все. Автор коммита — scripts/check_author.py: контейнерное умолчание облачного окна отвергается поимённо, и отказ печатает команду целиком. Трейлеры коммитов изменения — действие каталога шагом в .github/workflows/pr-check.yml, со своим списком имён в .github/authors.txt. Итоговая история — .github/workflows/attribution-history.yml: первопредки main с объявленного начала долга. Коммит вовсе без трейлеров отвергается НА ИЗМЕНЕНИИ — scripts/check_author.py::unattributed: у гейта каталога это устройство (на диапазоне он их считает числом, требует только на первопредках), и здесь живёт недостающая половина, а не вторая копия списка имён. Заведено 31 августа по живому долгу: ca0d920 уехал в main без единого трейлера, зелёный на всех проверках изменения; тот же гейт краснеет на нём задним числом. Что остаётся непокрытым: слово «Co-Authored-By:» в прозе, ставшее первым в строке после переноса, образец примет за трейлер — ложный пропуск, названный в наборе и отправленный в каталог обратным каналом. Оговорка по 143: на автора коммита в общей ветке ни один из трёх не влияет — его задаёт учётная запись, открывшая изменение; .github/workflows/open-pr.yml — изменение открывает токен владельца, а не окно: автором squash-коммита площадка ставит автора ИЗМЕНЕНИЯ, и соглашение держалось тем, что изменения открывал владелец. В окне, где на запись отвечает бот, оно перевернулось молча — коммит ca7dfcd в main подписан claude[bot], а владелец уехал в Co-authored-by мимо .github/authors.txt; .github/workflows/metrics.yml подписывает исполнителя суточной пересборки трейлером, а .github/authors.txt принимает его имя осознанно и с границей. ЗАМЕР 30 августа: три пересборки уехали в общую ветку вовсе без атрибуции, и создало это изменение #83 — убрав бота из авторов коммитов, оно убрало и расхождение, ради которого площадка дописывала Co-authored-by. Каждое изменение было зелёным на своём PR; дефект виден только в итоговой истории, ради чего гейт первопредков и заведён | `Claude-Code_Usage-Token` |
| 124 | `Engineering-Incidents-Playbook` — документ: AGENTS.md § Перезапуск — это диагностика. Перезапускается ОДНА упавшая работа, а не весь прогон; попытка ровно одна — второй перезапуск того же места это попытка получить нужный ответ повторением вопроса. Три случая разрешённого перезапуска разведены таблицей, и каждый называет, ЧТО записывается: причина найдена и устранена — ничего, это обычная починка; работа умерла до первого теста — фрагмент журнала; та же работа зеленела на этом же коммите раньше — фрагмент журнала как НЕСТАБИЛЬНОСТЬ, с номером прогона. Отдельного реестра нестабильностей нет намеренно: запись едет тем же фрагментом в changelog.d/, что и всякая починка, и там же отвечает, тянет ли она на правило — второй реестр разошёлся бы с первым (022). Сказано и то, что «флаки» причиной не является. У соседа это прогон с закрытым списком разрешённых к автоперезапуску и своим файлом находок; приём взят, файл нет — здесь перезапускает человек кнопкой площадки, и автоматического перезапуска нет вовсе (162). ГРАНИЦА: что перезапуск СОСТОЯЛСЯ, машина здесь не видит — кнопку жмёт человек, и запись остаётся на нём; `Stepik-Python-Grader` — конвейер: scripts/rerun_flaky_checks.py: список разрешённых к автоперезапуску закрыт, попытка ровно одна, а зелёное со второго раза записывается находкой в docs/agent/flaky-runs.md | `Claude-Code_Usage-Token` |
| 125 | `Engineering-Incidents-Playbook` — гейт: scripts/build_rules_index.py — область и даты из источников; `Stepik-Python-Grader` — гейт: scripts/check_generated_sources.py — у производного файла назван живой исходник; DIGEST.md и указатель правил пересобираются генератором, а не правятся; `Claude-Code_Usage-Token` — гейт: scripts/changelog.py — свод CHANGELOG.md собирается из changelog.d/, и фрагменты при складывании УДАЛЯЮТСЯ: без этого заметки следующего выпуска повторили бы записи прошлого, потому что источником стал бы собственный вывод. scripts/version.py считает по git-истории, а не по прежнему значению. | `ArtVsMark` |
| 130 | `Engineering-Incidents-Playbook` — конвейер: scripts/sync_inbox.py::candidates_here — во «входящие» потребителя приезжает раздел «Возможно, про это ваши задачи»: правила, ещё не разобранные у него, рядом с ЕГО ОТКРЫТЫМИ ЗАДАЧАМИ, чьи заголовки говорят о том же. Доставить правило мало: без предмета в своём проекте оно остаётся абстракцией, которую откладывают — «понятно, но не про нас». Связывают значимые слова: короче пяти знаков в счёт не идут (в русском это почти всегда служебное), общие слова каталога — «правило», «механизм», «проект» — исключены поимённо, потому что стоят и в правилах и в задачах и связывают всё со всем. Порог: два общих слова либо одно длиной от девяти. Показывается не больше двух задач на правило: список-отчёт не читают (016). ГРАНИЦА НАЗВАНА В САМОМ РАЗДЕЛЕ, а не только здесь: совпадение по словам — ПОДСКАЗКА, а не вердикт; ни принять правило, ни отклонить его список не может. Трекер не ответил — раздела просто нет: 130 говорит «приходит вместе с», а не «не приходит без», и ронять доставку правил из-за подсказки значило бы менять предмет на украшение (084). Приём взят у грейдера — у него это свой прогон связи правил с задачами (162). Набор — tests/test_sync_inbox.py, семь случаев с обеих сторон; `Stepik-Python-Grader` — конвейер: scripts/link_rules_to_issues.py — новое правило приходит вместе со списком кандидатов из нашего трекера | `Claude-Code_Usage-Token` |
| 132 | `Engineering-Incidents-Playbook` — документ: AGENTS.md § Критические запреты — «не везти в одном изменении две темы» стоит запретом наравне с остальными, и там же сказано, ПОЧЕМУ у него нет гейта: число тронутых зон сборности не доказывает (правка одного правила законно трогает пять зон и остаётся одной темой), а ложный отказ на широкой теме дороже пропуска и приучает читать красное как фон (051). Само правило требует предупреждения, а не отказа — и предупреждение есть: шаг «кто ещё правит те же файлы» в .github/workflows/agent-pr.yml пишет пересечения в сводку работы, не блокируя (133). Признак нарушения назван и читается, а не считается: заголовок изменения не описывается одной строкой без союза «и». У соседа ровно то же и по той же причине: запрет документом, пересечение неблокирующим шагом, гейта нет намеренно (162). ГРАНИЦА: одна тема в изменении или две — из диффа не следует, и судит это приёмка; `Stepik-Python-Grader` — конвейер: scripts/check_work_overlap.py показывает пересечение неблокирующим шагом scripts/preflight.py, а CLAUDE.md § Метки при заведении issue требует объявить все задачи сборного изменения (Closes #N либо «Часть #N»); `ArtVsMark` — документ: CLAUDE.md § Критические запреты — не везти в одном PR несколько тем; .github/pull_request_template.md — тот же вопрос критику. Гейта нет намеренно: число затронутых зон сборности не доказывает, а ложный отказ на широкой теме дороже пропуска. Правило само требует предупреждения, а не отказа, — а предупреждать здесь некому | `Claude-Code_Usage-Token` |
| 136 | `Engineering-Incidents-Playbook` — документ: .rules/bindings.json — вердикт о себе пишется после перебора предметов, и перебор называется в причине; гейта на полноту перебора нет; `Stepik-Python-Grader` — гейт: ответ по внешнему правилу пишется в .rules/bindings.json одним заходом: сначала перечисляются все свои предметы правила, потом вердикт; сверяется на ревью PR — гейта на полноту перечисления нет | `ArtVsMark`, `Claude-Code_Usage-Token` |
| 139 | `Stepik-Python-Grader` — документ: CONTRIBUTING.md § Когда дефект считается исправленным и чек-лист CLAUDE.md: дефект закрыт прогоном той поверхности, где найден, — браузер браузером, CLI командой; `ArtVsMark` — документ: .rules/README.md § Конвейер — каждое звено названо вместе с изменением, на котором оно отработало: механизм считается подтверждённым прогоном, а не чтением; `Claude-Code_Usage-Token` — гейт: tests/test_repo_links.py, tests/test_subprocess_encoding.py, tests/test_utf8_output.py — гейт запускается ПРОЦЕССОМ и проверяется его код возврата, а не чтение исходника. Оплачено четырьмя случаями за серию: mergeable_state «behind» без защиты ветки не появляется; в эталон попадал джоб самой очереди; очередь не просыпалась на последней позеленевшей проверке; отменённый прогон шёл впереди успешного. Ни один не был виден по зелёному набору тестов. | `Engineering-Incidents-Playbook` |
| 141 | `Engineering-Incidents-Playbook` — гейт: scripts/check_gates.py — набор «сборка указателя»: маркер и его расширение прогоняются как отдельный случай; `Stepik-Python-Grader` — гейт: scripts/check_marker_matching.py — константа-маркер не подставляется в startswith/removeprefix; префикс от маркера отличается именем, и это названо в самих константах; `Claude-Code_Usage-Token` — гейт: scripts/preflight.py — _НАБОР_ССЫЛКОЙ ищет ссылку, а не подстроку адреса; scripts/pr_check.py — _PR_EVENT не принимает pull_request_target за pull_request. Первое оплачено инцидентом: гейт остался зелёным, когда адрес ссылки подменили, а подпись оставили. | `ArtVsMark` |
| 144 | `Engineering-Incidents-Playbook` — гейт: scripts/check_text_cuts.py — у каждого разреза строки по точке (split, rsplit, partition, find, index; включая регулярку [.!?]) обязана стоять рядом пометка «не проза: <что именно>». Разбор дерева, а не поиск подстроки; `Stepik-Python-Grader` — конвейер: scripts/check_audit_registry.py — mention_verdict берёт окно контекста абзацем, а заголовок раздела перевешивает форму строки; закреплено тестами test_check_audit_registry.py; `Claude-Code_Usage-Token` — гейт: scripts/check_pr_metadata.py — разбор тела PR идёт СТРОКОЙ, а не «до ближайшей точки»: образцы _NO_ISSUE_RE и _PART_RE заякорены на ^…$ с re.MULTILINE, то есть границей служит структура разметки, как правило и предписывает. Проверено перебором, а не памятью: во всём дереве нет ни одного find(".") или rfind(".") как границы окна — единственное деление по точке (scripts/utf8_output.py) режет имя модуля, а не прозу. | `ArtVsMark` |
| 146 | `Engineering-Incidents-Playbook` — гейт: scripts/aggregate_bindings.py — обязательная проверка сверяет сводку с ОТВЕТОМ на диске, а не только саму с собой; до #122 она подтверждала своё основание тем же зелёным, каким подтверждала себя. Остальное правило держится разбором при приёмке: замер живого предмета машинно не отличить от рассуждения; `Stepik-Python-Grader` — документ: docs/agent/preflight.md § Что гейты не ловят: зелёный гейт подтверждает себя, утверждение проверяется замером на живом предмете, замер пишется рядом с механизмом; `Claude-Code_Usage-Token` — гейт: tests/test_subprocess_encoding.py — тест на дерево проекта отделён от тестов на подделках: зелёный гейт подтверждает себя, а утверждение о дереве проверяется отдельно. Две мутации за серию прошли зелёными и показали, что тестов не хватает — «пустая строка обрывает блок run» и «нечисловое значение складывается». | `ArtVsMark` |
| 153 | `Engineering-Incidents-Playbook` — документ: export/README.md § контракт — чужие решения описаны ссылкой на репозиторий потребителя, а не пересказом их устройства; .rules/consumers.json — про потребителя хранится адрес и роль, но не объяснение, почему у него так. Держится чтением при приёмке: отличить ссылку от пересказа машинно нечем; `Stepik-Python-Grader` — конвейер: docs/agent/rules/DIGEST.md собирается из каталога генератором (scripts/generate_rules_digest.py), а не переписывается руками: чужой текст здесь производное с живым исходником, и расхождение ловит check_rules_digest.py; `Claude-Code_Usage-Token` — документ: .github/workflows/rules-inbox.yml — единственное место, где объясняется устройство чужого проекта, и оно попадает ровно в исключение правила: чужое обоснование зафиксировано ВЕРСИЕЙ. Действие каталога подключено тегом v1.1.0, а не main, поэтому абзац «умолчание в закреплённой версии — старое имя» не может устареть от правки на той стороне: та сторона в этом теге больше не двигается. Остальное чужое «почему» лежит ссылкой: правила каталога здесь называются номерами, а не пересказываются, — и в CLAUDE.md, и в .rules/bindings.json. | `ArtVsMark` |
| 162 | `Engineering-Incidents-Playbook` — гейт: scripts/check_bindings.py — метрика «НИЧЕМ» тут же называет, сколько из очереди уже решено у соседа, у кого именно и где смотреть адрес; вопрос задаётся в тот момент, когда выбирают, что строить, а не отдельной командой, которую надо помнить. Свёртка одна на весь каталог: ею же собирается раздел «У соседей это уже решено» во входящие потребителю (scripts/sync_inbox.py). ГРАНИЦА: подошёл ли чужой приём, гейт не судит — стеки разные, и это метрика с адресами, а не отказ; красное на «у соседа есть, а у тебя нет» приучало бы пропускать красное (051); `Stepik-Python-Grader` — конвейер: scripts/check_rule_bindings.py::neighbour_holds печатает, чем правило без механизма держится у соседей по своду — собирает из export/where.json каталога, а не походом по чужим репозиториям; ходит ночным обходом; `ArtVsMark` — конвейер: scripts/neighbours.py — читает сводку каталога «чем держат другие» и по каждому нашему вердикту без механизма показывает соседей с их адресами; шаг «Чем это держат соседи» в .github/workflows/pr-check.yml приносит это в изменение. Себя в советчики не берёт, неподключённого соседа не берёт, ответ без разрешимого адреса не берёт — пересказ помогает не больше, чем его отсутствие. ГЕЙТОМ НЕ СДЕЛАНО НАМЕРЕННО: «приём переносится» решает человек, стеки разные, и отказ означал бы «повтори за соседом» — ровно ту копию, которую запрещает 090. Первый же прогон дал ответ по всем шестнадцати пробелам витрины. | `Claude-Code_Usage-Token` |
| 169 | `Engineering-Incidents-Playbook` — гейт: scripts/check_schedules.py — роль расписания объявлена в .rules/schedules.json: main либо safety-net. У страховки обязателен замер срабатываний, а страховка со сроком короче промежутка расписания отвергается сразу; `Stepik-Python-Grader` — конвейер: scripts/measure_queue_wakeups.py — замер источников пробуждения очереди выводится из живых прогонов, ночным обходом .github/workflows/tracker-guardrails.yml; отказ односторонний: страховка объявлена и по расписанию не пришло ни одного прогона. Шапка .github/workflows/merge-queue.yml называет наблюдаемое (42 срабатывания вместо ~201 за 201 час), а не заказанное; `Claude-Code_Usage-Token` — гейт: .github/workflows/merge-queue.yml — очередь просыпается от завершения каждого workflow по pull_request, а расписание оставлено дополнением, а не основой. Замер: cron 13,43 давал задержку до получаса. Правило родилось здесь. | `ArtVsMark` |
| 173 | `Engineering-Incidents-Playbook` — гейт: scripts/pr_body.py — три ответа различаются машинно, «Part of #NNN» требует названного остатка; scripts/check_task_state.py плюс .github/workflows/task-state.yml — состояние задачи спрашивается ПОСЛЕ слияния, замечание пишется в саму задачу; `Stepik-Python-Grader` — конвейер: scripts/check_issue_state_after_merge.py спрашивает у трекера судьбу задачи ПОСЛЕ слияния — закрыта ли закрытая, открыта ли частичная, назван ли остаток галочками; ночным обходом .github/workflows/tracker-guardrails.yml. Первая половина — три ответа (Closes #N · «Часть #N — что именно» · «Без issue:») — в scripts/check_pr_ready.py, но он числится в GATE_DEBT: запускает его окно руками, поэтому уровень взят по слабейшему звену (issue #1419); `Claude-Code_Usage-Token` — гейт: scripts/check_pr_metadata.py — связь с задачей обязательна и имеет ровно три формы: «Closes #N», «Часть #N — <что именно>» с пояснением, «Без issue: <причина>». Вторая половина правила — проверка судьбы задачи ПОСЛЕ слияния — механизмом здесь не держится, и это названо, а не умолчано: закрытие проверяет площадка, остаток частичного изменения не проверяет никто. | `ArtVsMark` |

## Сколько держит механизм · How much each mechanism holds

> Считается путь к файлу, найденный в поле `where` ответа потребителя. Механизм, держащий много правил, — это и образец, и точка отказа.

> Counted by the file path found in the consumer's `where` field. A mechanism holding many rules is both a model to copy and a single point of failure.

| Проект · Project | Механизм · Mechanism | Держит правил · Rules held |
|---|---|---|
| `Engineering-Incidents-Playbook` | `scripts/build_rules_index.py` | 12 |
| `Engineering-Incidents-Playbook` | `.github/workflows/ci.yml` | 11 |
| `Engineering-Incidents-Playbook` | `scripts/check_gates.py` | 11 |
| `Engineering-Incidents-Playbook` | `scripts/check_bindings.py` | 10 |
| `Engineering-Incidents-Playbook` | `.github/workflows/automerge.yml` | 9 |
| `Engineering-Incidents-Playbook` | `scripts/aggregate_bindings.py` | 9 |
| `Engineering-Incidents-Playbook` | `AGENTS.md` | 8 |
| `Engineering-Incidents-Playbook` | `export/README.md` | 8 |
| `Engineering-Incidents-Playbook` | `.github/workflows/agent-pr.yml` | 7 |
| `Engineering-Incidents-Playbook` | `scripts/check_charter.py` | 7 |
| `Engineering-Incidents-Playbook` | `CONTRIBUTING.md` | 6 |
| `Engineering-Incidents-Playbook` | `scripts/check_showcase.py` | 6 |
| `Engineering-Incidents-Playbook` | `scripts/check_workflows.py` | 6 |
| `Engineering-Incidents-Playbook` | `scripts/check_prose.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/check_subprocess.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/link_trails.py` | 5 |
| `Engineering-Incidents-Playbook` | `scripts/audit_catalogue.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/check_attribution.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/collect_proposals.py` | 4 |
| `Engineering-Incidents-Playbook` | `scripts/ghcli.py` | 4 |
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
| `Engineering-Incidents-Playbook` | `scripts/sync_inbox.py` | 3 |
| `Engineering-Incidents-Playbook` | `scripts/version.py` | 3 |
| `Engineering-Incidents-Playbook` | `.github/workflows/attribution-history.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/badges.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/consumers-sync.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/main-red.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.github/workflows/off-prefix.yml` | 2 |
| `Engineering-Incidents-Playbook` | `.rules/bindings.json` | 2 |
| `Engineering-Incidents-Playbook` | `.rules/schedules.json` | 2 |
| `Engineering-Incidents-Playbook` | `rules/README.md` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_links.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_own_name.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/check_schedules.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/pr_body.py` | 2 |
| `Engineering-Incidents-Playbook` | `scripts/sync_labels.py` | 2 |
| `Engineering-Incidents-Playbook` | `tests/test_ghcli.py` | 2 |
| `Engineering-Incidents-Playbook` | _остальные_ · _the rest_ | 44 механизмов по одному правилу; без названного адреса: 0 из 137 |
| `Stepik-Python-Grader` | `CLAUDE.md` | 39 |
| `Stepik-Python-Grader` | `.github/workflows/ci.yml` | 12 |
| `Stepik-Python-Grader` | `docs/agent/multiagent.md` | 12 |
| `Stepik-Python-Grader` | `docs/agent/preflight.md` | 9 |
| `Stepik-Python-Grader` | `scripts/check_rule_bindings.py` | 9 |
| `Stepik-Python-Grader` | `.github/workflows/tracker-guardrails.yml` | 8 |
| `Stepik-Python-Grader` | `docs/agent/environments.md` | 7 |
| `Stepik-Python-Grader` | `scripts/check_docs_guardrails.py` | 7 |
| `Stepik-Python-Grader` | `scripts/check_pr_ready.py` | 7 |
| `Stepik-Python-Grader` | `scripts/gh_rest.py` | 7 |
| `Stepik-Python-Grader` | `scripts/preflight.py` | 7 |
| `Stepik-Python-Grader` | `docs/agent/roles.md` | 6 |
| `Stepik-Python-Grader` | `.rules/bindings.json` | 5 |
| `Stepik-Python-Grader` | `CHANGELOG.md` | 4 |
| `Stepik-Python-Grader` | `scripts/check_adr_records.py` | 4 |
| `Stepik-Python-Grader` | `scripts/check_attribution.py` | 4 |
| `Stepik-Python-Grader` | `scripts/check_work_overlap.py` | 4 |
| `Stepik-Python-Grader` | `scripts/check_workflow_guardrails.py` | 4 |
| `Stepik-Python-Grader` | `.rules/proposals.json` | 3 |
| `Stepik-Python-Grader` | `HISTORY.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/claude-handoff.md` | 3 |
| `Stepik-Python-Grader` | `docs/agent/course-walkthrough.md` | 3 |
| `Stepik-Python-Grader` | `scripts/rerun_flaky_checks.py` | 3 |
| `Stepik-Python-Grader` | `src/stepik_grader/web/playground.py` | 3 |
| `Stepik-Python-Grader` | `.claude/hooks/pre_tool_use.py` | 2 |
| `Stepik-Python-Grader` | `CONTRIBUTING.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/corpus.md` | 2 |
| `Stepik-Python-Grader` | `docs/dev/glossary.md` | 2 |
| `Stepik-Python-Grader` | `scripts/check_audit_registry.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_branch_protection.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_declared_outcomes.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_gate_tests.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_generated_sources.py` | 2 |
| `Stepik-Python-Grader` | `scripts/check_hidden_defaults.py` | 2 |
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
| `Stepik-Python-Grader` | _остальные_ · _the rest_ | 91 механизмов по одному правилу; без названного адреса: 0 из 172 |
| `ArtVsMark` | `scripts/build_metrics.py` | 30 |
| `ArtVsMark` | `scripts/check_mechanisms.py` | 27 |
| `ArtVsMark` | `CLAUDE.md` | 14 |
| `ArtVsMark` | `scripts/check_labels.py` | 14 |
| `ArtVsMark` | `.github/workflows/automerge.yml` | 12 |
| `ArtVsMark` | `README.md` | 12 |
| `ArtVsMark` | `.github/workflows/open-pr.yml` | 10 |
| `ArtVsMark` | `.github/workflows/pr-check.yml` | 10 |
| `ArtVsMark` | `scripts/check_roles.py` | 10 |
| `ArtVsMark` | `.github/workflows/metrics.yml` | 8 |
| `ArtVsMark` | `.rules/README.md` | 7 |
| `ArtVsMark` | `HISTORY.md` | 7 |
| `ArtVsMark` | `scripts/check_author.py` | 7 |
| `ArtVsMark` | `scripts/check_bindings.py` | 7 |
| `ArtVsMark` | `scripts/check_page.py` | 7 |
| `ArtVsMark` | `scripts/checks.py` | 7 |
| `ArtVsMark` | `scripts/gh_outcome.py` | 6 |
| `ArtVsMark` | `scripts/hold.py` | 6 |
| `ArtVsMark` | `.github/workflows/main-red.yml` | 5 |
| `ArtVsMark` | `.github/workflows/release-hold.yml` | 5 |
| `ArtVsMark` | `.github/workflows/rules-inbox.yml` | 5 |
| `ArtVsMark` | `.rules/bindings.json` | 4 |
| `ArtVsMark` | `.rules/roles.md` | 4 |
| `ArtVsMark` | `scripts/check_journal.py` | 4 |
| `ArtVsMark` | `.rules/proposals.json` | 3 |
| `ArtVsMark` | `pr-check.yml` | 3 |
| `ArtVsMark` | `projects.json` | 2 |
| `ArtVsMark` | `scripts/neighbours.py` | 2 |
| `ArtVsMark` | _остальные_ · _the rest_ | 6 механизмов по одному правилу; без названного адреса: 0 из 86 |
| `Claude-Code_Usage-Token` | `scripts/preflight.py` | 29 |
| `Claude-Code_Usage-Token` | `CLAUDE.md` | 24 |
| `Claude-Code_Usage-Token` | `docs/spec.md` | 13 |
| `Claude-Code_Usage-Token` | `.rules/bindings.json` | 11 |
| `Claude-Code_Usage-Token` | `scripts/changelog.py` | 11 |
| `Claude-Code_Usage-Token` | `scripts/rules_answer.py` | 10 |
| `Claude-Code_Usage-Token` | `.github/workflows/rules-inbox.yml` | 9 |
| `Claude-Code_Usage-Token` | `scripts/merge_queue.py` | 9 |
| `Claude-Code_Usage-Token` | `scripts/pr_check.py` | 9 |
| `Claude-Code_Usage-Token` | `scripts/pr_ready.py` | 9 |
| `Claude-Code_Usage-Token` | `scripts/utf8_output.py` | 9 |
| `Claude-Code_Usage-Token` | `src/claude_code_usage/whitelist.py` | 9 |
| `Claude-Code_Usage-Token` | `src/claude_code_usage/cli.py` | 7 |
| `Claude-Code_Usage-Token` | `docs/labels.md` | 6 |
| `Claude-Code_Usage-Token` | `scripts/check_pr_metadata.py` | 6 |
| `Claude-Code_Usage-Token` | `src/claude_code_usage/storage.py` | 6 |
| `Claude-Code_Usage-Token` | `.rules/showcase.json` | 5 |
| `Claude-Code_Usage-Token` | `scripts/shell_ascii.py` | 5 |
| `Claude-Code_Usage-Token` | `scripts/subprocess_encoding.py` | 5 |
| `Claude-Code_Usage-Token` | `tests/test_subprocess_encoding.py` | 5 |
| `Claude-Code_Usage-Token` | `.github/workflows/merge-queue.yml` | 4 |
| `Claude-Code_Usage-Token` | `CHANGELOG.md` | 4 |
| `Claude-Code_Usage-Token` | `README.md` | 4 |
| `Claude-Code_Usage-Token` | `docs/release.md` | 4 |
| `Claude-Code_Usage-Token` | `docs/roles.md` | 4 |
| `Claude-Code_Usage-Token` | `scripts/repo_links.py` | 4 |
| `Claude-Code_Usage-Token` | `src/claude_code_usage/transcripts.py` | 4 |
| `Claude-Code_Usage-Token` | `tests/test_pr_check.py` | 4 |
| `Claude-Code_Usage-Token` | `HISTORY.md` | 3 |
| `Claude-Code_Usage-Token` | `docs/versioning.md` | 3 |
| `Claude-Code_Usage-Token` | `scripts/gh_rest.py` | 3 |
| `Claude-Code_Usage-Token` | `scripts/release.py` | 3 |
| `Claude-Code_Usage-Token` | `scripts/version.py` | 3 |
| `Claude-Code_Usage-Token` | `tests/test_changelog.py` | 3 |
| `Claude-Code_Usage-Token` | `tests/test_transcripts.py` | 3 |
| `Claude-Code_Usage-Token` | `tests/test_utf8_output.py` | 3 |
| `Claude-Code_Usage-Token` | `.github/badges/version.json` | 2 |
| `Claude-Code_Usage-Token` | `.github/workflows/release.yml` | 2 |
| `Claude-Code_Usage-Token` | `.rules/proposals.json` | 2 |
| `Claude-Code_Usage-Token` | `README.en.md` | 2 |
| `Claude-Code_Usage-Token` | `docs/storage-setup.md` | 2 |
| `Claude-Code_Usage-Token` | `scripts/subprocess_timeout.py` | 2 |
| `Claude-Code_Usage-Token` | `tests/test_registry.py` | 2 |
| `Claude-Code_Usage-Token` | `tests/test_repo_links.py` | 2 |
| `Claude-Code_Usage-Token` | `tests/test_shell_ascii.py` | 2 |
| `Claude-Code_Usage-Token` | _остальные_ · _the rest_ | 16 механизмов по одному правилу; без названного адреса: 0 из 125 |

## Правила · Rules

| № | `Engineering-Incidents-Playbook` | `Stepik-Python-Grader` | `ArtVsMark` | `Claude-Code_Usage-Token` |
|---|---|---|---|---|
| 001 | действует | действует | действует | действует |
| 002 | действует | действует | действует | действует |
| 003 | действует | действует | нет предмета | действует |
| 004 | действует | действует | нет предмета | действует |
| 005 | действует | действует | действует | действует |
| 006 | действует | действует | действует | действует |
| 007 | нет предмета | действует | нет предмета | нет предмета |
| 008 | действует | нет предмета | действует | нет предмета |
| 009 | действует | действует | действует | действует |
| 010 | действует | действует | действует | действует |
| 011 | действует | действует | действует | действует |
| 012 | действует | действует | нет предмета | действует |
| 013 | действует | действует | нет предмета | действует |
| 014 | действует | действует | действует | действует |
| 015 | нет предмета | действует | нет предмета | нет предмета |
| 016 | действует | действует | действует | действует |
| 017 | действует | действует | нет предмета | действует |
| 018 | действует | действует | нет предмета | действует |
| 019 | нет предмета | действует | нет предмета | действует |
| 020 | отклонено | действует | нет предмета | нет предмета |
| 021 | действует | действует | действует | действует |
| 022 | действует | действует | действует | действует |
| 023 | действует | действует | действует | действует |
| 024 | действует | действует | отклонено | действует |
| 025 | действует | действует | действует | отклонено |
| 026 | действует | действует | нет предмета | действует |
| 027 | действует | действует | действует | действует |
| 028 | действует | действует | нет предмета | действует |
| 029 | действует | действует | действует | действует |
| 030 | действует | действует | нет предмета | действует |
| 031 | отклонено | действует | нет предмета | нет предмета |
| 032 | нет предмета | действует | действует | действует |
| 033 | действует | действует | нет предмета | действует |
| 034 | отклонено | действует | нет предмета | нет предмета |
| 035 | действует | действует | нет предмета | отклонено |
| 036 | нет предмета | действует | нет предмета | нет предмета |
| 037 | нет предмета | действует | нет предмета | действует |
| 038 | нет предмета | действует | действует | действует |
| 039 | действует | действует | действует | действует |
| 040 | действует | действует | нет предмета | действует |
| 041 | действует | действует | действует | действует |
| 042 | действует | действует | нет предмета | действует |
| 043 | действует | действует | нет предмета | действует |
| 044 | действует | действует | действует | действует |
| 045 | действует | действует | действует | действует |
| 046 | действует | действует | действует | действует |
| 047 | действует | действует | действует | действует |
| 048 | нет предмета | нет предмета | нет предмета | действует |
| 049 | действует | действует | действует | действует |
| 050 | нет предмета | действует | действует | нет предмета |
| 051 | действует | действует | действует | действует |
| 052 | действует | действует | нет предмета | действует |
| 053 | действует | действует | нет предмета | действует |
| 054 | действует | действует | нет предмета | действует |
| 055 | действует | действует | нет предмета | действует |
| 056 | действует | действует | действует | действует |
| 057 | действует | действует | действует | действует |
| 058 | действует | действует | нет предмета | действует |
| 059 | нет предмета | действует | нет предмета | действует |
| 060 | отклонено | действует | нет предмета | нет предмета |
| 061 | отклонено | действует | нет предмета | действует |
| 062 | действует | действует | действует | действует |
| 063 | действует | действует | действует | действует |
| 064 | действует | действует | действует | действует |
| 065 | действует | действует | действует | действует |
| 066 | нет предмета | действует | нет предмета | нет предмета |
| 067 | действует | действует | нет предмета | нет предмета |
| 068 | действует | действует | действует | действует |
| 069 | нет предмета | действует | нет предмета | действует |
| 070 | нет предмета | действует | нет предмета | действует |
| 071 | действует | действует | действует | действует |
| 072 | действует | действует | нет предмета | действует |
| 073 | нет предмета | действует | действует | действует |
| 074 | действует | действует | действует | действует |
| 075 | действует | действует | действует | действует |
| 076 | нет предмета | действует | нет предмета | действует |
| 077 | действует | действует | нет предмета | действует |
| 078 | нет предмета | действует | нет предмета | действует |
| 079 | действует | нет предмета | нет предмета | нет предмета |
| 080 | действует | действует | действует | действует |
| 081 | нет предмета | действует | нет предмета | действует |
| 082 | действует | действует | действует | действует |
| 083 | нет предмета | действует | нет предмета | нет предмета |
| 084 | действует | действует | нет предмета | отклонено |
| 085 | нет предмета | действует | нет предмета | нет предмета |
| 086 | действует | действует | нет предмета | действует |
| 087 | нет предмета | действует | нет предмета | действует |
| 088 | действует | действует | нет предмета | действует |
| 089 | действует | действует | действует | отклонено |
| 090 | действует | действует | действует | действует |
| 091 | действует | действует | действует | действует |
| 092 | нет предмета | действует | нет предмета | действует |
| 093 | действует | действует | нет предмета | действует |
| 094 | нет предмета | действует | нет предмета | нет предмета |
| 095 | нет предмета | действует | нет предмета | действует |
| 096 | действует | действует | нет предмета | действует |
| 097 | действует | действует | действует | действует |
| 098 | действует | действует | нет предмета | действует |
| 099 | действует | действует | нет предмета | действует |
| 100 | действует | действует | действует | действует |
| 101 | нет предмета | действует | нет предмета | действует |
| 102 | нет предмета | действует | нет предмета | действует |
| 103 | нет предмета | действует | нет предмета | нет предмета |
| 104 | действует | действует | действует | действует |
| 105 | действует | действует | действует | действует |
| 106 | действует | действует | нет предмета | действует |
| 107 | действует | действует | действует | действует |
| 108 | действует | действует | действует | действует |
| 109 | действует | действует | нет предмета | действует |
| 110 | нет предмета | действует | нет предмета | действует |
| 111 | действует | действует | действует | действует |
| 112 | нет предмета | действует | нет предмета | отклонено |
| 113 | действует | действует | нет предмета | действует |
| 114 | действует | действует | нет предмета | нет предмета |
| 115 | нет предмета | действует | нет предмета | нет предмета |
| 116 | отклонено | действует | нет предмета | действует |
| 117 | отклонено | действует | нет предмета | нет предмета |
| 118 | действует | действует | действует | действует |
| 119 | действует | действует | действует | действует |
| 120 | действует | действует | нет предмета | действует |
| 121 | действует | действует | нет предмета | действует |
| 122 | действует | действует | нет предмета | действует |
| 123 | действует | действует | действует | действует |
| 124 | действует | действует | нет предмета | действует |
| 125 | действует | действует | действует | действует |
| 126 | действует | действует | действует | действует |
| 127 | действует | действует | действует | действует |
| 128 | действует | действует | действует | действует |
| 129 | действует | действует | действует | действует |
| 130 | действует | действует | нет предмета | действует |
| 131 | действует | действует | действует | нет предмета |
| 132 | действует | действует | действует | действует |
| 133 | действует | действует | действует | действует |
| 134 | действует | действует | действует | действует |
| 135 | действует | действует | действует | действует |
| 136 | действует | действует | действует | действует |
| 137 | нет предмета | действует | действует | действует |
| 138 | действует | действует | действует | действует |
| 139 | действует | действует | действует | действует |
| 140 | действует | действует | действует | действует |
| 141 | действует | действует | действует | действует |
| 142 | действует | действует | действует | действует |
| 144 | действует | действует | действует | действует |
| 145 | действует | действует | действует | действует |
| 146 | действует | действует | действует | действует |
| 147 | действует | действует | действует | действует |
| 148 | действует | действует | действует | действует |
| 149 | нет предмета | действует | действует | нет предмета |
| 150 | действует | действует | действует | действует |
| 151 | действует | действует | действует | действует |
| 152 | действует | действует | действует | действует |
| 153 | действует | действует | действует | действует |
| 154 | действует | действует | действует | действует |
| 155 | действует | действует | нет предмета | нет предмета |
| 156 | действует | действует | действует | нет предмета |
| 157 | действует | действует | действует | действует |
| 158 | действует | действует | действует | действует |
| 159 | действует | действует | действует | действует |
| 160 | действует | действует | действует | отклонено |
| 161 | действует | действует | действует | действует |
| 162 | действует | действует | действует | действует |
| 163 | действует | действует | нет предмета | нет предмета |
| 164 | действует | действует | действует | действует |
| 165 | действует | действует | действует | действует |
| 166 | действует | действует | действует | действует |
| 167 | действует | действует | действует | действует |
| 168 | действует | действует | действует | действует |
| 169 | действует | действует | действует | действует |
| 170 | действует | действует | действует | действует |
| 171 | действует | действует | действует | действует |
| 172 | действует | действует | действует | действует |
| 173 | действует | действует | действует | действует |
| 174 | действует | действует | действует | действует |
| 175 | действует | действует | действует | действует |
| 176 | действует | действует | действует | действует |
| 177 | действует | — | не рассмотрено | — |
| 178 | действует | — | — | — |
| 179 | действует | — | — | — |
| 180 | действует | — | — | — |
