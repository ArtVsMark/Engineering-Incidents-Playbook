# Как внести вклад · Contributing

> **Читатель:** участник — как внести правку сюда и что здесь примут.

Этот документ — для человека со стороны. Свод для агентского окна, работающего
внутри репозитория, отдельный: ядро [`AGENTS.md`](AGENTS.md) и надстройка
[`CLAUDE.md`](CLAUDE.md) поверх него. Разные читатели —
разные документы ([021](rules/ru/021-split-docs-by-reader.md)).

This document is for a person from outside. The rulebook for an agent session
working inside the repository is separate: the core [`AGENTS.md`](AGENTS.md)
and the [`CLAUDE.md`](CLAUDE.md) overlay on top of it.

## Что здесь принимают · What is accepted

**Правило с инцидентом.** Не «делай так», а разбор: что сломалось, как
обнаружили, чем обошлось, где это **не** работает.

**Правило без инцидента не принимается** — это предпочтение, а не правило, и
через месяц его нечем защитить. Отказ по этой причине не про качество текста:
хорошо написанное предпочтение остаётся предпочтением.

**A rule with an incident.** Not "do it this way" but a post-mortem: what broke,
how it surfaced, what it cost, and where it does **not** apply. A rule without an
incident is not accepted — that is a preference, and in a month there is nothing
left to defend it with.

## Что ещё принимают · Also welcome

- **второй инцидент к существующему правилу** — если он того же класса, но с
  другой причиной отказа: так дополнены 068 и 039;
- **граница применимости**, которой не хватало: «здесь это не работает, вот
  почему»;
- **исправление следа**, ведущего в никуда;
- **перевод**, если английская запись — подстрочник, а не текст
  ([077](rules/ru/077-key-parity-is-not-translation.md));
- **находка, что каталог нарушает собственное правило.** Такие ценнее всего:
  семь из них нашлись за один вечер, и все — по вопросу со стороны.

## Как устроена запись · The shape of a record

Формат неизменен: **правило → инцидент → почему → применимость → след**.
Разделы «Применимость» (где **не** работает) и «След» обязательны — именно их
чаще всего пропускают, и именно без них каталог превращается в свод «делай так».

Заготовка: [`templates/rule-template.md`](templates/rule-template.md).
Полностью, как ведётся каталог: [`120`](rules/ru/120-how-to-run-a-rule-catalogue.md).

## Порядок · The steps

**Каркас собирается командой, а не набирается руками:**

```
python scripts/new_rule.py --slug <слаг> --area <область> --trail <владелец/репо#номер>
```

Она берёт следующий свободный номер (номера не переиспользуются), кладёт файлы
в **оба** дерева, подставляет область из закрытого словаря и разрешимый след,
заводит ответ каталога и фрагмент журнала, показывает соседей. Дальше — ваше:
утверждение, инцидент, механизм поломки, граница «не работает». Генератор
этого не сделает, и это не лень: **сгенерированный инцидент был бы выдумкой, а
выдуманный инцидент хуже отсутствующего — он выглядит как основание.**

Предложение, приехавшее из проекта, превращается в каркас той же командой:
`--from-proposal владелец/репозиторий:слаг`. Слаг и след придут оттуда, **номер
присвоит каталог** — у предложения номера нет и быть не может.

The skeleton is generated, not typed. What the generator will never write is the
claim, the incident and the boundary: an invented incident is worse than a
missing one, because it looks like grounds.

Ниже — что именно происходит, если делать это руками.


0. **Спросить каталог, нет ли уже такого:**
   `python scripts/check_duplicates.py --near <номер|файл>`. Шаг нулевой,
   потому что он делается **до** того, как запись написана: правило 143
   переоткрыло то, что уже говорили 131 и 135, и было удалено — а искали бы,
   не написали бы. Ответ записывается в
   [`.rules/neighbours.json`](.rules/neighbours.json) и проверяется гейтом.
1. Номер — следующий свободный. **Номера не переиспользуются**, даже после
   удаления: пропуск в нумерации — законное состояние.
2. Имя файла латиницей, **одинаковое в обоих деревьях**: `rules/ru/` и
   `rules/en/`. Кириллица в именах ломает разрешение перекрёстных ссылок.
3. Строка `**Область.**` / `**Area.**` — из словаря в
   `scripts/build_rules_index.py`. Новая область дописывается туда осознанно и
   сразу с описанием.
4. Раздел «След» — задачей `владелец/репозиторий#номер` либо потребителем из
   [`.rules/consumers.json`](.rules/consumers.json) с названным артефактом.
   Проза следом не считается.
5. **Закоммитить правило**, затем пересобрать производные:
   `python scripts/build_rules_index.py`. Порядок именно такой: дата появления
   берётся из истории файла.
6. Ответить за новое правило в [`.rules/bindings.json`](.rules/bindings.json) —
   каталог отвечает за каждое своё правило, включая новое.
7. Фрагмент журнала в [`changelog.d/`](changelog.d/), одной строкой.

**Обе языковые версии сразу.** Не из аккуратности: запись на одном языке не
проходит сборку указателя, и это тот механизм, который не даёт деревьям
разойтись.

**Both language versions at once.** Not out of tidiness: a record in one language
fails the index build, and that is the mechanism keeping the trees together.

## Когда дефект считается исправленным · When a defect counts as fixed

**Красноту доказывают полу-откатом, а не откатом всего**
([014](rules/ru/014-red-before-fix-needs-partial-revert.md)). Убрать надо
**поведение**, оставив имена: функцию, ключ, поле, файл. Откат целиком даёт
`ImportError` или падение разбора — и набор краснеет не потому, что дефект
вернулся, а потому что сломан импорт. Такое красное не доказывает ничего.

Меняется **ровно одна переменная**: поведение убрано, имена на месте. Если
после этого набор не покраснел — он не проверяет то, ради чего написан
([146](rules/ru/146-a-green-gate-does-not-verify-its-premise.md)).

Годная мутация ломает **предмет** правила, а не его границу: подмена порога
проверяет арифметику сравнения, а подмена значения — решение. Отличить одно от
другого может только понимающий предмет, и это граница: гейт здесь не судья,
судит приёмка.

**A defect counts as fixed** only when the suite has been made red by a
*partial* revert: remove the behaviour, keep the names. A full revert breaks
the import and the red proves nothing.

## Своё ожидание — тоже гипотеза · Your own expectation is a hypothesis

Ожидание, написанное своей рукой, не доказывает ничего
([055](rules/ru/055-your-own-expectations-are-a-hypothesis.md)). Пока его не
подтвердил внешний источник, расхождение означает «один из двух неправ», а не
«предмет сломан». Практически это значит: **порог, словарь и «так быть не
может» берутся у замера, а не у автора.**

Внешних источников у каталога три, и все три доступны без сети к чужим людям:

- **корпус.** Порог считается по всем записям, а не по одной. Пороги
  `check_locale.py` замерены на 162 парах: доля кириллицы в английском дереве
  0.000–0.022 при потолке 0.15, в русском 0.814–0.946 при поле 0.50 — между
  худшим настоящим значением и порогом разы, а не проценты.
- **сосед.** Прежде чем строить свой механизм, спрашивают его ответ
  ([162](rules/ru/162-a-gap-asks-the-neighbours-first.md)) — и его же берут
  как контрпример. Проверка «раздел решений называет отвергнутую
  альтернативу» не заведена именно так: в истории соседа шесть разделов из
  двенадцати не содержат ни одного слова, по которому отказ узнаётся машинно,
  и словарь дал бы красное на верной работе
  ([051](rules/ru/051-warn-on-likely-block-on-certain.md)).
- **живая проба.** Механизм, читающий площадку, один раз прогоняется вживую
  ([139](rules/ru/139-a-mechanism-is-confirmed-by-a-run.md)): подделка
  проверяет только свои правила чтения, а сочиняет их автор вместе со своими
  допущениями.

Когда внешнего источника нет, остаётся **мутация**: сломать предмет и увидеть
красное (см. раздел выше). Согласие набора с собой доказательством не является
([146](rules/ru/146-a-green-gate-does-not-verify-its-premise.md)).

**Your own expectation proves nothing** until an external source confirms it:
a threshold, a vocabulary or a "this cannot happen" is taken from a measurement
over the whole corpus, from a neighbouring project's answer, or from one live
run — never from the author. Where no external source exists, mutate the
subject and watch it go red.

## Что идёт в историю, а что в журнал · History or changelog

[`HISTORY.md`](HISTORY.md) отвечает «почему решили именно так»,
[`CHANGELOG.md`](CHANGELOG.md) — «что изменилось». Смешивание съедает оба, и
критерий отбора обязан быть записан, иначе его подменяет память автора
([161](rules/ru/161-history-keeps-turning-points.md)).

**Единица истории — выпуск, а не запись о повороте.** Поворот не выносится
отдельным разделом: он рассказывается внутри того выпуска, который его принёс.
Форма взята у соседнего проекта, где история ведётся одиннадцатью релизами, и
взята целиком — первая попытка взяла у него только вывод «история это решения»
и завела свой жанр «Поворотный момент». Итог измерим: из трёх выпусков раздел
был у одного, а решения двух других лежали рядом с рядом тегов, ни к чему не
привязанные.

```
## vX.Y.0 · <дата> · <чем этот выпуск был>

**Контекст.** С чего началось: внешний сигнал, найденная поломка, замер.

**Что вошло.** Список с разрешимыми ссылками на задачи, изменения и правила.
Без ссылки выпуск остаётся рассказом — та же мерка, что «След» у правила.

**Решения.** Что выбрали и от чего отказались. Раздел о решениях, а не о
работе: решение без отвергнутой альтернативы — это ход работы ([026](rules/ru/026-rejected-findings-must-be-recorded.md)).

**Итог.** Чем проект стал после выпуска, одной фразой.
```

Незакрытый выпуск лежит под заголовком `## Не выпущено · <чем он будет>` в той
же форме; переименовывает его в номер и дату сам выпуск
(`scripts/history_metrics.py --add`), а не рука.

**Сюда не идёт** обычное добавление правила, починка ссылки, обновление
перевода, пересборка производных: это фрагмент в [`changelog.d/`](changelog.d/).

Форма проверяется машинно: `python scripts/audit_catalogue.py` требует четыре
части и разрешимую ссылку, `python scripts/history_metrics.py --check` — раздел
и строку метрик у каждого тега. **Отвергнутую альтернативу гейт не ищет**, и
это измерено: в истории соседа половина разделов «Решения» не называет отказ ни
одним словом из тех, по которым его можно узнать машинно. Словарь дал бы
красное на верной работе ([051](rules/ru/051-warn-on-likely-block-on-certain.md)),
и вопрос остаётся приёмке.

**History answers "why", the changelog answers "what changed".** The unit of
history is a **release**, not a stand-alone "turning point" entry: the decision
is told inside the release that carried it, in four parts — context, what
shipped (with resolvable links), decisions with the rejected alternative, and
the outcome. Ordinary additions and fixes go to [`changelog.d/`](changelog.d/).

## Прежде чем открывать PR · Before opening a PR

Одной командой — она читает шаги из конвейера и запускает те, у которых есть
предмет без изменения; чего запустить нельзя, называет:

```
python scripts/preflight.py
```

**By one command.** It reads the steps from the pipeline, runs those that have
a subject outside a pull request, and names the ones it cannot run.

Поштучно — теми же командами, что и в конвейере. Канонический список — шаги в
[`.github/workflows/ci.yml`](.github/workflows/ci.yml); ниже он повторён для
удобства, и если два списка разошлись, прав файл конвейера:

```
python scripts/build_rules_index.py --check
python scripts/check_links.py
python scripts/check_attribution.py
python scripts/collect_changelog.py --check
python scripts/check_bindings.py
python scripts/aggregate_bindings.py --check
python scripts/audit_catalogue.py
python scripts/check_charter.py
python scripts/check_duplicates.py --check
python scripts/collect_proposals.py --check
python scripts/check_gates.py
python scripts/check_candidates.py
python scripts/main_red.py --selftest
python scripts/link_trails.py --selftest
python scripts/refresh_derived.py --selftest
python scripts/check_showcase.py
python scripts/check_test_deps.py
python scripts/check_workflows.py
python scripts/check_templates.py
python scripts/check_connect.py
python scripts/check_readers.py
python scripts/check_locale.py
python scripts/check_skips.py
python scripts/check_prose.py
python scripts/history_metrics.py --check
python scripts/check_labels.py --paths-from <файл со списком путей> --have <метки>
python scripts/pr_body.py --check --body-file <файл с телом изменения>
```

У каждого **три исхода**: `0` чисто · `1` есть находки · `2` проверка не
отработала. Третий — не разновидность второго: находку чинит автор, а
неотработавшую проверку тот, кто запускает.

Коммит несёт трейлеры авторства — они сверяются со списком в
[`.github/authors.txt`](.github/authors.txt)
([123](rules/ru/123-attribution-is-verified-on-the-final-history.md)).

## Путь новичка · The newcomer's path

Метки [`good first issue`](.github/labels.yml) и `help wanted` — вход, и их
**две** намеренно: путь не кончается первым вкладом, а второй барьер обиднее
первого, потому что человек уже вложился.

Тело такой задачи ведётся **на двух языках**, и правило действует в момент
навешивания метки, а не создания задачи: вешаете метку на старую русскоязычную
задачу — сначала дописываете перевод
([065](rules/ru/065-the-onramp-must-speak-the-newcomers-language.md)).

The two entry labels are deliberate: the path does not end with the first
contribution, and the second barrier stings more than the first because the
person has already invested. Their bodies are kept in both languages, and the
rule applies when the label is **attached**, not when the issue is created.

## О чём спорить полезно · Worth arguing about

Возражение по существу ценнее согласия. Особенно:

- **границы применимости** — «у вас это не сработает вот здесь»;
- **правило, которое дублирует соседнее** — два правила об одном хуже одного;
- **правило без механизма**, названное правилом с механизмом.

Отвергнутый вариант записывается с причиной, а не выбрасывается: иначе он
вернётся следующей ревизией ([026](rules/ru/026-rejected-findings-must-be-recorded.md)).

## Лицензия · License

[CC BY 4.0](LICENSE) — записи, витрина и заготовки-документы.
[MIT](LICENSE-CODE) — скрипты, прогоны и исполняемые заготовки. Внося вклад, вы
соглашаетесь, что он распространяется на условиях той половины, к которой
относится: правило — CC BY, скрипт — MIT.

[CC BY 4.0](LICENSE) for the records, the showcase and the document templates;
[MIT](LICENSE-CODE) for scripts, workflows and executable templates. By
contributing you agree your contribution goes out under whichever of the two
covers it.
