#!/usr/bin/env python3
"""Транспорт к площадке соответствует объявленному: REST, GraphQL — поимённо.

ПОЧЕМУ ГЕЙТ, А НЕ ДОГОВОРЁННОСТЬ. Правило 001 записано 2 сентября после того,
как 2669 points из часовых 5000 ушли на девять операций: одна операция GraphQL
стоит ~300, REST — 1. Ответ каталога по 001 утверждал «всё остальное чтение и
открытие изменений переведено на REST», и это было ЛОЖНО: 7 сентября в дереве
нашлось полтора десятка вызовов семейства `gh issue`/`gh pr`, а исчерпание
GraphQL уронило дежурного и заморозило очередь целиком.

Утверждение о транспорте держалось прозой — и разошлось с транспортом молча,
дважды за один день (второй раз — комментарий «ПО REST, А НЕ ЧЕРЕЗ GraphQL»
над вызовом `gh issue view --json`, идущим через GraphQL). Это ровно 146:
зелёным было то, что никто не проверял.

ЧТО СЧИТАЕТСЯ ПРЕДМЕТОМ. Вызов `gh` с подкомандой, которую gh исполняет через
GraphQL. Список семейств ниже — из документации gh и подтверждён живыми
отказами площадки, которые называют транспорт сами: «GraphQL: API rate limit
already exceeded» на `gh pr merge`, «GraphQL: Resource not accessible … 
(addComment)» на `gh issue comment`.

ЧТО НАХОДКОЙ НЕ ЯВЛЯЕТСЯ (правило 051 — гейт отвергает свой предмет):
  • `gh api <путь>` — это и есть REST, ради него всё и затевалось;
  • упоминание команды в комментарии или строке документации: там она названа,
    а не вызвана, и находка была бы о форме текста;
  • вызов, названный поимённо в `.rules/transport.json` с причиной — закрытый
    список исключений, которого требует само правило 001.

Реализует правила каталога:
  183 — комментарий «идём по REST» есть утверждение о вызове рядом, и оно
        сверяется с тем, каким API вызов идёт на самом деле;
  001 — находит вызовы к площадке, идущие через GraphQL, и требует либо REST,
        либо имени в закрытом списке исключений, которого требует само правило;
  102 — вторая половина того же списка: послабление существует только
        перечисленным. У каждой записи .rules/transport.json назван адрес и
        причина, а адрес, которого в списке нет, становится находкой —
        неперечисленное снисхождение не проходит. Строгого режима, снимающего
        послабления разом, здесь нет намеренно: запись одна, и переключать было
        бы нечего.

Исходы:
  0 — весь транспорт либо REST, либо назван поимённо;
  1 — есть вызов через GraphQL без имени в списке исключений;
  2 — проверка не отработала (файл списка не прочитан, дерево не разобрано).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
СПИСОК = ROOT / ".rules" / "transport.json"

#: Семейства подкоманд `gh`, которые исполняются через GraphQL. Ключ — первое
#: слово после `gh`; значение — что именно у него идёт по GraphQL.
ЧЕРЕЗ_GRAPHQL = {
    "issue": "чтение, создание и правка задач",
    "pr": "чтение, создание, правка и слияние изменений",
    "project": "Projects V2 — REST-эквивалента нет вовсе",
    "search": "поиск",
}

#: Строка в файле прогона, где команда вызывается, а не упоминается.
ВЫЗОВ_В_ОБОЛОЧКЕ = re.compile(r"^\s*(?:[\w.]+=\$\()?\s*gh\s+([a-z-]+)\b")


def исключения() -> tuple[dict[str, str] | None, str]:
    """Закрытый список названных поимённо. Вторая строка — причина отказа."""
    if not СПИСОК.exists():
        return None, f"{СПИСОК.relative_to(ROOT)} не найден — список исключений ведёт человек"
    try:
        d = json.loads(СПИСОК.read_text(encoding="utf-8"))
    except ValueError as e:
        return None, f"{СПИСОК.relative_to(ROOT)} не разобран — {e}"
    return {и["where"]: и.get("why", "") for и in d.get("allowed", [])}, ""


def в_питоне(текст: str, файл: str) -> list[tuple[str, str]]:
    """Вызовы gh через модуль-дверь. Разбором дерева, а не поиском подстроки.

    Комментарий и строка документации в дерево вызовов не попадают вовсе, и
    поэтому упоминание команды в прозе здесь не находка по построению.
    """
    try:
        дерево = ast.parse(текст)
    except SyntaxError:
        return []
    найдено: list[tuple[str, str]] = []
    for узел in ast.walk(дерево):
        if not isinstance(узел, ast.Call) or not узел.args:
            continue
        имя = узел.func
        зовут = (getattr(имя, "id", None) == "gh"
                 or getattr(имя, "attr", None) == "run")
        if not зовут:
            continue
        первый = узел.args[0]
        if not isinstance(первый, ast.Constant) or not isinstance(первый.value, str):
            continue
        под = первый.value
        if под in ЧЕРЕЗ_GRAPHQL:
            найдено.append((f"{файл}:{узел.lineno}", f"gh {под}"))
    return найдено


def в_оболочке(текст: str, файл: str) -> list[tuple[str, str]]:
    """Вызовы gh в блоках `run:` файла прогона. Комментарии пропускаются."""
    найдено: list[tuple[str, str]] = []
    for n, строка in enumerate(текст.splitlines(), 1):
        голая = строка.strip()
        if голая.startswith("#"):
            continue
        м = ВЫЗОВ_В_ОБОЛОЧКЕ.search(строка)
        if м and м.group(1) in ЧЕРЕЗ_GRAPHQL:
            найдено.append((f"{файл}:{n}", f"gh {м.group(1)}"))
    return найдено


def предметы(root: Path) -> list[tuple[str, str]]:
    """Все вызовы через GraphQL в дереве, с адресом каждого."""
    найдено: list[tuple[str, str]] = []
    for путь in sorted((root / "scripts").glob("*.py")):
        найдено += в_питоне(путь.read_text(encoding="utf-8"),
                            str(путь.relative_to(root)))
    места = sorted((root / ".github" / "workflows").glob("*.yml"))
    if (root / "action.yml").exists():
        места.append(root / "action.yml")
    for путь in места:
        найдено += в_оболочке(путь.read_text(encoding="utf-8"),
                              str(путь.relative_to(root)))
    return найдено


def selftest() -> int:
    случаи = [
        ('gh("issue", "list")', 1, "вызов задачи через дверь"),
        ('ghcli.run("pr", "list")', 1, "вызов изменения через дверь"),
        ('gh("api", "repos/{owner}/{repo}/issues")', 0, "REST находкой не является"),
        ('# gh issue list — так было раньше', 0, "упоминание в комментарии"),
        ('"""Раньше звали gh issue view."""', 0, "упоминание в документации"),
        ('gh("run", "list")', 0, "run идёт по REST"),
    ]
    плохо = []
    for текст, ждём, что in случаи:
        вышло = len(в_питоне(текст, "проба.py"))
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    оболочка = [
        ('            out=$(gh pr merge "$PR" --auto)', 1, "вызов в оболочке"),
        ('          # gh pr merge умеет только GraphQL', 0, "комментарий в оболочке"),
        ('            gh api "repos/$R/pulls/$PR"', 0, "REST в оболочке"),
    ]
    for текст, ждём, что in оболочка:
        вышло = len(в_оболочке(текст, "прогон.yml"))
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    for строка in плохо:
        print(f"РАСХОЖДЕНИЕ: {строка}", file=sys.stderr)
    if плохо:
        return 1
    print("самопроверка пройдена: вызов отличается от упоминания, REST — от GraphQL")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--selftest", action="store_true",
                   help="прогнать гейт по случаям, а не по дереву (140)")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()

    названы, err = исключения()
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    находки = [(где, что) for где, что in предметы(args.root) if где not in названы]
    if находки:
        print("транспорт разошёлся с объявленным — вызовы идут через GraphQL, "
              "а правило 001 требует REST:", file=sys.stderr)
        for где, что in находки:
            print(f"  • {где}: {что} — {ЧЕРЕЗ_GRAPHQL[что.split()[1]]}", file=sys.stderr)
        print("  Одна операция GraphQL стоит ~300 points из часовых 5000, REST — 1.\n"
              "  Либо переведите на `gh api`, либо назовите вызов поимённо в "
              f"{СПИСОК.relative_to(args.root)} с причиной, как требует само правило.",
              file=sys.stderr)
        return 1

    print(f"транспорт совпадает с объявленным: вызовов через GraphQL "
          f"{len(названы)}, и каждый назван поимённо")
    return 0


if __name__ == "__main__":
    sys.exit(main())
