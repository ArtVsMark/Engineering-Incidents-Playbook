#!/usr/bin/env python3
"""Один предмет разбирает одна реализация: копия регулярного выражения в другом модуле — находка.

ПОЧЕМУ ГЕЙТ, А НЕ ДОГОВОРЁННОСТЬ. Правило 214 записано 25 сентября по двум
инцидентам и замеру. 10 сентября сторож толчка разбирал строку `git push` в
трёх местах, два разбора разошлись, и проверка воскрешения выключалась на всю
команду (ревью #475, затем #477). Замер дерева 25 сентября нашёл восемь
регулярных выражений, буква в букву повторённых в двух модулях рабочего кода,
и две копии стояли под комментарием, запрещающим ровно их. Комментарий о
единственности не держит: копию видит только тот, кто сравнивает модули.

ЧТО СЧИТАЕТСЯ ПРЕДМЕТОМ. Вызов `re.compile` со строкой-образцом в модулях
рабочего кода — `scripts/*.py` и `.claude/hooks/*.py`. Один и тот же образец в
двух и более модулях — находка. Внутри одного модуля совпадение не предмет:
его видно глазами на одном экране.

ЧТО НАХОДКОЙ НЕ ЯВЛЯЕТСЯ (051 — гейт отвергает свой предмет):
  • совпадение, названное поимённо в `.rules/copies.json` с причиной: общая
    грамматика, не принадлежащая предмету каталога (заголовок markdown,
    разделитель таблицы), или копия, оставленная намеренно и подписанная по
    071. Список закрыт, как у каждого послабления каталога (102), и запись,
    которой нечего разрешать, — тоже отказ;
  • образец, собранный выражением, а не записанный строкой: разбор его не
    прочтёт.

ГРАНИЦА. Машинно видна литеральная копия. Почти копия — та же мысль с другой
группой захвата или другим порядком — и дубль предиката, написанного кодом, а
не выражением, гейту не видны: их держит правило 214, а не он.

Реализует правила каталога:
  214 — один предмет разбирает одна реализация: одинаковое регулярное
        выражение в двух модулях рабочего кода — находка, пока совпадение не
        названо поимённо с причиной.

Исходы:
  0 — каждый образец живёт в одном модуле или назван в списке;
  1 — есть неназванная копия или запись списка без предмета;
  2 — проверка не отработала (список не прочитан, модуль не разобран).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Где лежит рабочий код — то же место, что у гейта сирот (211).
from check_orphans import РАБОЧИЙ_КОД  # noqa: E402


def образцы(текст: str) -> list[tuple[str, int]]:
    """Строки-образцы `re.compile` в модуле, с номером строки."""
    дерево = ast.parse(текст)
    вышло: list[tuple[str, int]] = []
    for узел in ast.walk(дерево):
        if not (isinstance(узел, ast.Call) and узел.args
                and isinstance(узел.func, ast.Attribute) and узел.func.attr == "compile"
                and isinstance(узел.func.value, ast.Name) and узел.func.value.id == "re"):
            continue
        первый = узел.args[0]
        if isinstance(первый, ast.Constant) and isinstance(первый.value, str):
            вышло.append((первый.value, узел.lineno))
    return вышло


def копии(root: Path) -> tuple[dict[str, list[str]] | None, str]:
    """Образец → места в РАЗНЫХ модулях, где он записан. Вторая строка — отказ."""
    где: dict[str, list[str]] = {}
    for папка in РАБОЧИЙ_КОД:
        for путь in sorted((root / папка).glob("*.py")):
            имя = str(путь.relative_to(root))
            try:
                найдено = образцы(путь.read_text(encoding="utf-8"))
            except (SyntaxError, OSError, UnicodeDecodeError) as e:
                return None, f"{имя} не разобран — {e}"
            for образец, строка in найдено:
                где.setdefault(образец, []).append(f"{имя}:{строка}")
    return {о: м for о, м in где.items()
            if len({x.rsplit(":", 1)[0] for x in м}) > 1}, ""


def список(root: Path) -> tuple[list[dict] | None, str]:
    """Совпадения, названные поимённо. Вторая строка — причина отказа."""
    путь = root / ".rules" / "copies.json"
    имя = путь.relative_to(root)
    if not путь.exists():
        return None, f"{имя} не найден — законные совпадения называет человек"
    try:
        d = json.loads(путь.read_text(encoding="utf-8"))
    except ValueError as e:
        return None, f"{имя} не разобран — {e}"
    записи = d.get("allowed")
    if not isinstance(записи, list):
        return None, f"{имя}: нет списка allowed"
    for з in записи:
        if not (isinstance(з, dict) and з.get("pattern") and str(з.get("why", "")).strip()):
            return None, f"{имя}: у записи нет pattern или why — {з}"
    return записи, ""


def selftest() -> int:
    """Гейт отличает копию в другом модуле от совпадения внутри одного."""
    import tempfile
    случаи = [
        ("один образец в двух модулях — копия",
         {"a": 'import re\nX = re.compile(r"^\\d+$")\n',
          "b": 'import re\nY = re.compile(r"^\\d+$")\n'}, 1),
        ("один образец дважды в одном модуле — не предмет",
         {"a": 'import re\nX = re.compile(r"^\\d+$")\nY = re.compile(r"^\\d+$")\n'}, 0),
        ("разные образцы — чисто",
         {"a": 'import re\nX = re.compile(r"^\\d+$")\n',
          "b": 'import re\nY = re.compile(r"^\\w+$")\n'}, 0),
        ("импорт вместо копии — чисто",
         {"a": 'import re\nX = re.compile(r"^\\d+$")\n',
          "b": "from a import X\n"}, 0),
        ("образец выражением не читается",
         {"a": 'import re\nX = re.compile(r"^\\d+$")\n',
          "b": 'import re\nP = "^\\\\d+$"\nY = re.compile(P)\n'}, 0),
    ]
    плохо = []
    for что, файлы, ждём in случаи:
        with tempfile.TemporaryDirectory() as t:
            корень = Path(t)
            (корень / "scripts").mkdir()
            for имя, текст in файлы.items():
                (корень / "scripts" / f"{имя}.py").write_text(текст, encoding="utf-8")
            найдено, _ = копии(корень)
        вышло = len(найдено or {})
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    for строка in плохо:
        print(f"РАСХОЖДЕНИЕ: {строка}", file=sys.stderr)
    if плохо:
        return 1
    print("самопроверка пройдена: копия в другом модуле отличается от совпадения "
          "в одном и от импорта")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--selftest", action="store_true",
                   help="прогнать гейт по случаям, а не по дереву (140)")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()

    записи, err = список(args.root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2
    найдено, err = копии(args.root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    названы = {з["pattern"] for з in записи}
    неназванные = {о: м for о, м in найдено.items() if о not in названы}
    мёртвые = [з for з in записи if з["pattern"] not in найдено]
    плохо = False
    if неназванные:
        плохо = True
        print("один предмет разбирают две реализации — образец повторён в "
              "другом модуле (214):", file=sys.stderr)
        for образец, места in неназванные.items():
            print(f"  • {образец!r}: {', '.join(места)}", file=sys.stderr)
        print("  Копия сегодня совпадает и разойдётся при первой правке одной из "
              "них, молча.\n"
              "  Либо импорт у того, кто разбирает предмет, либо совпадение "
              "поимённо в .rules/copies.json с причиной.", file=sys.stderr)
    if мёртвые:
        плохо = True
        print(".rules/copies.json: записи, которым в дереве больше нечего "
              "разрешать (102):", file=sys.stderr)
        for з in мёртвые:
            print(f"  • {з['pattern']!r}", file=sys.stderr)
    if плохо:
        return 1
    print(f"один предмет — одна реализация: образцов в двух модулях и более "
          f"{len(найдено)}, и каждый назван с причиной в .rules/copies.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
