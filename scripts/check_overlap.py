#!/usr/bin/env python3
"""Кто ещё правит те же файлы: граница изменения — пересечение, а не тема.

Правило 133 держалось ничем с ответом «общий файл между ветками счётен
сравнением диффов; очередь не дошла». Цена измерена 2 сентября: окно толкнуло
ветку с механизмом для 021, а ночной прогон `consumers-sync` в это же время
открыл своё изменение и тронул `export/where.json` и `export/where.md`.
Изменение приехало с конфликтом, и узналось это от площадки — после толчка.

ПОЧЕМУ ОТКРЫТЫЕ ИЗМЕНЕНИЯ, А НЕ ВЕТКИ. Пустая ветка и слитая ветка выглядят
одинаково: слияние идёт squash, коммиты ветки предками общей не становятся, и
`git branch --no-merged` считает живыми все 23 наших ветки, из которых живых
две. Признак «сейчас кто-то это правит» — открытое изменение, и берётся он у
площадки, а не выводится из формы истории (правило 049).

ПОЧЕМУ НЕ ОТКАЗ. Пересечение бывает законным: производные файлы трогает почти
каждая правка. Правило требует, чтобы граница была ВИДНА, а не чтобы её не
было; красное на законном приучало бы пропускать красное (051). Поэтому
находка печатается и адресуется тому, кто толкает, а слияние не держит.

Реализует правила каталога:
  133 — границу изменения задаёт пересечение файлов, а не число задач;
  049 — состояние берётся у площадки, а не выводится из формы истории;
  051 — предупреждают о вероятном, запрещают достоверное;
  039 — три исхода: чисто · есть пересечения · проверка не отработала;
  158 — третий исход называет предмет: чем именно не ответила площадка.

Запуск:  python scripts/check_overlap.py [--branch ВЕТКА]
Исходы:  0 пересечений нет · 1 есть · 2 проверка не отработала.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import ghcli

ROOT = Path(__file__).resolve().parent.parent
#: Сколько открытых изменений спрашивается. Больше полусотни у каталога не
#: бывало ни разу; предел стоит, чтобы отказ площадки не превратился в обход.
LIMIT = 50


def current_branch(root: Path) -> str:
    done = subprocess.run(["git", "-C", str(root), "rev-parse",
                           "--abbrev-ref", "HEAD"], capture_output=True, text=True, encoding="utf-8")
    return done.stdout.strip()


def open_changes() -> tuple[list[dict] | None, str | None]:
    """Открытые изменения с их файлами. Вторым — причина отказа с адресом."""
    code, out = ghcli.run("pr", "list", "--state", "open", "--limit", str(LIMIT),
                          "--json", "number,title,headRefName,files")
    if code != 0:
        return None, f"gh pr list — {out.strip()[:160] or f'код {code}'}"
    try:
        return json.loads(out), None
    except ValueError as e:
        return None, f"ответ gh pr list не разобран — {e}"


def files_of(change: dict) -> set[str]:
    return {f.get("path", "") for f in (change.get("files") or [])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    parser.add_argument("--branch", help="ветка, для которой считается "
                                         "пересечение; по умолчанию текущая")
    args = parser.parse_args(argv)
    root: Path = args.root
    branch = args.branch or current_branch(root)

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not branch:
        print("проверка не отработала: имя ветки не получено — git не ответил",
              file=sys.stderr)
        return 2
    changes, err = open_changes()
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    mine = next((c for c in changes if c.get("headRefName") == branch), None)
    if mine is not None:
        my_files = files_of(mine)
    else:
        done = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "-z",
             f"origin/main...{branch}"],
            capture_output=True, text=True, encoding="utf-8")
        if done.returncode != 0:
            print("проверка не отработала: список своих файлов не получен — "
                  f"{done.stderr.strip()[:120]}", file=sys.stderr)
            return 2
        my_files = {line for line in done.stdout.split() if line}
    if not my_files:
        print(f"ветка {branch} не трогает ни одного файла — сравнивать нечего")
        return 0

    # ── исход 1 ────────────────────────────────────────────────────────────
    overlaps: list[str] = []
    for change in changes:
        if change.get("headRefName") == branch:
            continue
        общие = sorted(my_files & files_of(change))
        if общие:
            overlaps.append(
                f"#{change.get('number')} «{(change.get('title') or '')[:48]}» "
                f"({change.get('headRefName')}): " + " · ".join(общие[:6])
                + (f" и ещё {len(общие) - 6}" if len(общие) > 6 else ""))

    if overlaps:
        print(f"те же файлы правит кто-то ещё — открытых изменений "
              f"{len(overlaps)}:")
        for o in overlaps:
            print(f"  ~ {o}")
        print("  Пересечение бывает законным, и слияние это не держит: "
              "решает тот, кто толкает. Но узнать об этом надо ДО толчка, а "
              "не из конфликта после (правило 133).")
        return 1

    print(f"пересечений нет: ветка {branch}, файлов {len(my_files)}, "
          f"открытых изменений рядом {len(changes) - (1 if mine else 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
