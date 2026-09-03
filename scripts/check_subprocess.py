#!/usr/bin/env python3
"""Текстовый вызов наружу называет кодировку, а не берёт её у окружения.

Правило 176: умолчание, вычисляемое из ОКРУЖЕНИЯ, — скрытая зависимость от
платформы, и матрица прогонов её не доказывает. `subprocess` в текстовом режиме
без `encoding=` берёт кодировку локали: на ubuntu и macos это UTF-8, на
windows-раннере cp1252. Дефект проявляется, только если СОВПАЛИ два условия —
платформа и подходящие данные, — поэтому зелёный прогон говорит «совпадения не
случилось», а не «умолчание задано».

ПОЧЕМУ РАЗБОР ИСХОДНИКА, А НЕ ПРОГОН. У прогона предмет появляется лишь при
совпадении условий; у разбора — всегда. Ответ разбора не зависит ни от
платформы, ни от данных, и потому проверяем он на любой машине.

ТЕКСТОВЫЙ РЕЖИМ ВКЛЮЧАЕТ ЛЮБОЙ ИЗ ТРЁХ КЛЮЧЕЙ — `text`, `universal_newlines`,
`errors`. Последний коварнее прочих: `errors="replace"` без `encoding=` даёт ту
же локаль и выглядит при этом предусмотрительностью.

ЗАМЕР У КАТАЛОГА, 3 сентября: 23 вызова в `scripts/` и 7 в `tests/` в текстовом
режиме и НИ ОДНОГО с явной кодировкой. Наступить дефект не мог — матрицы у
каталога нет вовсе, прогон идёт только на ubuntu, — и это ровно тот случай, о
котором правило и предупреждает.

ЧЕГО ГЕЙТ НЕ ДЕЛАЕТ. Не смотрит на ДВОИЧНЫЕ вызовы: там кодировки нет по
построению, и требовать её значило бы краснеть на верном коде (051). Не
проверяет он и сторону записи — `input=` кодируется тем же ключом, и отдельного
предмета там нет.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.

Реализует правила каталога:
  176 — умолчание, взятое из окружения, задаётся явно;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — ноль просмотренных файлов это отказ, а не чистый прогон;
  165 — печатается ОХВАТ: сколько файлов просмотрено, а не только находки.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Ключи, включающие текстовый режим. Любого достаточно, и это свойство
#: CPython, а не наше соглашение.
TEXT_KEYS = ("text", "universal_newlines", "errors")

#: Вызовы subprocess, у которых бывает текстовый режим.
CALLS = ("run", "check_output", "Popen", "check_call", "call")


def offenders(source: str) -> list[tuple[int, str]]:
    """Строки текстовых вызовов без `encoding=`. Разбор дерева, а не поиск строк.

    Поиск подстрокой здесь дал бы ложные находки на слове `text=True` в
    докстроке и пропустил бы вызов, разложенный по строкам (166: проверка
    отношения через присутствие подстроки зеленеет там, где отношения нет).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        имя = ""
        if isinstance(node.func, ast.Attribute):
            имя = node.func.attr
        elif isinstance(node.func, ast.Name):
            имя = node.func.id
        if имя not in CALLS:
            continue
        ключи = {kw.arg for kw in node.keywords if kw.arg}
        if not (ключи & set(TEXT_KEYS)):
            continue
        if "encoding" in ключи:
            continue
        found.append((node.lineno, имя))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    файлы = sorted(list((args.root / "scripts").glob("*.py"))
                   + list((args.root / "tests").glob("*.py"))
                   + list((args.root / "templates").glob("*.py")))
    # ── исход 2 ────────────────────────────────────────────────────────────
    if not файлы:
        print("проверка не отработала: ни одного исходника не нашлось — "
              "проверять нечего, и зеленеть на этом нельзя", file=sys.stderr)
        return 2

    находки: list[str] = []
    for f in файлы:
        for строка, имя in offenders(f.read_text(encoding="utf-8", errors="replace")):
            находки.append(f"{f.relative_to(args.root)}:{строка} — "
                           f"subprocess.{имя} в текстовом режиме без encoding=")

    # ── исход 1 ────────────────────────────────────────────────────────────
    if находки:
        print("текстовые вызовы берут кодировку у окружения:", file=sys.stderr)
        for n in находки:
            print(f"  • {n}", file=sys.stderr)
        print("\n  Допишите encoding=\"utf-8\". Матрица этого не поймает: дефект"
              "\n  требует совпадения платформы и данных, и зелёное говорит"
              "\n  «совпадения не случилось» (176).", file=sys.stderr)
        return 1

    print(f"текстовые вызовы называют кодировку: просмотрено файлов {len(файлы)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
