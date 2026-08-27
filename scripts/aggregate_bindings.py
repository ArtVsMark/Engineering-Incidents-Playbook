#!/usr/bin/env python3
"""Собирает таблицу «где действует правило» из ответов потребителей.

Путь «проект → каталог» держится правилом 080 и работает. Путь «каталог →
проект» не держался ничем: правило, родившееся в одном проекте, для остальных
не существовало — не «отклонено», не «неприменимо», а просто отсутствовало, и
отличить это от рассмотренного решения было нельзя ни в одном репозитории.

Здесь собирается вторая половина: ответы потребителей читаются по обычному
HTTPS, без API и без клона, и сводятся в одну таблицу.

Реализует правила каталога:
  129 — контракт потребления: ответ имеет форму, и она проверяется;
  049 — таблица вычисляется из ответов, а не ведётся руками;
  075 — объявленный потребитель, чей ответ не читается, — отказ, а не молчание;
  027 — «не подключён» и «неизвестно» это состояния, и они печатаются;
  046 — чего механизм не знает, названо прямо, а не сглажено;
  039 — три исхода, а не два.

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
        entry["state"] = "подключён"
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



#: Как механизм называется по-человечески. `none` сюда не попадает: он не
#: механизм, а его отсутствие, и в разделе «чем держат» ему нечего сказать.
MECHANISM_RU = {"gate": "гейт", "process-step": "шаг процесса"}


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
        "| Проект · Project | Состояние · State | Следов · Trails | "
        "Ответов · Answers | Без ответа · Unanswered | Лишних · Stale | "
        "Действует · Active | Гейтом · Gate | Шагом · Step | Ничем · Nothing | "
        "Механизмов · Mechanisms | Почему · Why |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    known = set(rule_ids)
    for s in slices:
        answered = s.get("answered")
        m = s.get("by_mechanism") or {}
        answers = s.get("rules") or {}
        if s.get("rules") is None:
            cells = ["—"] * 7
        else:
            # ЛИШНИЙ ОТВЕТ — ЭТО НАХОДКА, А НЕ ОКРУГЛЕНИЕ. Витрина отвечала за
            # сто сорок восемь правил при ста сорока семи в экспорте: ответ
            # остался от удалённой записи. Разница пряталась в одном числе
            # «ответов», и увидеть её можно было только вычитанием в уме.
            cells = [
                str(len(known - set(answers))),
                str(len(set(answers) - known)),
                str((s.get("by_status") or {}).get("active", 0)),
                *(str(m.get(k, 0)) for k in ("gate", "process-step", "none")),
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
    for entry in slices:
        entry["trails"] = counts.get(entry.get("repo"), 0)
    warnings = stale(slices)
    # Срок вышел — это отказ СЕТЕВОГО прогона: у него есть адресат, задача в
    # трекере. На изменении тот же список печатается без отказа (см. --check).
    problems += unconnected(consumers)

    doc = {
        "schema": "1.0",
        "catalogue": registry.get("consumers", [{}])[0].get("repo", ""),
        "consumers": slices,
    }
    text_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    text_md = as_markdown(slices, rule_ids)

    EXPORT_JSON.write_text(text_json, encoding="utf-8")
    EXPORT_MD.write_text(text_md, encoding="utf-8")

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
