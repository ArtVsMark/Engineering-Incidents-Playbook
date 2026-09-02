#!/usr/bin/env python3
"""Вердикт выносится ПОСЛЕ последнего случая, а не посреди перебора.

Правило 159 держалось ничем с ответом «не дошли руки». Руки и не нужны:
предмет счётен по коду. Набор или гейт, копящий находки в список, обязан
читать этот список после цикла — ранний выход превращает всё, что идёт
следом, в непроверенное, и делает это молча: вердикт печатается, код возврата
есть, а половина предметов не рассмотрена.

ЧТО СЧИТАЕТСЯ РАННИМ ВЕРДИКТОМ. Внутри цикла, который что-то добавляет в
накопитель, стоит `return`, ЧИТАЮЩИЙ этот накопитель. Тогда возвращается
неполный список — и не видно, что он неполон.

ЧТО РАННИМ ВЕРДИКТОМ НЕ ЯВЛЯЕТСЯ, и это измерено. Возврат ТРЕТЬЕГО ИСХОДА:
`return 2` или `return 2, …` — «проверка не отработала». Он законен и обязан
быть ранним: продолжать перебор, когда сборщика нет или источник не прочитан,
значит копить находки о состоянии, которого не знаешь (039). Замер по
`scripts/`: таких возвратов внутри накопительных циклов два, и оба именно
третий исход — сборщика нет, сборщик отказал.

ПОЧЕМУ РАЗБОР СИНТАКСИСОМ, А НЕ ПОИСКОМ. Поиск по тексту `return` внутри
`for` не отличает возврат накопителя от возврата константы, а именно в этом
различии всё правило. Тот же урок уже стоил одного гейта: первая редакция
проверки пропусков искала выражением и нашла находки в собственном наборе.

Реализует правила каталога:
  159 — вердикт выносится после последнего случая, а не посреди перебора;
  039 — третий исход законен и обязан быть ранним: он не вердикт, а отказ;
  137 — сторож смотрит на сырое значение: предмет здесь дерево разбора, а не
        текст файла;
  075 — ноль просмотренных файлов это отказ, а не чистый прогон;
  158 — третий исход называет предмет: какой файл не разобран и почему.

Запуск:  python scripts/check_verdict_order.py [--root <корень>]

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: Где смотрим. Наборы тестов тоже копят находки, и правило про них же.
WHERE = ("scripts", "tests")
#: Третий исход каталога — двойка. Возврат, несущий её, отказом перебора не
#: является: он говорит «проверка не отработала», а не «находок столько».
THIRD = 2


def accumulators(fn: ast.AST) -> set[str]:
    """Имена, которым в теле присвоен список: они и копят находки."""
    out: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            out |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        elif (isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.List)
              and isinstance(node.target, ast.Name)):
            out.add(node.target.id)
    return out


def third_outcome(ret: ast.Return) -> bool:
    """Возврат третьего исхода: `return 2` либо `return 2, …`."""
    value = ret.value
    if isinstance(value, ast.Constant) and value.value == THIRD:
        return True
    if isinstance(value, ast.Tuple) and value.elts:
        first = value.elts[0]
        return isinstance(first, ast.Constant) and first.value == THIRD
    return False


def early(tree: ast.AST, where: str) -> list[str]:
    """Ранние вердикты в одном разобранном файле."""
    out: list[str] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        acc = accumulators(fn)
        if not acc:
            continue
        for loop in ast.walk(fn):
            if not isinstance(loop, (ast.For, ast.While)):
                continue
            копит = any(
                isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                and c.func.attr in ("append", "extend")
                and isinstance(c.func.value, ast.Name) and c.func.value.id in acc
                for c in ast.walk(loop))
            if not копит:
                continue
            for ret in ast.walk(loop):
                if not isinstance(ret, ast.Return) or third_outcome(ret):
                    continue
                names = {n.id for n in ast.walk(ret) if isinstance(n, ast.Name)}
                if names & acc:
                    out.append(
                        f"{where}::{fn.name}, строка {ret.lineno}: вердикт "
                        "читает накопитель ВНУТРИ цикла — всё, что идёт "
                        "следом, останется непроверенным молча")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="корень каталога; по умолчанию сам этот репозиторий")
    args = ap.parse_args(argv)

    files = sorted(p for d in WHERE for p in (args.root / d).glob("*.py"))
    # ── исход 2 ────────────────────────────────────────────────────────────
    if not files:
        print(f"проверка не отработала: в {', '.join(WHERE)} нет ни одного "
              "файла — просматривать нечего (075)", file=sys.stderr)
        return 2

    problems: list[str] = []
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            print(f"проверка не отработала: {path.relative_to(args.root)} не "
                  f"разобран — {exc}", file=sys.stderr)
            return 2
        problems += early(tree, str(path.relative_to(args.root)))

    # ── исход 1 ────────────────────────────────────────────────────────────
    if problems:
        print("вердикт выносится посреди перебора:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        print("\n  Список находок читают ПОСЛЕ последнего случая (правило 159).\n"
              "  Ранний выход законен только третьим исходом — «проверка не\n"
              "  отработала», и он возвращает 2, а не накопитель.",
              file=sys.stderr)
        return 1

    print(f"вердикты на месте: просмотрено файлов {len(files)}, "
          "ранних вердиктов нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
