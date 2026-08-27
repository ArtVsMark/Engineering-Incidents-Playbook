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
        for rec in rules.values():
            st = rec.get("status", "?")
            by_status[st] = by_status.get(st, 0) + 1
        entry["state"] = "подключён"
        entry["read_at"] = today
        entry["answered"] = len(rules)
        entry["by_status"] = by_status
        entry["rules"] = {rid: rec.get("status") for rid, rec in rules.items()}
        slices.append(entry)

    return slices, problems


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
        "| Проект · Project | Состояние · State | Ответов · Answers | Почему · Why |",
        "|---|---|---|---|",
    ]
    for s in slices:
        answered = s.get("answered")
        lines.append(
            f"| `{s['repo']}` | {s['state']} | "
            f"{answered if answered is not None else '—'} | {s.get('why', '')} |")

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

    if as_markdown(slices, rule_ids) != stored_md:
        print(f"устарело — пересоберите: {EXPORT_MD.relative_to(ROOT)} не "
              f"соответствует {EXPORT_JSON.relative_to(ROOT)}", file=sys.stderr)
        return 1

    connected = sum(1 for s in slices if s.get("rules"))
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
    warnings = stale(slices)

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
