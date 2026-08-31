# Заготовки · Templates

Исполняемые заготовки к [каталогу правил](../rules/README.md). Каждая реализует
названные правила и содержит ссылки на них — чтобы было видно, **из какого
инцидента** взялась каждая строка.

Executable boilerplate for the [rule catalogue](../rules/README.md). Each one
implements the rules it names and links back to them, so you can see **which
incident** each line came from.

> **Берите и правьте, а не копируйте целиком.** Правило без своей истории не
> соблюдается — оно занимает место и создаёт видимость дисциплины. Это относится
> и к этим файлам.
>
> **Take and adapt, do not copy wholesale.** A rule without your own history
> behind it is not followed — it takes up space and creates the appearance of
> discipline. That applies to these files too.

## Что здесь · What is here

| Файл · File | Зачем · What for | Правила · Rules | У себя · At home |
|---|---|---|---|
| [`preflight.py`](preflight.py) | Гейт перед пушем одной командой: секреты, формат, линтер, типы, тесты · Pre-push gate in one command | [002](../rules/ru/002-rule-without-mechanism.md) · [039](../rules/ru/039-three-outcomes-not-two.md) · [068](../rules/ru/068-allowlist-not-denylist.md) · [075](../rules/ru/075-a-guard-that-finds-nothing-must-fail.md) · [100](../rules/ru/100-two-deadlines-start-and-work.md) | `scripts/preflight.py` |
| [`ci.yml`](ci.yml) | Конвейер: явные события, ручной запуск, матрица ОС, инварианты релиза · CI with explicit events, manual trigger, OS matrix | [104](../rules/ru/104-event-driven-automation-needs-a-manual-button.md) · [074](../rules/ru/074-one-shot-irreversible-steps-get-their-own-guard.md) · [018](../rules/ru/018-cloud-checks-nodes-local-checks-chain.md) · [041](../rules/ru/041-two-honest-numbers-beat-one-averaged.md) | `.github/workflows/ci.yml` |
| [`labels.yml`](labels.yml) | Метки, разделённые на содержание и конвейер · Labels split into content and pipeline | [064](../rules/ru/064-labels-are-machine-input-not-decoration.md) · [053](../rules/ru/053-queue-order-is-a-rule-not-arrival.md) · [065](../rules/ru/065-the-onramp-must-speak-the-newcomers-language.md) | `.github/labels.yml` |
| [`CLAUDE.md`](CLAUDE.md) | Свод проекта: триггеры и ссылки, без пересказа · Project rulebook: triggers and links | [029](../rules/ru/029-triggers-and-canon.md) · [022](../rules/ru/022-one-canonical-document.md) · [038](../rules/ru/038-window-name-declares-its-environment.md) | `CLAUDE.md` над ядром `AGENTS.md` |
| [`session-opening.md`](session-opening.md) | Стартовое сообщение окна: четыре раздела, контекст ссылками · Session opening message | [006](../rules/ru/006-window-lifetime.md) · [047](../rules/ru/047-rule-change-restarts-the-windows.md) · [091](../rules/ru/091-work-sources-are-ordered-first-non-empty-wins.md) | нет: договорённости окна живут в `CLAUDE.md`, отдельного стартового сообщения каталог не ведёт · no: they live in the rulebook |
| [`executor-brief.md`](executor-brief.md) | Задание параллельному исполнителю: числа и запреты · Brief for a parallel executor | [034](../rules/ru/034-small-zone-per-executor.md) · [061](../rules/ru/061-environment-bans-belong-in-the-task.md) · [117](../rules/ru/117-numeric-limits-belong-in-the-task-spec.md) | нет: параллельных исполнителей у каталога не бывает, работу ведёт одно окно · no: a single session does the work |
| [`adr-template.md`](adr-template.md) | Запись решения: контекст, альтернативы, последствия · Decision record | [042](../rules/ru/042-decision-records-its-alternatives.md) · [043](../rules/ru/043-decisions-are-superseded-not-edited.md) · [094](../rules/ru/094-a-compatibility-shim-makes-migration-permanent.md) | нет: решения каталога живут записями правил и задачами · no: rules and issues carry them |
| [`audit-document.md`](audit-document.md) | Документ аудита: находки, вердикты, условие архивации · Audit document | [019](../rules/ru/019-audit-from-surfaces-not-files.md) · [037](../rules/ru/037-finding-status-depends-on-window.md) · [086](../rules/ru/086-the-finder-does-not-grade-the-finding.md) · [121](../rules/ru/121-closing-the-container-is-not-closing-the-work.md) | нет: самоаудит был разовым, находки разошлись по задачам · no: the audit was one-off |
| [`bindings.json`](bindings.json) | Ответ проекта каталогу: что он сделал с каждым правилом и чем оно здесь держится · A project's answer to the catalogue | [129](../rules/ru/129-a-catalogue-needs-a-consumption-contract.md) · [026](../rules/ru/026-rejected-findings-must-be-recorded.md) · [113](../rules/ru/113-a-contract-states-how-it-may-change.md) | `.rules/bindings.json` |
| [`proposals.json`](proposals.json) | Обратный канал: правила, родившиеся у потребителя и предлагаемые каталогу · The consumer's channel back: rules born there | [080](../rules/ru/080-every-new-rule-goes-into-the-catalogue.md) · [129](../rules/ru/129-a-catalogue-needs-a-consumption-contract.md) | `.rules/proposals.json` |
| [`rule-template.md`](rule-template.md) | Запись правила в каталог · A catalogue entry | [120](../rules/ru/120-how-to-run-a-rule-catalogue.md) · [080](../rules/ru/080-every-new-rule-goes-into-the-catalogue.md) | `rules/ru/` — сверяется `scripts/audit_catalogue.py` |
| [`candidate-template.md`](candidate-template.md) | Кандидат в правило: наблюдение из чужого проекта без своего инцидента · Rule candidate | [026](../rules/ru/026-rejected-findings-must-be-recorded.md) · [080](../rules/ru/080-every-new-rule-goes-into-the-catalogue.md) | `candidates/` |

Порядок подключения — по цене ошибки: [`START.md`](../START.md).
Order of adoption, sorted by cost of getting it wrong: [`START.md`](../START.md).

## Как адаптировать

1. **Выкиньте то, чего у вас нет.** Пункт про матрицу трёх ОС бессмыслен в
   проекте под одну платформу, а правило, которое не применяется, обесценивает
   соседние.
2. **Оставьте ссылки на правила.** Через месяц никто не вспомнит, почему шаг
   стоит именно здесь, — а по ссылке видно инцидент.
3. **Замените плейсхолдеры `<…>` фактами своего проекта**, а не общими словами:
   «бюджет обращений 25» работает, «экономно» — нет.
4. **Заведите свой каталог** и записывайте туда свои инциденты. Чужой свод,
   перенесённый целиком, не соблюдается.

## How to adapt

1. **Throw out what you do not have.** A three-OS matrix means nothing in a
   single-platform project, and a rule that never applies devalues the ones next
   to it.
2. **Keep the links to the rules.** In a month nobody will remember why a step is
   there — the link shows the incident.
3. **Replace the `<…>` placeholders with facts from your project**, not with
   generalities: "tool-call budget 25" works, "be economical" does not.
4. **Start your own catalogue** and write your own incidents into it. Somebody
   else's rulebook, transplanted whole, is not followed.
