#!/usr/bin/env python3
"""Собирает таблицу «где действует правило» из ответов потребителей.

Путь «проект → каталог» держится правилом 080 и работает. Путь «каталог →
проект» не держался ничем: правило, родившееся в одном проекте, для остальных
не существовало — не «отклонено», не «неприменимо», а просто отсутствовало, и
отличить это от рассмотренного решения было нельзя ни в одном репозитории.

Здесь собирается вторая половина: ответы потребителей читаются по обычному
HTTPS, без API и без клона, и сводятся в одну таблицу.

Реализует правила каталога:
  120 — обратный указатель каталога собирается из ответов проектов, а не
        ведётся списком: сводка «где действует» это производное от них;
  129 — контракт потребления: ответ имеет форму, и она проверяется;
  049 — таблица вычисляется из ответов, а не ведётся руками;
  075 — объявленный потребитель, чей ответ не читается, — отказ, а не молчание;
  027 — «не подключён» и «неизвестно» это состояния, и они печатаются;
  046 — чего механизм не знает, названо прямо, а не сглажено;
  039 — три исхода, а не два;
  004 — расхождение ответа потребителя — штатное состояние сводки, а не авария прогона;
  016 — длинный список находок обрезается с маркером обрыва, а не молча;
  079 — срок свежести ответа считается от успешного чтения, а не от объявления потребителя;
  096 — .rules разведён по жизненному циклу: реестр, ответ, предложения и набор витрины — разные файлы;
  146 — обязательная проверка сверяет сводку с ОТВЕТОМ на диске, а не саму с собой;
  164 — номер версии говорит, чего он версия: расхождение версий формата у
        потребителей и у своей заготовки называется на КАЖДОМ изменении;
  157 — версия ответа потребителя сверяется с версией ответа каталога, а не
        с константой в коде: обе стороны такого сравнения были бы нашими;
  174 — сводка export/where.json собирается издателем и читается потребителями:
        считать её у себя значило бы держать копию нашего определения.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.

Сеть нужна только сборке. Проверка ходит по диску намеренно: обязательный гейт
изменения не должен зависеть от чужого сервера — иначе сетевой сбой красит
чужую работу и останавливает автомерж. Свежесть сводки держит отдельный прогон
по расписанию, у него другой предмет и другая цена красного.

Запуск:  python scripts/aggregate_bindings.py            # собрать, нужна сеть
         python scripts/aggregate_bindings.py --check    # сверить, сеть не нужна
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Словарь механизмов живёт в одном месте (правило 022). Импорт, а не копия:
# копия расходится молча, и первым это увидит потребитель, а не гейт.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_bindings import MECHANISM_ORDER, addressed  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONSUMERS = ROOT / ".rules" / "consumers.json"
EXPORT_JSON = ROOT / "export" / "where.json"
EXPORT_MD = ROOT / "export" / "where.md"
RULES = ROOT / "export" / "rules.json"

#: Сколько дней ответ потребителя считается свежим. Срок отсчитывается от
#: успешного чтения, а не от «когда собирались» (правило 079).
TTL_DAYS = 30

#: Состояния потребителя в таблице. «Не подключён» и «неизвестно» — разные
#: вещи, и путать их значит выдавать незнание за отказ (правило 027).
#: Сколько дней объявленный потребитель может не подключаться, прежде чем
#: «не подключён» перестанет быть состоянием и станет находкой.
#:
#: ПОЧЕМУ У ЭТОГО СОСТОЯНИЯ ДОЛЖЕН БЫТЬ СРОК. Замер: из шести объявленных
#: потребителей пятеро не отдают ответа, шестеро не отдают предложений. Канал
#: построен с обеих сторон и не пронёс НИ ОДНОГО предложения. «Не подключён»
#: при этом — законное состояние, печатается спокойно, и потому не читается
#: никем: у него нет адресата, ровно как у красного по расписанию (142).
#:
#: Срок делает адресата: после него состояние становится отказом СЕТЕВОГО
#: прогона, а тот заводит задачу. На изменении это остаётся списком без
#: отказа — автор изменения чужой репозиторий подключить не может, и красить
#: его работу за это значит приучать к красному (051).
UNCONNECTED_DAYS = 30
NOT_CONNECTED = "не подключён"
UNKNOWN = "неизвестно"

STATUS_RU = {
    "active": "действует",
    "rejected": "отклонено",
    "not-applicable": "нет предмета",
    "unreviewed": "не рассмотрено",
}


def fetch(url: str, timeout: int = 20) -> tuple[dict | None, str | None]:
    """Ответ потребителя по обычному HTTPS: без API, без токена, без клона."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except (urllib.error.URLError, OSError) as e:
        return None, f"не прочитан: {e}"
    except ValueError as e:
        return None, f"прочитан, но не разобран: {e}"


def read_local(path: str) -> tuple[dict | None, str | None]:
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8")), None
    except (OSError, ValueError) as e:
        return None, f"не прочитан: {e}"


def collect(consumers: list[dict]) -> tuple[list[dict], list[str]]:
    """Читает ответ каждого потребителя. Возвращает срезы и находки."""
    slices: list[dict] = []
    problems: list[str] = []
    today = dt.date.today().isoformat()

    for c in consumers:
        repo, source = c.get("repo"), c.get("bindings")
        entry: dict = {"repo": repo, "role": c.get("role", "")}

        if not source:
            # Объявлено, что связи нет. Это состояние, а не пробел в данных.
            entry["state"] = UNKNOWN if c.get("access") == "private" else NOT_CONNECTED
            entry["why"] = ("ответ приватен и публично недоступен"
                            if c.get("access") == "private"
                            else "ответ потребителя ещё не заведён")
            if c.get("since"):
                entry["since"] = c["since"]
            slices.append(entry)
            continue

        data, err = (read_local(source) if not source.startswith("http")
                     else fetch(source))
        if err:
            # Потребитель объявлен и обещал ответ. Молчать об этом нельзя:
            # молчание неотличимо от «у него всё в порядке» (правило 075).
            problems.append(f"{repo}: {source} {err}")
            entry["state"] = UNKNOWN
            entry["why"] = err
            slices.append(entry)
            continue

        rules = data.get("rules", {})
        by_status: dict[str, int] = {}
        by_mechanism: dict[str, int] = {}
        holds: dict[str, dict] = {}
        for rid, rec in rules.items():
            st = rec.get("status", "?")
            by_status[st] = by_status.get(st, 0) + 1
            if st != "active":
                continue
            # `mechanism` отсутствует и `mechanism: none` — одно и то же
            # состояние: правило признано действующим и не держится ничем.
            # Разводить их значило бы делать вид, что второе хуже первого.
            mech = rec.get("mechanism") or "none"
            by_mechanism[mech] = by_mechanism.get(mech, 0) + 1
            holds[rid] = {"mechanism": mech, "where": rec.get("where") or ""}
        entry["schema"] = data.get("schema") or ""
        entry["state"] = "подключён"
        # ЭТО ПОЛЕ МЕНЯЕТСЯ КАЖДЫМ ПРОГОНОМ САМО ПО СЕБЕ — см. VOLATILE ниже.
        entry["read_at"] = today
        entry["answered"] = len(rules)
        entry["by_status"] = by_status
        entry["by_mechanism"] = by_mechanism
        entry["rules"] = {rid: rec.get("status") for rid, rec in rules.items()}
        entry["holds"] = holds
        slices.append(entry)

    return slices, problems


def unconnected(consumers: list[dict]) -> list[str]:
    """Объявленные, но так и не подключившиеся дольше срока.

    Приватный потребитель сюда не попадает: его ответ недоступен по объявленной
    причине, и требовать подключения значило бы требовать невозможного.
    """
    out: list[str] = []
    today = dt.date.today()
    for c in consumers:
        if c.get("bindings") or c.get("access") == "private":
            continue
        since = c.get("since")
        if not since:
            out.append(f"{c.get('repo')}: объявлен потребителем, ответа нет, и "
                       "с какого дня — не сказано. Поле since называет начало "
                       "отсчёта, без него срок не считается")
            continue
        try:
            days = (today - dt.date.fromisoformat(since)).days
        except ValueError:
            out.append(f"{c.get('repo')}: since не разбирается — {since!r}")
            continue
        if days > UNCONNECTED_DAYS:
            out.append(f"{c.get('repo')}: объявлен потребителем {days} дн. назад, "
                       "ответа так и нет. Либо подключить, либо убрать из реестра — "
                       "объявленный и молчащий потребитель делает сводку шире "
                       "правды")
    return out


def stale(slices: list[dict]) -> list[str]:
    """Отставший потребитель — предупреждение по сроку, а не отказ (079)."""
    out: list[str] = []
    today = dt.date.today()
    for s in slices:
        read_at = s.get("read_at")
        if not read_at:
            continue
        try:
            age = (today - dt.date.fromisoformat(read_at)).days
        except ValueError:
            continue
        if age > TTL_DAYS:
            out.append(f"{s['repo']}: ответ читался {age} дн. назад")
    return out



#: Поля сводки, которые меняются САМИ ПО СЕБЕ, без изменения данных. Дата
#: последнего чтения — это «когда мы спросили», а не «что нам ответили».
#:
#: ЗАЧЕМ ЭТО ОБЪЯВЛЕНО ЗДЕСЬ. Знание жило неявно и вбок: прогон сверял только
#: `where.md`, потому что даты в ней нет, — и `where.json` тихо отставал на
#: дату у каждого коммита. Стоило это одной ловушки: автоматическая пересборка,
#: сравнивая файл целиком, заводила бы изменение КАЖДЫЙ ДЕНЬ, ничего при этом
#: не меняя, и приучила бы пролистывать эти изменения не глядя (правило 051).
#: Список читает `refresh_derived.py` — импортом, а не копией (022).
VOLATILE = ("read_at",)

#: Как механизм называется по-человечески. `none` сюда не попадает: он не
#: механизм, а его отсутствие, и в разделе «чем держат» ему нечего сказать.
#: `process-step` попадает — его ещё отдают потребители, и назвать его в
#: отчёте «шагом процесса» честнее, чем молча приравнять к одному из новых.
MECHANISM_RU = {"gate": "гейт", "pipeline": "конвейер", "document": "документ",
                "process-step": "шаг процесса"}

#: Колонки «чем держится» и порядок показа. Канон один — `check_bindings.py`;
#: здесь он импортируется, а не переписывается: две классификации одной
#: территории расходятся молча (правило 022).
MECHANISM_COLUMNS = MECHANISM_ORDER

#: Заголовок колонки. Двуязычный, как и вся таблица.
MECHANISM_HEAD = {
    "gate": "Гейтом · Gate",
    "pipeline": "Конвейером · Pipeline",
    "document": "Документом · Document",
    "none": "Ничем · Nothing",
    "process-step": "Шагом · Step",
}


#: Что в поле `where` считается АДРЕСОМ механизма. Поле — свободная проза, и
#: разбирать её целиком нельзя; путь к файлу — единственное, что в ней имеет
#: одинаковый смысл у всех потребителей.
ADDRESS_RE = re.compile(r"[\w./-]+\.(?:py|yml|yaml|md|toml|cfg|json)")

#: Со скольких удержанных правил механизм попадает в раздел поимённо. Один —
#: это ещё не нагрузка, а список из тридцати семи строк на потребителя никто
#: не дочитает; сколько таких, говорится числом.
LOAD_MIN = 2


def _load_bearing(connected: list[dict]) -> list[str]:
    """Сколько правил держит каждый механизм — и какой держит больше всех.

    ЗАЧЕМ. «Чем держат другие» отвечает, кто решил задачу; этот раздел —
    насколько дорого решение стоит перенимать. Замер: у витрины
    `scripts/build_metrics.py` держит двадцать два правила, у каталога самый
    нагруженный механизм — шесть. Один файл на двадцать два правила это и
    готовый образец, и точка отказа: сводка называет обе стороны числом, а
    выводы делает человек.

    ГРАНИЦА. Считается ПУТЬ, найденный в свободном поле `where`, а не сам
    механизм: поле — проза, и у половины записей пути в нём нет вовсе. Сколько
    таких, печатается рядом — иначе доля выглядела бы как полнота (046).
    """
    lines = ["", "## Сколько держит механизм · How much each mechanism holds", ""]
    rows: list[str] = []
    for s in connected:
        name = s["repo"].split("/")[-1]
        holders = [h for h in (s.get("holds") or {}).values()
                   if h.get("mechanism") != "none"]
        counted: dict[str, int] = {}
        named = 0
        for h in holders:
            found = set(ADDRESS_RE.findall(h.get("where") or ""))
            if found:
                named += 1
            for a in found:
                counted[a] = counted.get(a, 0) + 1
        if not holders:
            continue
        top = sorted(((n, a) for a, n in counted.items() if n >= LOAD_MIN),
                     key=lambda x: (-x[0], x[1]))
        singles = sum(1 for n in counted.values() if n < LOAD_MIN)
        for n, a in top:
            rows.append(f"| `{name}` | `{a}` | {n} |")
        rows.append(
            f"| `{name}` | _остальные_ · _the rest_ | "
            f"{singles} механизмов по одному правилу; без названного адреса: "
            f"{len(holders) - named} из {len(holders)} |")
    if not rows:
        lines += ["Подключённых потребителей с построенными механизмами пока нет.",
                  "", "No connected consumer has a mechanism in place yet."]
        return lines
    lines += [
        "> Считается путь к файлу, найденный в поле `where` ответа потребителя. "
        "Механизм, держащий много правил, — это и образец, и точка отказа.",
        "",
        "> Counted by the file path found in the consumer's `where` field. A "
        "mechanism holding many rules is both a model to copy and a single "
        "point of failure.",
        "",
        "| Проект · Project | Механизм · Mechanism | Держит правил · Rules held |",
        "|---|---|---|",
    ] + rows
    return lines


def _how_others_enforce(connected: list[dict]) -> list[str]:
    """Правила, которые у одного держатся, а у другого — ничем.

    ЗАЧЕМ ЭТОТ РАЗДЕЛ. Сводка отвечала «действует ли правило у проекта» и
    молчала о том, ЧЕМ. Замер по трём подключённым: правил, объявленных
    действующими и не обеспеченных ничем, — семьдесят два. При этом у сорока
    из них кто-то из соседей уже построил механизм и назвал его адрес. Это
    готовый ответ, который до сих пор нельзя было увидеть, не открыв три
    файла в трёх репозиториях.

    ГРАНИЦА. Раздел не утверждает, что чужой механизм подойдёт: стеки разные,
    и «у соседа это гейт» не значит «у нас должен быть такой же». Он отвечает
    ровно на один вопрос — кто уже сталкивался и чем закрыл.

    Правила, которые не держатся НИ У КОГО, сюда не попадают намеренно: учиться
    там не у кого, и их очередь — метрика `check_bindings.py`.
    """
    held: dict[str, list[tuple[str, str, str]]] = {}
    unheld: dict[str, list[str]] = {}
    for s in connected:
        name = s["repo"].split("/")[-1]
        for rid, h in (s.get("holds") or {}).items():
            if h.get("mechanism") == "none":
                unheld.setdefault(rid, []).append(name)
            else:
                held.setdefault(rid, []).append(
                    (name, h.get("mechanism", ""), h.get("where", "")))
    both = sorted(set(held) & set(unheld))
    lines = ["", "## Чем держат другие · How others enforce it", ""]
    if not both:
        lines += [
            "Правил, которые у одного держатся механизмом, а у другого не "
            "держатся ничем, сейчас нет.",
            "",
            "No rule is currently held by a mechanism in one project and by "
            "nothing in another.",
        ]
        return lines
    lines += [
        "> Слева — тот, у кого механизм есть, и его адрес. Справа — у кого это "
        "правило признано действующим и не обеспечено ничем.",
        "> Чужой механизм не обязан подойти: стеки разные. Раздел отвечает на "
        "один вопрос — кто уже сталкивался и чем закрыл.",
        "",
        "> On the left, whoever holds the rule and where. On the right, whoever "
        "calls it active but holds it by nothing.",
        "",
        "| № | Держит · Held by | Ничем · By nothing |",
        "|---|---|---|",
    ]
    for rid in both:
        by = "; ".join(
            f"`{name}` — {MECHANISM_RU.get(mech, mech)}: {where}" if where
            else f"`{name}` — {MECHANISM_RU.get(mech, mech)}"
            for name, mech, where in held[rid])
        lines.append(f"| {rid} | {by} | " + ", ".join(f"`{n}`" for n in unheld[rid]) + " |")
    return lines


def origin_counts(rules: list[dict]) -> dict[str, int]:
    """Сколько правил каталога РОДИЛОСЬ у каждого репозитория.

    Это третье число рядом с «разобрано» и «связей», и оно отвечает на другой
    вопрос: те два про то, как проект каталог ПОТРЕБЛЯЕТ, это — про то, чем он
    его наполнил. Каталог общий, но растёт неравномерно, и кто именно его
    наполняет, не было видно нигде (задача #192).

    СЧИТАЕТСЯ ПО ПОЛЮ `origin`, А НЕ ПО СЛЕДАМ. След ведёт туда, где поломка
    ВИДНА, а не туда, где она случилась; у части записей следов на задачи нет
    вовсе, а у некоторых их несколько и родителя по ним не выбрать. Замер на
    момент заведения поля: следы были у 64 записей из 152 — метрика по ним
    оказалась бы догадкой, выданной за выборку.
    """
    out: dict[str, int] = {}
    for r in rules:
        repo = r.get("origin")
        if repo:
            out[repo] = out.get(repo, 0) + 1
    return out


def trail_counts(rules: list[dict]) -> dict[str, int]:
    """Сколько следов каталога ведёт в каждый репозиторий.

    След — раздел записи, называющий задачу или артефакт у потребителя. До сих
    пор он был виден только внутри правила, и вопрос «сколько наших правил
    выросло у грейдера» требовал ручного пересчёта ста сорока семи файлов.

    Считается по ЭКСПОРТУ, а не разбором Markdown: разбор прозы дал бы вторую
    интерпретацию той же территории. Репозиторий, у которого следов нет, здесь
    отсутствует — ноль подставляет вызывающий, чтобы «нет следов» и «нет
    потребителя» не слились.
    """
    out: dict[str, int] = {}
    for r in rules:
        for t in r.get("trails") or []:
            repo = t.get("repo")
            if repo:
                out[repo] = out.get(repo, 0) + 1
    return out


def schema_lag(slices: list[dict], own: str) -> list[str]:
    """Потребители, чей ответ отвечает по версии старше нашей.

    ПОЧЕМУ ЭТО НАДО ГОВОРИТЬ ВСЛУХ. Совместимость по формату маскирует
    расхождение по смыслу: расколотое слово продолжает читаться, просто теперь
    оно означает «мы не ответили». Издатель при этом видит колонку нулей и
    читает её как «у него так устроено», а потребитель видит свой файл
    валидным. Ни одна сторона не видит причины, пока кто-то не спросит вслух —
    именно так это и вскрылось у грейдера, вопросом владельца (правило 157).

    Замер, ради которого правило приехало: 52 ответа из 153 стояли словом
    `process-step`, расколотым в версии 1.1, и гейт потребителя был зелёным —
    он сравнивал свою версию со своей же константой.

    ГРАНИЦА. Отсюда не чинится: файл чужой. Поэтому находка живёт рядом с
    лишними ответами, в разделе «правится не здесь», и прогон от неё не
    краснеет.
    """
    out: list[str] = []
    for s in slices:
        if not s.get("rules"):
            continue
        theirs = s.get("schema") or ""
        if not theirs:
            out.append(f"{s['repo']}: ответ не называет версию схемы — "
                       "подъём контракта у нас он не заметит")
        elif theirs != own:
            out.append(f"{s['repo']}: ответ по схеме {theirs}, у контракта {own} — "
                       "записи остаются валидными, означая уже другое")
    return out


def _schema_of(path: Path) -> str:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("schema") or ""
    except (OSError, ValueError):
        return ""


def schema_findings(slices: list[dict]) -> tuple[list[str], list[str]]:
    """Расхождения версий ФОРМАТА: у потребителей и у своей заготовки.

    ВЕРСИЯ БЕРЁТСЯ У ИЗДАТЕЛЯ, А НЕ ИЗ КОНСТАНТЫ. Каталог — такой же
    потребитель (129), и его собственный ответ по определению стоит на текущей
    версии; сравнивать с числом в коде значило бы повторить ту самую ошибку,
    из-за которой правило и приехало (157).

    ЗАЧЕМ ЭТО ЗДЕСЬ, А НЕ ТОЛЬКО В СЕТЕВОМ ПРОГОНЕ. Данных хватает на диске:
    версия каждого ответа лежит в собранной сводке. Раньше находка считалась
    только сетевым прогоном и потому появлялась раз в сутки — собрано и никому
    не доставлено, ровно то, о чём 142. Замер, которым это вскрылось: у одного
    потребителя ответ объявлял версию ВЫШЕ нашей — в его файл попал номер
    схемы ВЫГРУЗКИ вместо номера схемы ОТВЕТА, — а у другого на версию ниже, и
    ни то ни другое ни один прогон на изменении не называл.

    Возвращает две половины: чужое (правится не здесь) и своё (правится здесь).
    """
    own = _schema_of(ROOT / ".rules" / "bindings.json")
    if not own:
        return [], []
    свои: list[str] = []
    tpl = _schema_of(ROOT / "templates" / "bindings.json")
    if tpl and tpl != own:
        свои.append(
            f"templates/bindings.json: заготовка ответа объявляет схему {tpl}, "
            f"а ответ каталога — {own}. Образец, который раздают, отстал от "
            "того, что применяется дома (155, 157)")
    return schema_lag(slices, own), свои


def stale_answers(slices: list[dict], rule_ids: list[str],
                  superseded: dict[str, str] | None = None) -> list[str]:
    """Ответы потребителей о правилах, которых в каталоге НЕТ.

    ЭТО НАХОДКА, А НЕ ОЧЕРЕДЬ. Нерассмотренное правило — состояние: решение
    ещё не принято, и оно примется. Ответ о несуществующем правиле не
    рассосётся сам: он останется ровно таким, пока его кто-нибудь не удалит.

    ЧЕМ ЭТО ОПАСНО ИМЕННО ЗДЕСЬ. Потребители ключуются по НОМЕРУ, а не по
    слагу. Пока номер свободен, лишний ответ — мусор; как только номер займёт
    новая запись, тот же ответ начнёт читаться как решение по ней, и не
    покраснеет ничто: статус есть, механизм назван, гейт полноты зелен.
    Каталог сообщит «потребитель держит правило NNN вот здесь» о записи,
    которой тот не видел.

    ПОЧЕМУ ЭТОГО НЕ БЫЛО. У СЕБЯ каталог такой ответ отвергает — это
    `check_bindings.py`, «ответ есть, а правила такого в каталоге нет».
    У потребителей тот же вопрос не задавался вовсе: число печаталось в
    отчёте и ни к чему не вело. Замер: у витрины лежит ответ о правиле 143,
    удалённом как дубль, и лежит он с самого удаления.

    ГРАНИЦА. Отсюда нельзя починить: файл чужой. Поэтому находка живёт в
    СЕТЕВОМ прогоне, у которого есть адресат, а на изменении печатается
    предупреждением — красить чужую работу за чужой файл значит приучать к
    красному (051).
    """
    known = set(rule_ids)
    superseded = superseded or {}
    out: list[str] = []
    for s in slices:
        extra = sorted(set(s.get("rules") or {}) - known)
        if extra:
            out.append(f"{s['repo']}: отвечает о правилах, которых в каталоге "
                       f"нет — {', '.join(extra)}. Номер не переиспользуется, "
                       "но и ответ о снятом правиле не должен лежать: заняв "
                       "номер, новая запись унаследует чужое решение молча")
        out += unaddressed(s)
        out += answers_superseded(s, superseded)
    return out


def superseded_map() -> dict[str, str]:
    """Заменённые правила из выгрузки: номер → номер смены. Пусто — законно.

    Читается из `export/rules.json`, а не выводится заново разбором записей:
    вторая интерпретация той же территории разошлась бы молча (022).
    """
    try:
        doc = json.loads(RULES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {r["id"]: r["superseded_by"] for r in doc.get("rules", [])
            if r.get("superseded_by")}


def answers_superseded(s: dict, superseded: dict[str, str]) -> list[str]:
    """Потребитель отвечает о ЗАМЕНЁННОМ правиле. Состояние, а не находка.

    Заменённая запись остаётся в выгрузке и остаётся действующей — значит в
    «лишние» такой ответ не попадёт и не должен: потребитель отвечает о том,
    что было, и упрекать его не в чем. Но и молчать нельзя: он не знает, что
    появилась смена, а узнать может только отсюда.

    ГРАНИЦА. Это НЕ упрёк и не очередь каталога: переносить ответ или нет,
    решает потребитель. Печатается рядом с чужими находками по той же причине —
    отсюда не чинится (051, 053).
    """
    answers = s.get("rules") or {}
    было = sorted(rid for rid in answers if rid in superseded)
    if not было:
        return []
    пары = ", ".join(f"{rid} → {superseded[rid]}" for rid in было)
    return [f"{s['repo']}: отвечает о заменённых правилах — {пары}. Это "
            "состояние, а не находка: ответ верен для того, что было. "
            "Перенести его или нет, решает потребитель"]


def unaddressed(s: dict) -> list[str]:
    """Механизмы потребителя, у которых назван не адрес, а рассказ.

    ТО ЖЕ ТРЕБОВАНИЕ, ЧТО У СЕБЯ. `check_bindings.py` отвергает свой ответ, в
    котором «держится гейтом» сказано без адреса: механизм, который нельзя
    открыть, проверить нечем. У потребителей тот же вопрос не задавался — и
    ровно поэтому раздел «чем держат другие» иногда предлагал соседу вместо
    решения пересказ.

    ГРАНИЦА — ТА ЖЕ, ЧТО У ЛИШНЕГО ОТВЕТА. Отсюда не чинится: файл чужой.
    Поэтому находка едет адресату, а прогон от неё не краснеет (051, 053).
    Существование файла здесь не проверяется вовсе: чужого дерева у нас нет,
    и утверждать о нём мы можем только то, что видно в ответе.
    """
    out: list[str] = []
    bad = sorted(rid for rid, h in (s.get("holds") or {}).items()
                 if h.get("mechanism") not in (None, "", "none")
                 and not addressed(h.get("where") or ""))
    if bad:
        shown = ", ".join(bad[:8]) + (f" и ещё {len(bad) - 8}" if len(bad) > 8 else "")
        out.append(f"{s['repo']}: механизм назван, а адреса нет — {shown}. "
                   "Открыть такой механизм нечем, и соседу он достаётся "
                   "пересказом вместо решения")
    return out


def census(slices: list[dict], rule_ids: list[str]) -> list[str]:
    """Сколько правил сейчас и сколько из них разобрано — по каждому.

    Печатается КАЖДЫМ прогоном, а не только красным. Число, которое видно
    лишь при поломке, отвечает на вопрос «что сломалось», но не на вопрос
    «куда мы движемся»; второй здесь и есть предмет.
    """
    known = set(rule_ids)
    out = [f"правил в каталоге: {len(known)}"]
    for s in slices:
        answers = s.get("rules")
        if answers is None:
            out.append(f"  {s['repo']}: {s.get('state')} — {s.get('why', '')}")
            continue
        by = s.get("by_status") or {}
        mech = s.get("by_mechanism") or {}
        out.append(
            f"  {s['repo']}: разобрано {len(known & set(answers)) - by.get('unreviewed', 0)}"
            f" из {len(known)} · не рассмотрено {by.get('unreviewed', 0)}"
            f" · без ответа {len(known - set(answers))}"
            f" · лишних {len(set(answers) - known)}"
            f" · действует {by.get('active', 0)} (ничем {mech.get('none', 0)})")
    return out


def as_markdown(slices: list[dict], rule_ids: list[str]) -> str:
    """Таблица «где действует». Файл производный и руками не правится."""
    lines = [
        "# Где действует правило · Where a rule applies",
        "",
        "> **Этот файл собирается скриптом** `scripts/aggregate_bindings.py` из",
        "> ответов потребителей и не правится руками. Пустая клетка означает, что",
        "> потребитель не подключён, а не что правило им отклонено.",
        "",
        "> **This file is generated** by `scripts/aggregate_bindings.py` from the",
        "> consumers' answers and is never edited by hand. An empty cell means the",
        "> consumer is not connected, not that the rule was rejected there.",
        "",
        "## Потребители · Consumers",
        "",
    ]
    # КОЛОНКИ СОБИРАЮТСЯ ИЗ ДАННЫХ, А НЕ ВПИСАНЫ РУКОЙ. Устаревшее слово
    # показывается ровно пока им кто-то отвечает: вписанная колонка `Шагом`
    # жила бы и после того, как последний потребитель перешёл, а вычеркнуть её
    # было бы некому (правило 049 — вычисляемое состояние протухает молча).
    seen = {k for s in slices for k, v in (s.get("by_mechanism") or {}).items() if v}
    cols = list(MECHANISM_COLUMNS) + [
        m for m in ("process-step",) if m in seen]
    head = " | ".join(MECHANISM_HEAD[m] for m in cols)
    lines += [
        "| Проект · Project | Состояние · State | Следов · Trails | "
        "Родил · Born | "
        "Ответов · Answers | Без ответа · Unanswered | Лишних · Stale | "
        f"Действует · Active | {head} | Механизмов · Mechanisms | Почему · Why |",
        "|" + "---|" * (9 + len(cols)),
    ]
    known = set(rule_ids)
    for s in slices:
        answered = s.get("answered")
        m = s.get("by_mechanism") or {}
        answers = s.get("rules") or {}
        if s.get("rules") is None:
            cells = ["—"] * (4 + len(cols))
        else:
            # ЛИШНИЙ ОТВЕТ — ЭТО НАХОДКА, А НЕ ОКРУГЛЕНИЕ. Витрина отвечала за
            # сто сорок восемь правил при ста сорока семи в экспорте: ответ
            # остался от удалённой записи. Разница пряталась в одном числе
            # «ответов», и увидеть её можно было только вычитанием в уме.
            cells = [
                str(len(known - set(answers))),
                str(len(set(answers) - known)),
                str((s.get("by_status") or {}).get("active", 0)),
                *(str(m.get(k, 0)) for k in cols),
                str(len({a for h in (s.get("holds") or {}).values()
                         if h.get("mechanism") != "none"
                         for a in ADDRESS_RE.findall(h.get("where") or "")})),
            ]
        # ТОЛЬКО ИМЯ ПРОЕКТА. Владелец у всех строк один и тот же, и в таблице
        # из двенадцати колонок он занимает место, не различая ни одной. Ниже,
        # в таблице правил, имя и так короткое — две записи об одном предмете
        # обязаны выглядеть одинаково (022).
        lines.append(
            f"| `{s['repo'].split('/')[-1]}` | {s['state']} | {s.get('trails', 0)} | "
            f"{s.get('born', 0)} | "
            f"{answered if answered is not None else '—'} | "
            + " | ".join(cells) + f" | {s.get('why', '')} |")

    connected = [s for s in slices if s.get("rules")]
    if not connected:
        lines += [
            "",
            "## Правила · Rules",
            "",
            "Подключённых потребителей, кроме самого каталога, пока нет — таблицы по",
            "правилам не будет, и это объявленное состояние, а не пустой файл.",
            "",
            "No connected consumers yet beyond the catalogue itself: there is no",
            "per-rule table, and that is a declared state rather than an empty file.",
        ]
        return "\n".join(lines) + "\n"

    lines += _how_others_enforce(connected)
    lines += _load_bearing(connected)

    head = " | ".join(f"`{s['repo'].split('/')[-1]}`" for s in connected)
    lines += ["", "## Правила · Rules", "",
              f"| № | {head} |", "|---" * (len(connected) + 1) + "|"]
    for rid in rule_ids:
        cells = " | ".join(STATUS_RU.get(s["rules"].get(rid), "—") for s in connected)
        lines.append(f"| {rid} | {cells} |")
    return "\n".join(lines) + "\n"


def check_offline(consumers: list[dict], rule_ids: list[str]) -> int:
    """Сверка без сети: сводка на диске согласована и покрывает весь реестр.

    Сюда не ходят наружу сознательно. Обязательная проверка изменения не должна
    зависеть от чужого сервера: сетевой сбой покрасил бы чужую работу и
    остановил автомерж, а предмет у этой проверки другой — «собрано ли то, что
    лежит», а не «что сейчас у потребителей».

    МЕСТНЫЕ ОТВЕТЫ СВЕРЯЮТСЯ ЗДЕСЬ ЖЕ, И РАНЬШЕ ЭТОГО НЕ БЫЛО. Проверка
    убеждалась, что реестр покрыт и что markdown отвечает json, — то есть что
    сводка согласована САМА С СОБОЙ. Ответ каталога о себе при этом мог уехать
    вперёд молча: изменение правит `.rules/bindings.json`, сводку не
    пересобирает, гейт зелен. Так и вышло (#122): ответ по 097 стал
    «действует», в сводке осталось «не рассмотрено», и заметил это НОЧНОЙ
    прогон с сетью, а не обязательная проверка на самом изменении. Ровно 146 —
    зелёный гейт подтверждал себя, а не своё основание. Сеть для этого не
    нужна: ответ каталога лежит на диске.
    """
    try:
        stored = json.loads(EXPORT_JSON.read_text(encoding="utf-8"))
        stored_md = EXPORT_MD.read_text(encoding="utf-8")
    except (OSError, ValueError) as e:
        print(f"нет собранной сводки или она не разобрана — {e}. Соберите: "
              "python scripts/aggregate_bindings.py", file=sys.stderr)
        return 1

    slices = stored.get("consumers", [])
    seen = {s.get("repo") for s in slices}
    missing = [c["repo"] for c in consumers if c.get("repo") not in seen]
    if missing:
        print("в реестре есть потребители, которых нет в сводке: "
              + ", ".join(missing) + ".\n  Пересоберите: "
              "python scripts/aggregate_bindings.py", file=sys.stderr)
        return 1
    # Потребитель с местным ответом читается прямо здесь: сети это не требует,
    # а расхождение ловит на том же изменении, которое его создало.
    for c in consumers:
        source = c.get("bindings")
        if not source or source.startswith("http"):
            continue
        data, err = read_local(source)
        if err:
            print(f"объявленный местный ответ не читается: {c['repo']}: "
                  f"{source} {err}", file=sys.stderr)
            return 1
        want = {rid: rec.get("status") for rid, rec in data.get("rules", {}).items()}
        have = next((s.get("rules") or {} for s in slices
                     if s.get("repo") == c.get("repo")), {})
        if want != have:
            diff = sorted(set(want) | set(have))
            names = [r for r in diff if want.get(r) != have.get(r)]
            shown = ", ".join(f"{r} ({have.get(r, '—')} → {want.get(r, '—')})"
                              for r in names[:5])
            more = "" if len(names) <= 5 else f" и ещё: {len(names) - 5}"
            print(f"сводка отстала от ответа {c['repo']} — расходится: "
                  f"{shown}{more}.\n  Пересоберите: "
                  "python scripts/aggregate_bindings.py", file=sys.stderr)
            return 1
        # ЧЕМ ДЕРЖИТСЯ — ТОЖЕ ПРЕДМЕТ СВЕРКИ. Сравнивать один статус значило бы
        # ловить «правило перестало действовать» и пропускать «правило перестало
        # держаться гейтом»: второе — ровно та потеря, ради которой раздел «чем
        # держат другие» и заведён, и уехала бы она молча (146).
        want_h = {rid: {"mechanism": rec.get("mechanism") or "none",
                        "where": rec.get("where") or ""}
                  for rid, rec in data.get("rules", {}).items()
                  if rec.get("status") == "active"}
        have_h = next((s.get("holds") or {} for s in slices
                       if s.get("repo") == c.get("repo")), {})
        if want_h != have_h:
            names = sorted(r for r in set(want_h) | set(have_h)
                           if want_h.get(r) != have_h.get(r))
            shown = ", ".join(
                f"{r} ({(have_h.get(r) or {}).get('mechanism', '—')} → "
                f"{(want_h.get(r) or {}).get('mechanism', '—')})"
                for r in names[:5])
            more = "" if len(names) <= 5 else f" и ещё: {len(names) - 5}"
            print(f"сводка отстала от того, ЧЕМ держит {c['repo']}: {shown}"
                  f"{more}.\n  Пересоберите: "
                  "python scripts/aggregate_bindings.py", file=sys.stderr)
            return 1

    if as_markdown(slices, rule_ids) != stored_md:
        print(f"устарело — пересоберите: {EXPORT_MD.relative_to(ROOT)} не "
              f"соответствует {EXPORT_JSON.relative_to(ROOT)}", file=sys.stderr)
        return 1

    connected = sum(1 for s in slices if s.get("rules"))
    # Не подключившиеся дольше срока называются и здесь — но БЕЗ отказа:
    # автор изменения чужой репозиторий подключить не может, и красить его
    # работу за это значит приучать к красному (051). Отказ живёт в сетевом
    # прогоне, где у него есть адресат.
    for w in unconnected(consumers):
        print(f"  · {w}")
    for w in stale_answers(slices, rule_ids, superseded_map()):
        print(f"  · {w}")
    # РАСХОЖДЕНИЕ ВЕРСИЙ ФОРМАТА НАЗЫВАЕТСЯ И ЗДЕСЬ. Данных хватает на диске,
    # а раньше находка считалась только сетевым прогоном — то есть появлялась
    # раз в сутки на вкладке, куда не ходят (142). Чужое печатается БЕЗ
    # отказа: файл чужой, и красить им работу автора значит приучать к
    # красному (051). Своё — отказ: заготовку правят здесь.
    чужие_схемы, свои_схемы = schema_findings(slices)
    for w in чужие_схемы:
        print(f"  · {w}")
    if свои_схемы:
        for w in свои_схемы:
            print(w, file=sys.stderr)
        return 1
    for line in census(slices, rule_ids):
        print(line)
    print(f"сводка согласована: потребителей {len(slices)}, из них подключено "
          f"{connected}; сеть не опрашивалась")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="сверить собранное с тем, что лежит на диске")
    args = ap.parse_args()

    # ── исход 2: проверка не отработала ────────────────────────────────────
    try:
        registry = json.loads(CONSUMERS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"проверка не отработала: реестр потребителей не прочитан — {e}",
              file=sys.stderr)
        return 2
    consumers = registry.get("consumers", [])
    if not consumers:
        print(f"проверка не отработала: {CONSUMERS.relative_to(ROOT)} не называет "
              "ни одного потребителя — агрегировать нечего, а молчать нельзя",
              file=sys.stderr)
        return 2
    try:
        rule_ids = [r["id"] for r in json.loads(RULES.read_text(encoding="utf-8"))["rules"]]
    except (OSError, ValueError, KeyError) as e:
        print(f"проверка не отработала: экспорт правил не прочитан — {e}",
              file=sys.stderr)
        return 2

    if args.check:
        return check_offline(consumers, rule_ids)

    slices, problems = collect(consumers)
    try:
        counts = trail_counts(json.loads(RULES.read_text(encoding="utf-8"))["rules"])
    except (OSError, ValueError, KeyError):
        counts = {}
    try:
        born = origin_counts(json.loads(RULES.read_text(encoding="utf-8"))["rules"])
    except (OSError, ValueError, KeyError):
        born = {}
    for entry in slices:
        entry["trails"] = counts.get(entry.get("repo"), 0)
        entry["born"] = born.get(entry.get("repo"), 0)
    warnings = stale(slices)
    # ЧИНИТ НЕ ТОТ, КТО НАШЁЛ. Находки делятся по тому, чьей правкой они
    # снимаются, а не по тому, насколько они серьёзны.
    #
    #   НАШИ   — сводка отстала, объявленный ответ не читается, потребитель
    #            объявлен и молчит дольше срока. Все три правятся ЗДЕСЬ:
    #            первое пересборкой, два других — реестром, вплоть до
    #            удаления записи. Красное уместно;
    #   ЧУЖИЕ  — ответ о правиле, которого в каталоге нет. Правится ровно
    #            одной правкой в ЧУЖОМ файле, и другого способа нет: убирать
    #            потребителя из реестра из-за одной устаревшей строки — не
    #            починка, а потеря связи.
    #
    # ЦЕНА СМЕШЕНИЯ ИЗМЕРЕНА. Первый же прогон с проверкой лишнего ответа
    # покрасил общую ветку из-за записи 143 в ответе витрины. По 053 красное
    # на общей ветке останавливает всю остальную работу — то есть каталог
    # встал из-за строки в чужом файле, и снять это красное он не мог ничем,
    # кроме исключения потребителя из реестра. Красное, которое нельзя снять
    # своей работой, приучают пропускать (051), и тогда оно перестаёт работать
    # и там, где оно наше.
    #
    # МОЛЧАНИЕМ ЭТО НЕ СТАНОВИТСЯ, и это не смягчение (075). Чужая находка
    # печатается каждым прогоном, стоит числом в колонке «Лишних» сводки,
    # едет задачей в НАШ трекер и отдельным разделом во входящие САМОГО
    # потребителя, где её и правят. Четыре адресата вместо одного красного,
    # которое не гаснет.
    problems += unconnected(consumers)
    elsewhere = stale_answers(slices, rule_ids, superseded_map())
    # ВЕРСИЯ БЕРЁТСЯ У ИЗДАТЕЛЯ, А НЕ ИЗ КОНСТАНТЫ. Каталог — такой же
    # потребитель (129), и его собственный ответ по определению стоит на
    # текущей версии; сравнивать с числом в коде значило бы повторить ту самую
    # ошибку, из-за которой правило и приехало (157).
    чужие_схемы, свои_схемы = schema_findings(slices)
    elsewhere += чужие_схемы
    problems += свои_схемы

    doc = {
        "schema": "1.0",
        "catalogue": registry.get("consumers", [{}])[0].get("repo", ""),
        "consumers": slices,
    }
    text_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    text_md = as_markdown(slices, rule_ids)

    EXPORT_JSON.write_text(text_json, encoding="utf-8")
    EXPORT_MD.write_text(text_md, encoding="utf-8")

    for line in census(slices, rule_ids):
        print(line)

    # Чужая находка печатается ВСЕГДА и до нашей: её проще всего потерять.
    if elsewhere:
        print("находки в чужих репозиториях — правятся не здесь:")
        for e in elsewhere:
            print(f"  • {e}")
        print("  Прогон от этого не краснеет: снять такое красное отсюда "
              "нечем.\n  Адресаты — задача в этом трекере и раздел во "
              "входящих самого потребителя.")

    # ── исход 1: находки ───────────────────────────────────────────────────
    if problems:
        print("объявленные потребители, чей ответ не читается:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Потребитель в реестре обещает ответ. Недоступный ответ — "
              "отказ, а не\n  молчание: иначе «не смогли прочитать» выглядит "
              "как «у него всё хорошо».", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"предупреждение: {w}")

    # ── исход 0 ────────────────────────────────────────────────────────────
    connected = sum(1 for s in slices if s.get("rules"))
    print(f"сводка собрана: потребителей {len(slices)}, из них подключено "
          f"{connected}; правил в экспорте {len(rule_ids)}")
    for s in slices:
        if not s.get("rules"):
            print(f"  · {s['repo']}: {s['state']} — {s.get('why', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
