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
    """Открытые изменения БЕЗ файлов. Вторым — причина отказа с адресом.

    ПО REST, И СПИСОК ФАЙЛОВ СЮДА НЕ ВХОДИТ. Стояло
    `gh pr list --json number,title,headRefName,files` — одна команда, но у
    неё две цены. Первая: `gh pr list` идёт через GraphQL, а у него своя
    квота, исчерпание которой 7 сентября уронило дежурного и заморозило
    очередь целиком («GraphQL: API rate limit already exceeded»). Вторая:
    поле `files` тянет содержимое КАЖДОГО из полусотни изменений, и стоит
    такой запрос тем дороже, чем больше их открыто.

    Теперь список приходит по REST одним дешёвым запросом, а файлы — только
    у тех изменений, с которыми есть что сравнивать (обычно ни у одного).
    """
    code, out = ghcli.run(
        "api", f"repos/{{owner}}/{{repo}}/pulls?state=open&per_page={LIMIT}",
        "--jq", "[.[] | {number, title, headRefName: .head.ref}]")
    if code != 0:
        return None, f"gh api pulls — {out.strip()[:160] or f'код {code}'}"
    try:
        return json.loads(out or "[]"), None
    except ValueError as e:
        return None, f"ответ gh api pulls не разобран — {e}"


def files_of(number: int) -> tuple[set[str] | None, str | None]:
    """Файлы одного изменения по REST. Вторым — причина отказа с адресом."""
    code, out = ghcli.run(
        "api", f"repos/{{owner}}/{{repo}}/pulls/{number}/files?per_page=100",
        "--jq", "[.[].filename]")
    if code != 0:
        return None, f"gh api pulls/{number}/files — {out.strip()[:160] or f'код {code}'}"
    try:
        return set(json.loads(out or "[]")), None
    except ValueError as e:
        return None, f"ответ gh api pulls/{number}/files не разобран — {e}"


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
        print(f"проверка не отработала: `git -C {args.root} rev-parse "
              "--abbrev-ref HEAD` не назвал ветку", file=sys.stderr)
        return 2
    changes, err = open_changes()
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    mine = next((c for c in changes if c.get("headRefName") == branch), None)
    # СВОИ ФАЙЛЫ СНАЧАЛА ЛОКАЛЬНО, И ТОЛЬКО ПОТОМ У ПЛОЩАДКИ. Раньше у
    # открытого изменения их спрашивали у площадки всегда — запрос ради того,
    # что лежит в рабочем дереве. Гейт зовут ПЕРЕД толчком, истина о своих
    # файлах здесь, и стоит она ноль.
    #
    # НО ЛОКАЛЬНЫЙ ПУТЬ НЕ ВСЕГДА ЕСТЬ, И ЭТО НАШЛИ ТЕСТЫ, А НЕ РАССУЖДЕНИЕ.
    # Первая редакция брала git diff ЕДИНСТВЕННЫМ способом и падала третьим
    # исходом там, где `origin/main` не разрешается: мелкий клон в прогоне,
    # чужое рабочее дерево. Поэтому площадка осталась запасным путём — она
    # дороже, но она есть тогда, когда локальной истории нет.
    done = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", "-z",
         f"origin/main...{branch}"],
        capture_output=True, text=True, encoding="utf-8")
    if done.returncode == 0:
        my_files = {line for line in done.stdout.split() if line}
    elif mine is not None:
        my_files, err = files_of(mine.get("number"))
        if err:
            print(f"проверка не отработала: {err}", file=sys.stderr)
            return 2
    else:
        print("проверка не отработала: список своих файлов не получен — "
              f"{done.stderr.strip()[:120]}", file=sys.stderr)
        return 2
    if not my_files:
        print(f"ветка {branch} не трогает ни одного файла — сравнивать нечего")
        return 0

    # ── исход 1 ────────────────────────────────────────────────────────────
    overlaps: list[str] = []
    for change in changes:
        if change.get("headRefName") == branch:
            continue
        чужие, err = files_of(change.get("number"))
        if err:
            print(f"проверка не отработала: {err}", file=sys.stderr)
            return 2
        общие = sorted(my_files & чужие)
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
