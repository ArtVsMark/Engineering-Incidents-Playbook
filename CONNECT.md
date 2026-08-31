# Подключение проекта к каталогу

**Кому это.** Проекту — новому или уже живущему, — который хочет держаться
этих правил. Тому, кто пришёл почитать, нужны [`README.md`](README.md) и
[`TOP-10.md`](TOP-10.md); тому, кто правит сам каталог, —
[`CONTRIBUTING.md`](CONTRIBUTING.md) и [`AGENTS.md`](AGENTS.md). Документы
разведены по читателю намеренно
([021](rules/ru/021-split-docs-by-reader.md)).

**Главное: подключаются командой, а не копированием.** Каталог отдаёт наружу
не только текст правил, но и механизмы — команду подключения, действие для
прогонов, готовые скрипты. Перенос руками того, что уже собрано инструментом,
заводит вторую реализацию одного алгоритма, и первая же правка разводит их
([090](rules/ru/090-shared-helpers-move-up-not-sideways.md)).

---

## Шаг первый — одна команда

```
python scripts/onboard_consumer.py --repo владелец/имя --out ПАПКА
```

Команда собирает готовый набор и кладёт его в указанную папку:

| Файл | Что это |
|---|---|
| `.rules/bindings.json` | ответ проекта по **каждому** правилу каталога: статус, чем держится, где. Заготовлен со статусом `unreviewed` — разбирается по одному |
| `.rules/proposals.json` | канал обратно: правило, родившееся здесь, едет в каталог этим файлом |
| `.github/workflows/rules-inbox.yml` | ежедневный прогон и ручная кнопка; тег каталога в нём **закреплён** |

Файлы несёт в свой репозиторий человек: каталог в чужие репозитории не пишет
и ничего не рассылает сам
([131](rules/ru/131-no-writes-from-a-cloud-session.md)). Рассылка потребовала
бы токена с правом записи во все проекты, включая приватные, — одной точки
отказа ради уведомления.

## Что приезжает дальше, само

Прогон `rules-inbox` ведёт **одну** задачу-«входящие» и обновляет её, а не
плодит новые:

- **очередь правил** — по каким записям каталога проект ещё не ответил;
- **«У соседей это уже решено»** — правила, которые здесь не держатся ничем, а
  у соседнего проекта держатся, с адресом механизма
  ([162](rules/ru/162-a-gap-asks-the-neighbours-first.md)). Чужой приём не
  обязан подойти: раздел отвечает «вот кто уже сталкивался», а не «сделай так»;
- **лишние ответы** — ответ о правиле, которого в каталоге нет: номер снят, а
  ответ остался и завтра прочитается как решение по чужой записи.

## Инструменты каталога

Список **единственный**: README и START ссылаются сюда, а не заводят второй
([022](rules/ru/022-one-canonical-document.md)). Что отсюда пропало, а в
`scripts/` осталось — держит `scripts/check_connect.py`.

| Инструмент · Tool | Что делает · What it does | Где запускается · Where |
|---|---|---|
| `scripts/onboard_consumer.py` | собирает набор для подключения: ответ, канал предложений, прогон с закреплённым тегом | у каталога, набор несёт человек |
| `uses: ArtVsMark/claude-code-playbook@<!--m:ref-->v1.1.0<!--/m:ref-->` | действие «входящие»: тянет `export/rules.json`, сверяет с ответом проекта, ведёт задачу | в репозитории потребителя |
| `scripts/sync_inbox.py` | то же самое напрямую, без действия — если прогонов GitHub нет | в репозитории потребителя |
| `scripts/link_trails.py` | обратная сторона следа: задача узнаёт, что породила правило | в репозитории потребителя |
| `scripts/main_red.py` | дежурный по общей ветке: одна задача, пока `main` красная | в репозитории потребителя |
| `uses: ArtVsMark/claude-code-playbook/.github/actions/attribution@<!--m:ref-->v1.1.0<!--/m:ref-->` | сверяет авторство коммитов со списком согласованных имён | в репозитории потребителя |

Версия в примерах закреплена тегом и подставляется сборкой, а не вписывается
руками ([035](rules/ru/035-version-is-never-edited-by-hand.md)): смотреть на неё надо в
[контракте](export/README.md), там же — поля выгрузки и правила эволюции схемы.

## Чего каталог не делает

- **не рассылает** — тянет потребитель, своим токеном и в свой трекер;
- **не пишет** в чужой репозиторий: набор подключения кладётся в папку, а
  дальше решает человек;
- **не заводит** копию генератора у каждого: реализация одна и живёт здесь.

## Когда копирование всё-таки уместно

Заготовки в [`templates/`](templates/README.md) — для того, у кого прогонов
GitHub нет или подключаться он не хочет: их **берут и правят**, а не копируют
целиком. И сами правила копировать целиком не надо: у каждой записи есть
раздел «Применимость», и половина заточена под агентские окна.

Порядок первого дня для нового проекта — [`START.md`](START.md); он начинается
с этой страницы.

---

## In English

**Connect with a command, not by copying.** The catalogue ships mechanisms, not
just rule texts: an onboarding command, a published action and ready-to-run
scripts. Copying by hand what a tool already assembles creates a second
implementation of one algorithm, and the first edit pulls them apart
([090](rules/en/090-shared-helpers-move-up-not-sideways.md)).

```
python scripts/onboard_consumer.py --repo owner/name --out FOLDER
```

It writes three files — the project's answer for every rule
(`.rules/bindings.json`), the channel back (`.rules/proposals.json`) and a
daily workflow with the catalogue tag pinned. A human carries them into the
repository: the catalogue never writes into anyone else's repo and never pushes
anything out — the consumer pulls, with their own token and into their own
tracker.

From then on one "inbox" issue is kept up to date: rules with no answer yet,
rules held by nothing here but **solved next door** (with the neighbour's
address), and answers about rules the catalogue no longer has.

The table above is the single list of tools; `README` and `START` link here
instead of keeping a second one. Templates in [`templates/`](templates/README.md)
are the fallback for a project that cannot run GitHub workflows — take and
adapt them, never copy wholesale.
