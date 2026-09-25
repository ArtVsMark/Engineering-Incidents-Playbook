#!/usr/bin/env python3
"""Имя рабочего кода, до которого не доходит рабочий путь, — сирота, даже с зелёным набором.

ПОЧЕМУ ГЕЙТ, А НЕ ДОГОВОРЁННОСТЬ. Правило 211 записано 25 сентября по замеру:
двенадцать имён на 62 модуля, и среди них две настоящие сироты, обе от
постройки соседа, делающего то же и больше. `sync_inbox.contract_gap`
пятнадцать дней держала четыре зелёных утверждения набора о коде, который не
исполнялся ни одним рабочим путём. Обрыв лежит не в механизме, а между ним и
зовущим: отсутствие вызова не попадает ни в один дифф, и чтение его не видит.

ЧТО СЧИТАЕТСЯ ПРЕДМЕТОМ. Имя верхнего уровня модуля рабочего кода —
`scripts/*.py` и `.claude/hooks/*.py`: функция, класс, присвоенное имя.
Сирота — имя, которое не достигается от корней. Корни — то, что исполняется
при запуске или импорте модуля: операторы верхнего уровня, кроме объявлений
(в их числе `if __name__ == "__main__"`), декораторы, значения по умолчанию,
вызовы в значении присваивания (`X = f()` исполняет f, `X = f` — нет) и тело
класса. Тело lambda и генератора ленивы и корнем не считаются.
Дальше достижимость идёт по телам достигнутых имён: обращение к своему
имени, `from модуль import имя`, `модуль.имя` через `import модуль`.

ТРАНЗИТИВНО, А НЕ ОДНИМ УРОВНЕМ. Замер правила считал имя живым, если его
читает хоть кто-то, — и имя, которое зовёт одна сирота, в него не попадало;
правило само назвало это нижней границей. Здесь живо только то, до чего
доходит цепочка от корня.

ЧТО НАХОДКОЙ НЕ ЯВЛЯЕТСЯ (051 — гейт отвергает свой предмет):
  • набор: `tests/` рабочим путём не является, и его обращения не считаются —
    ради этого гейт и построен;
  • `main` и имена с двойным подчёркиванием — их зовёт интерпретатор;
  • законный сосед, названный поимённо в `.rules/orphans.json` с причиной:
    закрытая роспись для набора, граница, адресованная человеку, — рабочим
    путём не достигаются по построению (211 называет их сам). Список закрыт,
    как у каждого послабления каталога (102), и запись без предмета — отказ.

ГРАНИЦА. Обращение по строке — `getattr(модуль, "имя")`, `globals()["имя"]` —
разбором не видно; такое имя называется в списке. Методы классов гейт не
разбирает: класс достигнут — достигнуто всё его тело. Модуль целиком, которого
не запускает ни прогон, ни хук, ни команда свода, гейт не ищет: корни каждого
модуля он считает исполняемыми.

Реализует правила каталога:
  211 — механизм жив, пока до него доходит рабочий путь: имя рабочего кода,
        которого рабочий код не достигает, — находка, а законный сосед назван
        поимённо с причиной.

Исходы:
  0 — каждое имя рабочего кода достигается или названо соседом;
  1 — есть сирота или запись списка, которой нечего разрешать;
  2 — проверка не отработала (список не прочитан, модуль не разобран).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Где лежит рабочий код: то, что исполняют прогон, хук и команда из свода.
РАБОЧИЙ_КОД = ("scripts", ".claude/hooks")

Имя = tuple[str, str]          # (модуль, имя)


def объявления(дерево: ast.Module) -> dict[str, ast.stmt]:
    """Имена верхнего уровня и узел, который их объявляет."""
    вышло: dict[str, ast.stmt] = {}
    for узел in дерево.body:
        if isinstance(узел, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            вышло[узел.name] = узел
        elif isinstance(узел, ast.Assign):
            for цель in узел.targets:
                if isinstance(цель, ast.Name):
                    вышло[цель.id] = узел
        elif isinstance(узел, ast.AnnAssign) and isinstance(узел.target, ast.Name):
            вышло[узел.target.id] = узел
    return вышло


def вызовы_при_импорте(выражение: ast.AST) -> list[ast.Call]:
    """Вызовы, которые выражение исполняет сразу, а не когда-нибудь потом.

    ФОРМЫ — ПО ГРАММАТИКЕ, А НЕ ПО ВСТРЕЧЕННЫМ (210). Вторая находка обзора в
    одном месте (#611, затем #612: `(lambda: f())()` и генератор) — повод
    перечислить все ленивые формы выражения, а не залатать две названные:
      • lambda — тело ленивое, умолчания аргументов вычисляются сразу;
      • генератор — ленивый, кроме первого итерируемого: он вычисляется сразу;
      • вызов берётся ЦЕЛИКОМ, со всем поддеревом: `(lambda: f())()` исполняет
        тело, а что вызванный сделает с аргументом-функцией, разбор не знает.
        Счесть такое живым безопаснее, чем назвать живое сиротой (051).
    Списочные, множественные и словарные включения исполняются сразу и
    разбираются как обычное поддерево.
    """
    вышло: list[ast.Call] = []
    очередь: list[ast.AST] = [выражение]
    while очередь:
        у = очередь.pop()
        if isinstance(у, ast.Call):
            вышло.append(у)
            continue
        if isinstance(у, ast.Lambda):
            очередь += у.args.defaults + [д for д in у.args.kw_defaults if д]
            continue
        if isinstance(у, ast.GeneratorExp):
            очередь.append(у.generators[0].iter)
            continue
        очередь += ast.iter_child_nodes(у)
    return вышло


class Модуль:
    """Разобранный модуль: объявления, импорты и корни."""

    def __init__(self, имя: str, путь: Path, дерево: ast.Module, свои: set[str]) -> None:
        self.имя = имя
        self.путь = путь
        self.объявлено = объявления(дерево)
        self.псевдонимы: dict[str, str] = {}      # имя в модуле → модуль каталога
        self.ввезено: dict[str, Имя] = {}         # имя в модуле → (модуль, имя)
        for узел in ast.walk(дерево):
            if isinstance(узел, ast.Import):
                for а in узел.names:
                    if а.name in свои:
                        self.псевдонимы[а.asname or а.name] = а.name
            elif isinstance(узел, ast.ImportFrom) and узел.module in свои:
                for а in узел.names:
                    self.ввезено[а.asname or а.name] = (узел.module, а.name)
        self.корни: list[ast.AST] = []
        self.корни_тела(дерево.body)

    def корни_тела(self, тело: list[ast.stmt]) -> None:
        """Корни из операторов, которые исполняются при импорте модуля."""
        for узел in тело:
            if isinstance(узел, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # исполняются при определении: декораторы и умолчания
                self.корни += узел.decorator_list
                self.корни += узел.args.defaults + [у for у in узел.args.kw_defaults if у]
            elif isinstance(узел, ast.ClassDef):
                self.корни += узел.decorator_list
                self.корни += узел.bases + [к.value for к in узел.keywords]
                # ТЕЛО КЛАССА ИСПОЛНЯЕТСЯ ПРИ ЕГО ОПРЕДЕЛЕНИИ, то есть при
                # импорте, даже если на класс не ссылается никто: `x = f()` в
                # нём зовёт f. Методы — нет: у них, как и у функций, сразу
                # вычисляются только декораторы и умолчания.
                self.корни_тела(узел.body)
            elif isinstance(узел, (ast.Assign, ast.AnnAssign)):
                # ЗНАЧЕНИЕ ПРИСВАИВАНИЯ ЛЕНИВО, ВЫЗОВ В НЁМ — НЕТ. `X = f()`
                # исполняет f при каждом импорте, прочитают X или нет, и f
                # живая (находка обзора на #611). А `X = f` и `Y = [X]` лишь
                # ссылаются: мёртвая константа не должна держать живым то, на
                # что ссылается, — иначе вернулся бы одноуровневый замер.
                if узел.value is not None:
                    self.корни += вызовы_при_импорте(узел.value)
            else:
                self.корни.append(узел)

    def обращения(self, узел: ast.AST) -> set[Имя]:
        """Имена каталога, к которым обращается поддерево."""
        вышло: set[Имя] = set()
        for у in ast.walk(узел):
            if isinstance(у, ast.Name) and isinstance(у.ctx, ast.Load):
                if у.id in self.объявлено:
                    вышло.add((self.имя, у.id))
                elif у.id in self.ввезено:
                    вышло.add(self.ввезено[у.id])
            elif (isinstance(у, ast.Attribute) and isinstance(у.value, ast.Name)
                  and у.value.id in self.псевдонимы):
                вышло.add((self.псевдонимы[у.value.id], у.attr))
        return вышло


def модули(root: Path) -> tuple[dict[str, Модуль] | None, str]:
    """Разобранный рабочий код. Вторая строка — причина отказа."""
    пути = [п for папка in РАБОЧИЙ_КОД for п in sorted((root / папка).glob("*.py"))]
    имена = {п.stem for п in пути}
    вышло: dict[str, Модуль] = {}
    for п in пути:
        try:
            дерево = ast.parse(п.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError) as e:
            return None, f"{п.relative_to(root)} не разобран — {e}"
        вышло[п.stem] = Модуль(п.stem, п, дерево, имена)
    return вышло, ""


def достигнутые(мод: dict[str, Модуль]) -> set[Имя]:
    """Имена, до которых доходит цепочка от корней рабочего кода."""
    очередь: list[Имя] = []
    for м in мод.values():
        for корень in м.корни:
            очередь += м.обращения(корень)
    видели: set[Имя] = set()
    while очередь:
        имя = очередь.pop()
        if имя in видели:
            continue
        видели.add(имя)
        м = мод.get(имя[0])
        узел = м.объявлено.get(имя[1]) if м else None
        if узел is not None:
            очередь += м.обращения(узел)
    return видели


def сироты(мод: dict[str, Модуль], root: Path) -> list[tuple[str, str]]:
    """(файл, имя) каждого имени рабочего кода, которое не достигается."""
    живые = достигнутые(мод)
    вышло: list[tuple[str, str]] = []
    for м in мод.values():
        for имя in м.объявлено:
            if имя == "main" or имя.startswith("__"):
                continue
            if (м.имя, имя) not in живые:
                вышло.append((str(м.путь.relative_to(root)), имя))
    return вышло


def соседи(root: Path) -> tuple[list[dict] | None, str]:
    """Законные соседи, названные поимённо. Вторая строка — причина отказа."""
    путь = root / ".rules" / "orphans.json"
    имя = путь.relative_to(root)
    if not путь.exists():
        return None, f"{имя} не найден — законных соседей называет человек"
    try:
        d = json.loads(путь.read_text(encoding="utf-8"))
    except ValueError as e:
        return None, f"{имя} не разобран — {e}"
    записи = d.get("allowed")
    if not isinstance(записи, list):
        return None, f"{имя}: нет списка allowed"
    for з in записи:
        if not (isinstance(з, dict) and з.get("where") and з.get("what")
                and str(з.get("why", "")).strip()):
            return None, f"{имя}: у записи нет where, what или why — {з}"
    return записи, ""


def selftest() -> int:
    """Гейт отличает достигнутое от сироты, в том числе через цепочку и импорт."""
    import tempfile
    случаи = [
        ("зовёт main", {"a": "def f(): pass\ndef main(): f()\n"
                        "if __name__ == '__main__': main()\n"}, set()),
        ("никто не зовёт", {"a": "def f(): pass\ndef main(): pass\n"
                            "if __name__ == '__main__': main()\n"}, {"f"}),
        ("зовёт одна сирота — тоже сирота",
         {"a": "def g(): pass\ndef f(): g()\ndef main(): pass\n"
               "if __name__ == '__main__': main()\n"}, {"f", "g"}),
        ("через import модуль",
         {"a": "import b\ndef main(): b.f()\nif __name__ == '__main__': main()\n",
          "b": "def f(): pass\ndef h(): pass\n"}, {"h"}),
        ("через from модуль import",
         {"a": "from b import f\ndef main(): f()\nif __name__ == '__main__': main()\n",
          "b": "def f(): pass\n"}, set()),
        ("константа в значении другой константы",
         {"a": "X = 1\nY = [X]\ndef main(): print(Y)\n"
               "if __name__ == '__main__': main()\n"}, set()),
        ("одноимённое в соседнем модуле не спасает",
         {"a": "ROOT = 1\ndef main(): pass\nif __name__ == '__main__': main()\n",
          "b": "ROOT = 2\nprint(ROOT)\n"}, {"ROOT"}),
        ("декоратор исполняется при импорте",
         {"a": "def d(f): return f\n@d\ndef g(): pass\n"}, {"g"}),
        ("вызов в значении присваивания исполняется, даже если имя не читают",
         {"a": "def f(): return 1\nX = f()\n"}, {"X"}),
        ("ссылка в значении мёртвой константы не держит функцию",
         {"a": "def f(): return 1\nX = f\n"}, {"X", "f"}),
        ("вызов в теле lambda при импорте не исполняется",
         {"a": "def f(): return 1\nX = lambda: f()\n"}, {"X", "f"}),
        ("lambda, вызванная сразу, исполняет тело",
         {"a": "def f(): return 1\nX = (lambda: f())()\n"}, {"X"}),
        ("умолчание lambda вычисляется сразу",
         {"a": "def f(): return 1\nX = lambda y=f(): y\n"}, {"X"}),
        ("тело генератора ленивое",
         {"a": "def f(): return 1\nX = (f() for _ in range(2))\n"}, {"X", "f"}),
        ("первый итерируемый генератора вычисляется сразу",
         {"a": "def f(): return []\nX = (i for i in f())\n"}, {"X"}),
        ("тело класса исполняется при импорте",
         {"a": "def f(): return 1\nclass A:\n    x = f()\n"}, {"A"}),
        ("метод класса не исполняется при импорте",
         {"a": "def f(): return 1\nclass A:\n    def m(self): f()\n"}, {"A", "f"}),
    ]
    плохо = []
    for что, файлы, ждём in случаи:
        with tempfile.TemporaryDirectory() as t:
            корень = Path(t)
            (корень / "scripts").mkdir()
            for имя, текст in файлы.items():
                (корень / "scripts" / f"{имя}.py").write_text(текст, encoding="utf-8")
            мод, _ = модули(корень)
            вышло = {имя for _, имя in сироты(мод, корень)}
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {sorted(ждём)}, вышло {sorted(вышло)}")
    for строка in плохо:
        print(f"РАСХОЖДЕНИЕ: {строка}", file=sys.stderr)
    if плохо:
        return 1
    print("самопроверка пройдена: достижимость идёт цепочкой от корня, "
          "набор и одноимённое её не заменяют")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--selftest", action="store_true",
                   help="прогнать гейт по случаям, а не по дереву (140)")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()

    записи, err = соседи(args.root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2
    мод, err = модули(args.root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    названы = {(з["where"], з["what"]) for з in записи}
    найдено = сироты(мод, args.root)
    настоящие = [(ф, и) for ф, и in найдено if (ф, и) not in названы]
    мёртвые = [з for з in записи if (з["where"], з["what"]) not in set(найдено)]
    плохо = False
    if настоящие:
        плохо = True
        print("имя рабочего кода не достигается ни одним рабочим путём (211):",
              file=sys.stderr)
        for файл, имя in настоящие:
            print(f"  • {файл}::{имя}", file=sys.stderr)
        print("  Набор, зовущий его напрямую, здесь не доказательство: он зелёный и "
              "тогда, когда путь оборван.\n"
              "  Либо позовите его из рабочего пути, либо удалите, либо назовите "
              "законным соседом в .rules/orphans.json с причиной.", file=sys.stderr)
    if мёртвые:
        плохо = True
        print("записи .rules/orphans.json, которым в дереве больше нечего "
              "разрешать (102):", file=sys.stderr)
        for з in мёртвые:
            print(f"  • {з['where']}::{з['what']}", file=sys.stderr)
    if плохо:
        return 1

    всего = sum(len(м.объявлено) for м in мод.values())
    print(f"рабочий путь доходит до каждого имени: имён {всего} в {len(мод)} "
          f"модулях, законных соседей {len(записи)}, и каждый назван с причиной")
    return 0


if __name__ == "__main__":
    sys.exit(main())
