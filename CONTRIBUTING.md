# Как внести вклад · Contributing

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

[CC BY 4.0](LICENSE). Внося вклад, вы соглашаетесь, что он распространяется на
тех же условиях.
