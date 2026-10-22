#!/usr/bin/env python3
"""Починка, тронувшая код механизма, приносит проверку — или называет, почему не нужна.

Правило 014 доказывает исправление красным до починки, и половина его — сам
полу-откат — машине недоступна: отличить в откате поведение от имён значит
читать смысл правки. Вторая половина доступна: без проверки, краснеющей до
починки, доказывать нечем, а значит, починка кода без тронутых `tests/`
убирает поведение, а не дефект — и вернуться он может молча.

ЗАМЕР 16.09 ПО СОРОКА КОММИТАМ ОБЩЕЙ ВЕТКИ (ответ каталога по 014): починок,
тронувших `scripts/*.py`, одиннадцать; проверку принесли семь. Из четырёх без
неё две тронули ТОЛЬКО докстроку — им проверка не нужна, — и две были
настоящими пропусками. Поэтому правка одной прозы освобождается здесь сама:
без этого гейт отказал бы четырём, и двум ложно.

ЧТО СЧИТАЕТСЯ ПРОЗОЙ. Сравниваются деревья разбора файла до и после, без
докстрок модуля, классов и функций; комментарии в дерево не попадают вовсе.
Деревья совпали — правка прозаическая, проверки не требует. Сравнение строк
здесь не годится: переформатирование кода без смены смысла дало бы «код
тронут», а правка докстроки на одной строке с кодом — «не тронут».

ЧЕГО ГЕЙТ НЕ ДЕЛАЕТ. Он не судит, та ли это проверка и краснела ли она до
починки: это первая половина 014, и она остаётся документом
(CONTRIBUTING.md § Когда дефект считается исправленным). Удалённый скрипт
проверки не требует — проверять больше нечего.

ВЫХОД НАЗВАН, А НЕ ПОДРАЗУМЕВАЕТСЯ (126): строка в теле изменения
«Проверка: не требуется — <причина>». Без выхода гейт обходили бы пустым
тестом, а пустой тест хуже отсутствующего — он выглядит доказательством.

Взят у соседа: тот же отказ стоит в `check_journal.py`
ArtVsMark/Engineering-Pipeline-Mechanisms; освобождение прозы добавлено здесь
по нашему замеру.

Реализует правила каталога:
  014 — починка кода приносит проверку: без неё нечем показать красное до починки;
  051 — запрещается достоверное: проза освобождена, потому что ложный отказ
        на ней был бы систематическим;
  126 — у отказа есть названный выход, и он заполняется причиной;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  158 — третий исход называет предмет: какой файл не прочитан.

Запуск:
  python scripts/check_fix_check.py --paths-from <файл путей> --base <sha> \\
      --body-file <файл с телом изменения>

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

import proc

ROOT = Path(__file__).resolve().parent.parent

#: Фрагмент журнала, объявляющий изменение починкой.
FIXED_RE = re.compile(r"^changelog\.d/[^/]+\.fixed\.md$")
#: Код механизмов: скрипты каталога.
CODE_RE = re.compile(r"^scripts/.+\.py$")
TESTS = "tests/"
#: Названный выход: «Проверка: не требуется — причина». Причина обязательна.
#: Пробелы — только внутри строки: `\s` перешагнул бы перевод строки, и пустая
#: причина взяла бы следующую строку тела (обзор #830).
WAIVER_RE = re.compile(
    r"(?m)^[ \t]*Проверка:[ \t]*не[ \t]+требуется[ \t]*[—–-][ \t]*(?P<why>\S[^\n]*?)[ \t]*$")


class NotRun(Exception):
    """Проверка не состоялась; сообщение называет предмет."""


def без_прозы(текст: str, имя: str) -> str:
    """Дерево разбора без докстрок — то, что исполняется, а не читается."""
    try:
        дерево = ast.parse(текст)
    except SyntaxError as exc:
        raise NotRun(f"{имя} не разбирается: {exc.msg}, строка {exc.lineno}") from exc
    for узел in ast.walk(дерево):
        if isinstance(узел, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            тело = узел.body
            if (тело and isinstance(тело[0], ast.Expr)
                    and isinstance(тело[0].value, ast.Constant)
                    and isinstance(тело[0].value.value, str)):
                узел.body = тело[1:] or [ast.Pass()]
    return ast.dump(дерево, include_attributes=False)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return proc.run(["git", "-C", str(root), *args],
                    capture_output=True, text=True, encoding="utf-8", timeout=60)


def прежний(root: Path, base: str, путь: str) -> str | None:
    """Текст файла на базе; None — файла на базе не было.

    Наличие спрашивается кодом `git cat-file -e`, а не разбором текста ошибки
    (обзор #830): сообщение `git` переводится и меняется от версии к версии.
    """
    if git(root, "cat-file", "-e", f"{base}^{{commit}}").returncode != 0:
        raise NotRun(f"база {base} не найдена в дереве {root}")
    if git(root, "cat-file", "-e", f"{base}:{путь}").returncode != 0:
        return None
    run = git(root, "show", f"{base}:{путь}")
    if run.returncode != 0:
        raise NotRun(f"база {base} не прочитана для {путь}: {run.stderr.strip()}")
    return run.stdout


def код_тронут(root: Path, base: str, путь: str) -> bool:
    """Изменилось ли исполняемое: новый файл — да, удалённый — нет, иначе деревья."""
    файл = root / путь
    if not файл.exists():
        return False                      # удалён: проверять больше нечего
    try:
        новый = файл.read_text(encoding="utf-8")
    except OSError as exc:
        raise NotRun(f"{путь} не прочитан: {exc}") from exc
    старый = прежний(root, base, путь)
    if старый is None:
        return True                       # новый скрипт — новое поведение
    return без_прозы(старый, f"{путь}@{base}") != без_прозы(новый, путь)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--paths-from", type=Path, required=True,
                    help="файл со списком путей изменения, по одному в строке")
    ap.add_argument("--base", required=True, help="коммит базы изменения")
    ap.add_argument("--body-file", type=Path, required=True,
                    help="файл с телом изменения")
    args = ap.parse_args(argv)

    try:
        пути = [p.strip() for p in args.paths_from.read_text(encoding="utf-8").splitlines()
                if p.strip()]
        тело = args.body_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"проверка не отработала: не прочитан {exc.filename}: {exc.strerror}",
              file=sys.stderr)
        return 2

    починка = [p for p in пути if FIXED_RE.match(p)]
    if not починка:
        print("изменение не объявлено починкой — фрагмента *.fixed.md нет, спрашивать нечего")
        return 0
    # Проверкой считается живой файл под tests/: удалённый тест — это убранная
    # проверка, а не принесённая (обзор #830). Та ли это проверка — граница
    # гейта: судит приёмка, а не машина.
    проверки = [p for p in пути if p.startswith(TESTS) and (args.root / p).is_file()]
    if проверки:
        print(f"починка принесла проверку: {', '.join(проверки)}")
        return 0

    try:
        код = [p for p in пути if CODE_RE.match(p) and код_тронут(args.root, args.base, p)]
    except NotRun as exc:
        print(f"проверка не отработала: {exc}", file=sys.stderr)
        return 2
    прозой = [p for p in пути if CODE_RE.match(p) and p not in код]

    if not код:
        хвост = f" (тронута только проза: {', '.join(прозой)})" if прозой else ""
        print(f"починка не тронула исполняемый код механизмов{хвост} — проверка не требуется")
        return 0
    if (m := WAIVER_RE.search(тело)) is not None:
        print(f"починка кода без проверки, выход назван: {m['why']}")
        return 0

    print("починка тронула код механизмов и не принесла проверки:", file=sys.stderr)
    for p in код:
        print(f"  • {p}", file=sys.stderr)
    print("\n  Без проверки, краснеющей до починки, доказывать нечем (014): убрано\n"
          "  поведение, а не дефект, и вернуться он может молча. Добавьте случай в\n"
          "  tests/ — либо строку «Проверка: не требуется — <причина>» в тело\n"
          "  изменения, если проверять и правда нечем.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
