#!/usr/bin/env python3
"""Готово ли изменение к слиянию: решение по списку проверок, а не по красноте.

ПОЧЕМУ ЭТО ОТДЕЛЬНЫЙ СКРИПТ, А НЕ УСЛОВИЕ В ОБОЛОЧКЕ. У условия в `run:` нет
отвергаемого предмета: подсунуть ему подделанный список проверок нечем, и
проверить его можно только живым слиянием — то есть никак (правила 140, 145).

ЧТО ЗДЕСЬ ДЕРЖИТСЯ. Правило 010 дословно: «условие „нет красных и нет
ожидающих“ истинно на ПУСТОМ множестве». Сторож слияния проверял только
отсутствие красных, и изменение без единого прогона проходило как чистое.

Пустой список — не редкость и не сбой: изменение с конфликтом НЕ ПОЛУЧАЕТ
прогонов вовсе, потому что площадка не может собрать ссылку слияния и события
`pull_request` не рождается. В этом состоянии проверок нет штатно, и оно с
«всё зелено» неотличимо ровно так, как предупреждает 010.

ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА СПРАШИВАЕТСЯ ПОИМЁННО. «Что-то зелёное есть» — не то же
самое, что «прошла та самая»: посторонняя работа зеленеет сама по себе, и её
достаточно, чтобы условие стало истинным. Разрешительный список вместо
запретительного, ровно 068.

Запуск:  gh api …/check-runs | python scripts/merge_ready.py --required catalogue
Коды:    0 сливать можно · 1 сливать нельзя · 2 проверка не отработала

Реализует правила каталога:
  010 — пустой список проверок трактуется как «не стартовало», а не «всё хорошо».
"""

from __future__ import annotations

import argparse
import json
import sys

#: Исходы, которые считаются незелёными. Список её, площадки, а не наш.
BAD = ("failure", "timed_out", "cancelled", "action_required", "stale")
#: Исходы, означающие «ещё идёт». Ожидание — не отказ, но и не разрешение.
PENDING = (None, "", "queued", "in_progress", "waiting", "pending", "requested")


def verdict(runs: list[dict], required: list[str]) -> tuple[bool, str]:
    """Можно ли сливать. Вторая строка — причина, годная для печати."""
    if not runs:
        return False, ("проверок нет НИ ОДНОЙ — это «не стартовало», а не «всё "
                       "хорошо» (правило 010). Частая причина: у изменения "
                       "конфликт, и площадка не собрала ссылку слияния")
    bad = sorted({r.get("name", "?") for r in runs
                  if (r.get("conclusion") or "") in BAD})
    if bad:
        return False, "незелёные проверки: " + ", ".join(bad)
    waiting = sorted({r.get("name", "?") for r in runs
                      if r.get("status") != "completed"
                      or r.get("conclusion") in PENDING})
    if waiting:
        return False, "проверки ещё идут: " + ", ".join(waiting)
    green = {r.get("name") for r in runs if r.get("conclusion") == "success"}
    missing = [n for n in required if n not in green]
    if missing:
        return False, ("обязательные проверки не зелены на этой голове: "
                       + ", ".join(missing) + ". Зелены: "
                       + (", ".join(sorted(n for n in green if n)) or "—"))
    return True, f"проверок {len(runs)}, все зелёные, обязательные на месте"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--required", default="", metavar="ИМЕНА",
                    help="имена обязательных проверок через запятую")
    args = ap.parse_args(argv)
    required = [n.strip() for n in args.required.split(",") if n.strip()]

    # ── исход 2 ────────────────────────────────────────────────────────────
    raw = sys.stdin.read()
    if not raw.strip():
        print("проверка не отработала: список проверок не передан", file=sys.stderr)
        return 2
    try:
        doc = json.loads(raw)
    except ValueError as e:
        print(f"проверка не отработала: список проверок не разобран — {e}",
              file=sys.stderr)
        return 2
    runs = doc.get("check_runs") if isinstance(doc, dict) else doc
    if not isinstance(runs, list):
        print("проверка не отработала: в ответе нет списка проверок",
              file=sys.stderr)
        return 2

    ok, why = verdict(runs, required)
    if ok:
        print(f"сливать можно: {why}")
        return 0
    # ── исход 1 ────────────────────────────────────────────────────────────
    print(f"сливать нельзя: {why}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
