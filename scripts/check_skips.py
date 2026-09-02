#!/usr/bin/env python3
"""Пропущенный тест называет причину, иначе он неотличим от забытого.

Правило 040 держалось ничем с ответом «предмета ещё не было: пропущенных
тестов в наборе ни одного». Ответ верен по факту и неверен по существу:
предмет проверки здесь — **набор тестов**, а он не пуст.
Ноль пропусков сегодня — это не пустота, а состояние, и сторож нужен ровно к
тому дню, когда первый пропуск появится: тогда он приедет с причиной, а не
молча.

ЦЕНА ОТСУТСТВИЯ ИЗМЕРЕНА У СОСЕДА. У грейдера то же держит
`scripts/skip_inventory.py`, и в его же ответе записано: «скрипт был написан
гейтом и полтора месяца не запускался ничем». То есть сам механизм без места в
конвейере не работает — поэтому здесь он шагом `ci.yml`, а не командой,
которую надо помнить (правило 002).

ЧТО СЧИТАЕТСЯ ПРИЧИНОЙ. Непустой `reason=` у метки или непустая строка первым
доводом у вызова. «Временно», «потом» и пустая строка причиной не считаются
только на чтении — гейт держит форму, а не содержание, и это его граница.

ПОЧЕМУ РАЗБОР, А НЕ ПОИСК ПО СТРОКАМ. Первая версия искала выражением и первым
же прогоном нашла пропуски в наборе САМОГО ЭТОГО ГЕЙТА: подделки лежат там
строками внутри тестов, и для поиска по тексту они неотличимы от настоящих.
Разбор синтаксисом различает их без единого исключения — строка в кавычках
декоратором не является (правило 137: сторож смотрит на сырое значение, а
сырое значение здесь — дерево разбора, а не текст).

Реализует правила каталога:
  040 — пропуск без причины неотличим от забытого теста;
  128 — обязательное поле проверяется на полноту, а не на непустоту;
  075 — нет ни одного тестового модуля — отказ, а не чистый прогон;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  158 — третий исход называет предмет: какой файл и какая строка;
  137 — сторож смотрит на сырое значение: пропуск опознаётся разбором, а не
        совпадением текста, иначе подделки в наборе считаются настоящими.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Формы пропуска, встречающиеся в наборах. Список разрешительный и короткий:
#: новая форма получит отказ и придёт с этим (правило 068), а не растворится в
#: широком выражении.
MARKS = {("pytest", "mark", "skip"), ("pytest", "mark", "skipif"),
         ("unittest", "skip"), ("unittest", "skipIf"), ("unittest", "skipUnless")}
CALLS = {("pytest", "skip"), ("unittest", "skip")}


def dotted(node: ast.AST) -> tuple[str, ...]:
    """Имя узла точками: `pytest.mark.skip` → ('pytest', 'mark', 'skip')."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return tuple(reversed(parts))


def named(node: ast.Call) -> bool:
    """Есть ли у вызова непустая причина: `reason=` либо строка доводом."""
    for kw in node.keywords:
        if kw.arg == "reason" and isinstance(kw.value, ast.Constant) \
                and str(kw.value.value).strip():
            return True
    args = [a for a in node.args if isinstance(a, ast.Constant)
            and isinstance(a.value, str)]
    return bool(args and args[-1].value.strip())


def skips(path: Path) -> tuple[list[tuple[int, str]], str | None]:
    """Пропуски без названной причины. Вторым — причина отказа разбора."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as e:
        return [], f"{path.name}:{e.lineno} — {e.msg}"

    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                if dotted(target) not in MARKS:
                    continue
                # Голая метка без скобок причины не несёт по построению.
                if not isinstance(dec, ast.Call) or not named(dec):
                    out.append((dec.lineno, f"пропуск {node.name}"))
        elif isinstance(node, ast.Call) and dotted(node.func) in CALLS:
            if not named(node):
                out.append((node.lineno, "вызов пропуска"))
    return sorted(out), None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    args = parser.parse_args(argv)
    root: Path = args.root
    folder = root / "tests"

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not folder.is_dir():
        print(f"проверка не отработала: нет {folder} — предмета проверки, "
              "то есть самого набора тестов", file=sys.stderr)
        return 2
    files = sorted(p for p in folder.glob("test_*.py"))
    if not files:
        print(f"проверка не отработала: в {folder} нет ни одного модуля "
              "test_*.py. Ноль пропусков при нуле тестов ничего не значит",
              file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    for path in files:
        found, err = skips(path)
        if err:
            print(f"проверка не отработала: набор не разобрался — {err}",
                  file=sys.stderr)
            return 2
        for line_no, what in found:
            problems.append(
                f"{path.relative_to(root)}:{line_no} — {what} без причины. "
                "Без неё пропущенный тест неотличим от забытого")

    if problems:
        print("пропуски без причины:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"пропусков без причины нет: модулей {len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
