# Десять правил, с которых начать · Ten rules to start with

Каталог [на 125 записей](rules/README.md) читать подряд незачем. Здесь десять,
которые переносятся дальше своего стека: они про механику проверок, состояние и
доверие к находкам, а не про GitHub и агентские окна. Порядок — не по номеру, а
по тому, в каком порядке они начинают окупаться.

The [125-record catalogue](rules/README.md) is not meant to be read front to
back. These ten travel beyond the stack they came from: they are about the
mechanics of checks, about state, and about trusting your own findings — not
about GitHub and agent sessions. Ordered by when each starts paying off, not by
number.

## По-русски

1. **[002 · Правило без механизма — обещание, а не гарантия](rules/ru/002-rule-without-mechanism.md)**
   Требование, которое нельзя проверить машинно, соблюдаться не будет. Либо
   гейт, либо не пишите. Это мета-правило всего каталога: по нему проверяются
   остальные.
2. **[039 · У проверки три исхода, а не два](rules/ru/039-three-outcomes-not-two.md)**
   «Чисто», «нашли проблему» и «проверка не отработала» требуют разных действий.
   Третий исход различают по наличию результата, а не по коду возврата.
3. **[075 · Гейт, не нашедший предмета проверки, падает](rules/ru/075-a-guard-that-finds-nothing-must-fail.md)**
   Ноль файлов, ноль совпадений, отсутствующий раздел — это ошибка входа, а не
   «чисто». Зелёный на пустом входе — самый дорогой вид зелёного.
4. **[005 · Число, вписанное руками, устаревает молча](rules/ru/005-hand-written-numbers-rot.md)**
   Цифра в документации либо пересчитывается автоматически, либо её не должно
   быть. Устаревает она без единого признака.
5. **[049 · Состояние выводится из живых артефактов](rules/ru/049-derive-state-from-live-artifacts.md)**
   Кто что взял и что готово — вычисляется из веток и задач, а не ведётся
   файлом, который надо не забыть обновить. Вычисленное не может протухнуть.
6. **[044 · Премиса находки проверяется до фикса](rules/ru/044-check-the-premise-before-fixing.md)**
   Находка содержит утверждение о текущем состоянии. Оно проверяется первым
   действием — до планирования, до задачи, до кода.
7. **[037 · Находка не с той поверхности — гипотеза](rules/ru/037-finding-status-depends-on-window.md)**
   Дефект, найденный на подделке, не получает тяжести, пока не подтверждён на
   настоящей поверхности. Иначе отчёт растёт быстрее, чем продукт чинится.
8. **[068 · Список разрешённого, а не запрещённого](rules/ru/068-allowlist-not-denylist.md)**
   Запретительный список не знает о том, что появится завтра, и молча пропускает
   новое. Именно так утекают секреты.
9. **[034 · Зона одного исполнителя должна быть маленькой](rules/ru/034-small-zone-per-executor.md)**
   Роль дробится на двух-трёх, плану даётся не больше трёх пунктов. Большая зона
   гибнет целиком.
10. **[006 · Агентское окно живёт три–пять дней](rules/ru/006-window-lifetime.md)**
    Долгоживущая сессия дорожает и консервирует устаревшие правила. С числами:
    замер по живым сессиям есть в записи.

## In English

1. **[002 · A rule without a mechanism is a promise, not a guarantee](rules/en/002-rule-without-mechanism.md)**
   A requirement that cannot be checked by machine will not be followed. Either
   build a gate, or do not write it down. This is the catalogue's meta-rule: the
   others are judged against it.
2. **[039 · A check has three outcomes, not two](rules/en/039-three-outcomes-not-two.md)**
   "Clean", "found a problem" and "the check did not run" need different
   responses. The third is told apart by the presence of a result, not by an exit
   code.
3. **[075 · A guard that finds nothing must fail](rules/en/075-a-guard-that-finds-nothing-must-fail.md)**
   Zero files, zero matches, a missing section — that is bad input, not "all
   clear". Green on empty input is the most expensive kind of green.
4. **[005 · A number typed by hand goes stale in silence](rules/en/005-hand-written-numbers-rot.md)**
   A figure in documentation is either recomputed automatically, or it does not
   belong there. It rots without a single visible sign.
5. **[049 · Derive state from live artefacts](rules/en/049-derive-state-from-live-artifacts.md)**
   Who took what and what is ready is computed from branches and tasks, not kept
   in a file somebody has to remember to update. Computed state cannot go stale.
6. **[044 · Check the premise before fixing](rules/en/044-check-the-premise-before-fixing.md)**
   A finding contains a claim about the current state. That claim is verified as
   the first action — before planning, before the task, before code.
7. **[037 · A finding from the wrong surface is a hypothesis](rules/en/037-finding-status-depends-on-window.md)**
   A defect found against a fake gets no severity until it is confirmed on the
   real surface. Otherwise the report grows faster than the product gets fixed.
8. **[068 · Allowlist, not denylist](rules/en/068-allowlist-not-denylist.md)**
   A denylist knows nothing about what appears tomorrow and lets new things
   through in silence. That is exactly how secrets leak.
9. **[034 · One executor's zone must be small](rules/en/034-small-zone-per-executor.md)**
   Split a role across two or three executors and give each plan no more than
   three items. A large zone dies whole.
10. **[006 · An agent session lives three to five days](rules/en/006-window-lifetime.md)**
    A long-lived session grows expensive and preserves obsolete rules. With
    numbers: the record carries the measurement across live sessions.

---

Дальше: [`START.md`](START.md) — порядок первого дня · [`rules/`](rules/README.md) —
все 125 записей и вход по областям · [`templates/`](templates/README.md) —
исполняемые заготовки.

Next: [`START.md`](START.md) for day-one order · [`rules/`](rules/README.md) for
all 125 records and the by-area entry point · [`templates/`](templates/README.md)
for executable boilerplate.
