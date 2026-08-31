#!/usr/bin/env python3
"""Каждая заготовка названа в своём документе и сказано, как она живёт у себя.

Правило 155: заготовка, которой не пользуешься сам, расходится с практикой
молча. Расхождение одностороннее и невидимое — о нём сообщил бы потребитель, а
он не знает, как устроено у нас, и берёт заготовку за образец именно поэтому.

ЧТО ПРОВЕРЯЕТСЯ. Таблица в `templates/README.md` — единственное место, где о
заготовках говорят, — обязана называть каждый файл каталога заготовок и на
каждый отвечать, чем он применяется у себя: адресом своего артефакта либо
явным «нет: причина». Отсутствие ответа — находка; ответ «нет» без причины —
тоже, потому что «у нас иначе» без причины неотличимо от «забыли».

ЧЕГО ЗДЕСЬ НЕТ. Суждения о том, применяется ли заготовка НА САМОМ ДЕЛЕ тем же
способом. Названный путь проверяется на существование, и только: совпадает ли
практика по существу, машинно не выразимо, и это граница самого 155. Гейт
держит форму ответа, а содержание — приёмка.

ПОЧЕМУ НЕ «ЗАПУСКАЕТСЯ». Шаг `templates/preflight.py --list` в конвейере уже
стоял и был зелёным всё то время, что заготовка расходилась с практикой:
запускаются обе — и рабочая, и разошедшаяся (155, инцидент).

Реализует правила каталога:
  155 — заготовка применяется у себя либо называет, почему у себя иначе;
  046 — «нет предмета» и «забыли» различаются только названной причиной;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — ноль заготовок это отказ, а не чистый прогон.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Строка таблицы: `| [`файл`](файл) | зачем | правила | у себя |`.
ROW_RE = re.compile(r"^\|\s*\[`([^`]+)`\]")
#: Ответ «у себя такого нет» — причина обязана быть непустой.
ABSENT_RE = re.compile(r"^нет:\s*\S+")
#: Адрес своего артефакта: путь либо каталог. Проза адресом не считается —
#: ровно как в `where` ответа каталога (правило 049 и гейт check_bindings).
PATH_RE = re.compile(r"[\w./-]+(?:\.\w+|/)")


def rows(readme: str) -> dict[str, str]:
    """Файл заготовки → содержимое последнего столбца таблицы."""
    out: dict[str, str] = {}
    for line in readme.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        out[m.group(1)] = cells[-1] if len(cells) >= 2 else ""
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    args = parser.parse_args(argv)
    root: Path = args.root
    folder = root / "templates"
    readme = folder / "README.md"

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not readme.exists():
        print(f"проверка не отработала: нет {readme} — документа о заготовках, "
              "в котором и живёт ответ", file=sys.stderr)
        return 2
    files = sorted(p.name for p in folder.iterdir()
                   if p.is_file() and p.name != "README.md")
    if not files:
        print("проверка не отработала: в templates/ нет ни одной заготовки — "
              "проверять нечего, и зеленеть на этом нельзя", file=sys.stderr)
        return 2

    table = rows(readme.read_text(encoding="utf-8"))
    if not table:
        print("проверка не отработала: в templates/README.md не разобралось ни "
              "одной строки таблицы — это ошибка разбора, а не пустой каталог",
              file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    for name in files:
        if name not in table:
            problems.append(
                f"{name}: заготовка есть, а строки о ней в templates/README.md "
                "нет. Потребитель видит файл, о котором каталог молчит")
            continue
        answer = table[name]
        if not answer:
            problems.append(
                f"{name}: не сказано, чем эта заготовка применяется у себя. "
                "Либо адрес своего артефакта, либо «нет: причина» (155)")
            continue
        if ABSENT_RE.match(answer):
            continue
        found = PATH_RE.findall(answer.replace("`", ""))
        alive = [t for t in found if (root / t.rstrip("/")).exists()]
        if not found:
            problems.append(
                f"{name}: ответ «{answer[:50]}» адреса не называет. Проза не "
                "адрес: применение, которое нельзя открыть, не проверить")
        elif not alive:
            problems.append(
                f"{name}: назван адрес «{found[0]}», а его не существует — "
                "декларация разошлась с фактом")

    for name in sorted(set(table) - set(files)):
        problems.append(
            f"{name}: назван в таблице, а файла в templates/ нет. Строка "
            "пережила заготовку и обещает то, чего нет")

    if problems:
        print("заготовки разошлись со своим документом:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"заготовки в порядке: {len(files)}, у каждой сказано, "
          "чем она применяется у самого каталога")
    return 0


if __name__ == "__main__":
    sys.exit(main())
