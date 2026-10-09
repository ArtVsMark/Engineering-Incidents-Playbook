#!/usr/bin/env python3
"""Вызов наружу задаёт то, что иначе возьмёт у окружения: кодировку и разделитель.

ПОЧЕМУ ЭТО ОДИН ГЕЙТ, А НЕ ДВА. Предмет один — вызов `subprocess` в нашем
дереве, и оба вопроса задаются одним разбором. Два скрипта над одной
территорией разошлись бы в том, что считать вызовом, и разбор пришлось бы
держать в двух местах. Тот же довод записан у check_workflows.py.

ПЕРВОЕ ТРЕБОВАНИЕ — кодировка (правило 176).

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

ВТОРОЕ ТРЕБОВАНИЕ — разделитель списка путей (правило 165). Перечисляя пути из
git для последующего ЧТЕНИЯ, надо передавать `-z` и разбирать по NUL: иначе git
экранирует не-ASCII имена, построенный путь не разрешается, и файл молча
выпадает из обработки. Замер у каталога 3 сентября: семь мест брали список без
`-z`, четыре из них потом читали эти файлы.

ГРАНИЦА ВТОРОГО, И ОНА СТОИЛА РЕГРЕССИИ. У `git log --name-only -z` NUL'ами
разделяются ИМЕНА, а строка формата отдаётся как есть; разбор, переведённый на
NUL без `%x00` в формате, молча перестал находить даты — сборка сказала «правило
ещё не в истории» о правилах, которые в ней были. Поэтому гейт требует `-z`, а
верность разбора остаётся за автором.

ВТОРАЯ ПОЛОВИНА ВТОРОГО — `-z` без разбора по NUL (#762). Гейт держал только
команду, и `check_overlap` прошёл его с `-z` в вызове и голым `.split()` в
разборе: NUL не пробел, весь список склеивался в одно имя, и механизм 133
отвечал «пересечений нет» на любом дереве. Теперь вывод такого вызова,
разобранный `split()` без разделителя или `splitlines()`, — находка. Связь
вызова с разбором прослеживается ИМЕНЕМ в той же функции (`done = run(…)` →
`done.stdout.split()`) или цепочкой прямо на вызове. ГРАНИЦА, названная вслух:
вывод, переданный в другую функцию или собственной обёрткой над git
(`pr_source_commit.git`), разбором не прослеживается; формат `%x00` у `git log`
— тоже по-прежнему за автором.

ТРЕТЬЕ ТРЕБОВАНИЕ — `gh` зовут через `ghcli`, а не напрямую (правила 017, 058).
Оба правила держатся ОДНИМ модулем: он мерит остаток квоты при первом отказе и
отдаёт исчерпанию собственный терминальный код. Держатся они там ровно до тех
пор, пока дверь одна: вызов `gh` мимо `ghcli` получает от площадки код 1, и
«лимит кончился» снова становится неотличимо от «ничего не нашлось». Замер при
заведении: в scripts/ обходов нет ни одного — требование заводится ДО первого
нарушения, а не после, потому что цена нарушения известна (2 сентября: agent-pr
упал на первой команде, четыре изменения подряд не открылись, никто не покраснел).

ГРАНИЦА ТРЕТЬЕГО: сам `ghcli.py` и оболочка прогонов. Модулю звать `gh` положено
— он и есть дверь. Шаги прогонов зовут `gh` строкой оболочки, и разбором питона
они не видны вовсе; это названо здесь вслух, а не замолчано (075).

Реализует правила каталога:
  176 — умолчание, взятое из окружения, задаётся явно;
  165 — список путей из git читается по NUL, а проверка называет охват;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — ноль просмотренных файлов это отказ, а не чистый прогон;
  165 — печатается ОХВАТ: сколько файлов просмотрено, а не только находки;
  165 — вывод `-z` разбирается по NUL, а не `split()` без разделителя;
  180 — предмет разрешается по импортам разбираемого файла, а не по
        последнему звену имени вызова;
  017 — остаток квоты мерится, а не угадывается: мерит ghcli, и потому звать
        площадку мимо него нельзя;
  058 — исчерпав квоту, работа останавливается: терминальный код живёт в
        ghcli, и обход двери его теряет.
"""


import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Ключи, включающие текстовый режим. Любого достаточно, и это свойство
#: CPython, а не наше соглашение.
TEXT_KEYS = ("text", "universal_newlines", "errors")

#: Вызовы subprocess, у которых бывает текстовый режим. Это ИСХОДНЫЕ имена в
#: модуле, а не то, как вызов записан в файле: разрешение до исходного имени —
#: работа resolve_calls (правило 180).
CALLS = ("run", "check_output", "Popen", "check_call", "call")

#: Подкоманды и ключи git, отдающие СПИСОК ПУТЕЙ. Только они требуют `-z`:
#: у `git rev-parse` или `git describe` списка нет, и требовать от них
#: разделитель значило бы краснеть на верном вызове (051).
LISTING = ("ls-files", "--name-only", "--porcelain", "--diff-filter")

#: Кому звать `gh` напрямую положено. Список разрешительный и с причиной у
#: каждой строки: запретительный («всё, кроме…») завтра пропустит новый файл.
ДВЕРЬ = {
    "ghcli.py": "он и есть дверь: мерит остаток и отдаёт исчерпанию свой код",
}



def resolve_calls(tree: ast.AST) -> tuple[set[str], dict[str, str]]:
    """Как subprocess назван В ЭТОМ ФАЙЛЕ: имена модуля и псевдонимы функций.

    ПОЧЕМУ НЕ ПО ПОСЛЕДНЕМУ ЗВЕНУ ИМЕНИ (правило 180). Совпадение звена ничего
    не доказывает: в дереве каталога ДВЕНАДЦАТЬ своих функций с именем `run`.
    Сегодня они не попадают в находки лишь потому, что триггером служит
    `text=`, которого у своих функций не бывает, — то есть по счастливой
    случайности, а не по построению. У потребителя такая же конструкция с более
    широким триггером дала 17 ложных находок из 48, автоматическая правка
    дописала своим функциям несуществующий параметр, и пятнадцать тестов упали.

    ОБРАТНАЯ ПОЛОВИНА ТОГО ЖЕ, и у нас она была открыта полностью: вызов через
    `from subprocess import run as ...` по последнему звену не находился вовсе —
    гейт зеленел ровно за отсутствие того, чего не умел увидеть (146).

    Возвращает: имена, под которыми доступен САМ МОДУЛЬ, и отображение
    «имя в файле → исходное имя функции».
    """
    модули: set[str] = set()
    функции: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "subprocess":
                    модули.add(a.asname or "subprocess")
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for a in node.names:
                функции[a.asname or a.name] = a.name
    return модули, функции


def called_name(node: ast.Call, модули: set[str],
                функции: dict[str, str]) -> str:
    """Исходное имя функции subprocess у этого вызова; пусто — вызов чужой."""
    if isinstance(node.func, ast.Attribute):
        владелец = node.func.value
        if isinstance(владелец, ast.Name) and владелец.id in модули:
            return node.func.attr
        return ""
    if isinstance(node.func, ast.Name):
        return функции.get(node.func.id, "")
    return ""

def offenders(source: str) -> list[tuple[int, str]]:
    """Строки текстовых вызовов без `encoding=`. Разбор дерева, а не поиск строк.

    Поиск подстрокой здесь дал бы ложные находки на слове `text=True` в
    докстроке и пропустил бы вызов, разложенный по строкам (166: проверка
    отношения через присутствие подстроки зеленеет там, где отношения нет).

    Предмет определяется по ИМПОРТАМ файла, а не по последнему звену имени
    вызова (180) — см. resolve_calls.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    модули, функции = resolve_calls(tree)
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        имя = called_name(node, модули, функции)
        if имя not in CALLS:
            continue
        ключи = {kw.arg for kw in node.keywords if kw.arg}
        if not (ключи & set(TEXT_KEYS)):
            continue
        if "encoding" in ключи:
            continue
        found.append((node.lineno, имя))
    return found


def unseparated(source: str) -> list[tuple[int, str]]:
    """Строки вызовов git, отдающих список путей без `-z`.

    Разбор дерева, а не поиск строки: аргументы вызова часто разложены по
    строкам, и поиск подстроки не увидел бы связи между командой и ключом
    (166 — проверка отношения через присутствие подстроки).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        слова = [a.value for a in ast.walk(node)
                 if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if "git" not in слова:
            continue
        подкоманда = next((с for с in слова if с in LISTING), "")
        if not подкоманда:
            continue
        # ВТОРОЙ ЗАКОННЫЙ ОТВЕТ, и он найден живым отказом. `-c
        # core.quotePath=false` снимает ту же поломку с другой стороны: git
        # перестаёт экранировать не-ASCII имена вовсе, и разбор по строкам
        # снова верен. Два места в дереве отвечали именно так, и их докстроки
        # это объясняют — красное на них было бы ложным (051).
        #
        # ЧТО ЭТОТ ОТВЕТ НЕ ЗАКРЫВАЕТ, названо вслух: имя с переносом строки. У
        # `-z` такой границы нет, поэтому он остаётся предпочтительным, а
        # quotePath — принимается, а не рекомендуется.
        if "-z" in слова or "core.quotePath=false" in слова:
            continue
        found.append((node.lineno, подкоманда))
    return found


#: Методы, режущие строку. Находка — любой из них на выводе `-z`, кроме
#: `split("\0")`: `split()` и `split(None)` режут по пробельным, `split("\n")`
#: и `splitlines()` — по переводам строк, и никто из них не видит `\0` (#762,
#: ревью #764).
РЕЖУЩИЕ = ("split", "rsplit", "splitlines")

#: Узлы, открывающие СВОЮ область имён: внутри — свои переменные, и имя
#: внешней функции к ним отношения не имеет (ревью #764).
ОБЛАСТИ = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def _списочный_z(node: ast.AST) -> bool:
    """Вызов git, отдающий список путей с `-z`: его вывод режется по NUL."""
    if not isinstance(node, ast.Call):
        return False
    слова = [a.value for a in ast.walk(node)
             if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    return ("git" in слова and "-z" in слова
            and any(с in LISTING for с in слова))


def _корень(node: ast.AST) -> ast.AST:
    """Начало цепочки `done.stdout.strip()[…]` — то, к чему привязан разбор.

    Цепочка идёт и сквозь вызовы методов: `.strip().split("\\n")` режет тот
    же вывод (ревью #764). Останавливается на самом вызове git с `-z`.
    """
    while not _списочный_z(node):
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            node = node.func.value
        else:
            break
    return node


def _режет_не_по_nul(call: ast.Call) -> bool:
    """Разбор, который NUL разделителем не считает.

    Разделитель-переменная находкой не считается: чему она равна, разбор
    исходника не знает, и красное на ней было бы догадкой (051).
    """
    if call.func.attr == "splitlines":
        return True
    sep = call.args[0] if call.args else next(
        (k.value for k in call.keywords if k.arg == "sep"), None)
    if sep is None:
        return True
    if isinstance(sep, ast.Constant):
        return sep.value != "\0"
    return False


def _узлы_области(корень: ast.AST) -> list[ast.AST]:
    """Узлы одной области имён — без тел вложенных функций и лямбд."""
    out: list[ast.AST] = []
    стек = list(ast.iter_child_nodes(корень))
    while стек:
        n = стек.pop()
        out.append(n)
        if not isinstance(n, ОБЛАСТИ):
            стек.extend(ast.iter_child_nodes(n))
    return out


def _имена(target: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}


def unsplit(source: str) -> list[tuple[int, str]]:
    """Строки, где вывод `git … -z` разобран не по NUL.

    Предмет — ОТНОШЕНИЕ вызова и разбора, а не присутствие `.split()` в файле
    (166). Связь прослеживается в ОДНОЙ области имён и В ПОРЯДКЕ ИСХОДНИКА:
    присваивание из вызова с `-z` связывает имя, любое другое присваивание
    того же имени — развязывает (`d = d.stdout.split("\\0")` делает `d`
    списком, и `.split()` на нём уже не находка — ревью #764). Цепочка прямо
    на вызове связана всегда.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found: list[tuple[int, str]] = []
    области = [tree, *(n for n in ast.walk(tree) if isinstance(n, ОБЛАСТИ))]
    for область in области:
        # События области по месту в исходнике. Присваивание срабатывает в
        # КОНЦЕ своего узла: правая часть вычисляется до привязки имени.
        события: list[tuple[tuple[int, int], int, str, ast.AST]] = []
        for n in _узлы_области(область):
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr)) \
                    and n.value is not None:
                цели = (n.targets if isinstance(n, ast.Assign) else [n.target])
                связать = any(_списочный_z(m) for m in ast.walk(n.value))
                for ц in цели:
                    for имя in _имена(ц):
                        события.append(((n.end_lineno, n.end_col_offset), 1,
                                        "связать" if связать else "развязать",
                                        ast.Name(id=имя)))
            elif isinstance(n, (ast.For, ast.AsyncFor, ast.With)):
                цели = ([n.target] if isinstance(n, (ast.For, ast.AsyncFor))
                        else [i.optional_vars for i in n.items if i.optional_vars])
                for ц in цели:
                    for имя in _имена(ц):
                        события.append(((ц.lineno, ц.col_offset), 1,
                                        "развязать", ast.Name(id=имя)))
            elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in РЕЖУЩИЕ and _режет_не_по_nul(n)):
                события.append(((n.lineno, n.col_offset), 0, "разбор", n))
        связанные: set[str] = set()
        for _, _, что, n in sorted(события, key=lambda e: (e[0], e[1])):
            if что == "связать":
                связанные.add(n.id)
            elif что == "развязать":
                связанные.discard(n.id)
            else:
                корень = _корень(n.func.value)
                if ((isinstance(корень, ast.Name) and корень.id in связанные)
                        or _списочный_z(корень)):
                    found.append((n.lineno, n.func.attr))
    return sorted(set(found))


def мимо_двери(source: str) -> list[int]:
    """Строки, где `gh` зовут подпроцессом напрямую.

    Предмет — ПЕРВОЕ СЛОВО списка аргументов, а не наличие строки «gh» где-то в
    вызове: `shutil.which("gh")` подпроцесс не запускает вовсе, а
    `["git", "log"]` содержит «g» и «h» в разных местах. Проверка отношения
    через присутствие подстроки зеленеет там, где отношения нет (166), и здесь
    краснела бы там, где его нет.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        имя = (getattr(node.func, "attr", None)
               or getattr(node.func, "id", None) or "")
        if имя not in CALLS:
            continue
        первый = node.args[0]
        if isinstance(первый, (ast.List, ast.Tuple)) and первый.elts:
            голова = первый.elts[0]
        else:
            голова = первый
        if isinstance(голова, ast.Constant) and голова.value == "gh":
            found.append(node.lineno)
    return sorted(set(found))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    файлы = sorted(list((args.root / "scripts").glob("*.py"))
                   + list((args.root / "tests").glob("*.py"))
                   + list((args.root / "templates").glob("*.py")))
    # ── исход 2 ────────────────────────────────────────────────────────────
    if not файлы:
        print(f"проверка не отработала: в {args.root}/{{scripts,tests,"
              "templates}} не нашлось ни одного *.py — проверять нечего, и "
              "зеленеть на этом нельзя", file=sys.stderr)
        return 2

    находки: list[str] = []
    for f in файлы:
        текст = f.read_text(encoding="utf-8", errors="replace")
        for строка, имя in offenders(текст):
            находки.append(f"{f.relative_to(args.root)}:{строка} — "
                           f"subprocess.{имя} в текстовом режиме без encoding=")
        for строка, подкоманда in unseparated(текст):
            находки.append(f"{f.relative_to(args.root)}:{строка} — "
                           f"git {подкоманда} отдаёт список путей без -z")
        for строка, разбор in unsplit(текст):
            находки.append(f"{f.relative_to(args.root)}:{строка} — "
                           f"вывод git -z режется {разбор}(), а не по NUL")
        if f.name not in ДВЕРЬ:
            for строка in мимо_двери(текст):
                находки.append(f"{f.relative_to(args.root)}:{строка} — "
                               "gh зовут мимо scripts/ghcli.py")

    # ── исход 1 ────────────────────────────────────────────────────────────
    if находки:
        print("вызовы наружу берут у окружения то, что обязаны задать:",
              file=sys.stderr)
        for n in находки:
            print(f"  • {n}", file=sys.stderr)
        print("\n  Кодировка: допишите encoding=\"utf-8\" — матрица этого не"
              "\n  поймает, дефект требует совпадения платформы и данных (176)."
              "\n  Список путей: допишите -z и разбирайте по NUL — иначе"
              "\n  не-ASCII имя выпадет из обработки молча (165)."
              "\n  Площадка: зовите через ghcli.run — он мерит остаток квоты при"
              "\n  первом отказе и отдаёт исчерпанию свой код; мимо двери «лимит"
              "\n  кончился» неотличимо от «ничего не нашлось» (017, 058).",
              file=sys.stderr)
        return 1

    print("вызовы наружу задают своё явно: просмотрено файлов "
          f"{len(файлы)} — кодировка у текстовых, -z у списков путей, "
          "площадка через одну дверь")
    return 0


if __name__ == "__main__":
    sys.exit(main())
