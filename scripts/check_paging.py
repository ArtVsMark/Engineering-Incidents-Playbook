#!/usr/bin/env python3
"""Список, который площадка отдаёт страницами, читают до конца или с названным пределом.

ПОЧЕМУ ГЕЙТ, А НЕ ДОГОВОРЁННОСТЬ. Правило 212 записано 25 сентября по
перечню дерева: 19 чтений списков одним запросом, и у пятнадцати предел не
назван нигде. Их перевели на обход по перечню — и первый же прогон этого
гейта нашёл ещё два чтения одной страницей: проверки головы в
automerge.yml (страница по умолчанию, тридцать) и изменения коммита в
check_task_state.py. Пока список короче страницы, одиночный запрос неотличим
от обхода ни кодом, ни прогоном, ни подделкой в наборе: разница рождается у
живого списка, когда он дорос до края, и в этот момент никто не смотрит.

ЧТО СЧИТАЕТСЯ ПРЕДМЕТОМ. Чтение списка площадки одним запросом:
  • `gh api <путь>`, у которого последнее буквальное звено пути — имя
    коллекции (СПИСКИ ниже), метод — чтение, а `--paginate` нет;
  • `gh <что угодно> list` — `run`, `release`, `workflow`, `cache` и прочие:
    обхода страниц у подкоманды нет вовсе, только `--limit`, и без него
    предел — умолчание gh, которого никто не называл;
  • `gh api`, чей путь — выражение, а не строка: гейт его не прочтёт, и
    молча счесть его объектом значило бы пропустить то, ради чего гейт.
Вызов находится в питоне разбором дерева (любой вызов, чей первый аргумент —
строка "api" или второй — "list"; модуль-дверь зовётся по-разному: gh, run,
gh_json), в прогонах — по строке вызова после склейки переносов `\\`.
Формы взяты из справочника gh, а не из дерева: перечень, составленный по
встреченным формам, пропускает ту, что ещё не встретилась (210).

ЧТО НАХОДКОЙ НЕ ЯВЛЯЕТСЯ (правило 051 — гейт отвергает свой предмет):
  • `--paginate` и общий шов `ghcli.список()` — это и есть обход;
  • запись: `-X`/`--method` не GET, или поля `-f`/`-F`/`--input` — с ними
    gh сам меняет метод на POST;
  • одиночный объект: путь кончается подстановкой (`pulls/{n}`) или звеном
    из ОДИНОЧНЫЕ — страниц у него нет;
  • упоминание в комментарии или документации — в дерево вызовов оно не
    попадает, а строки-комментарии оболочки пропускаются;
  • предел, названный поимённо в `.rules/limits.json` с причиной, —
    закрытый список, как у каждого послабления каталога (102): «свежие N»
    — решение, а не забытый край.

НЕЗНАКОМОЕ ЗВЕНО — ОТКАЗ, А НЕ ПРОПУСК. Последнее буквальное звено, которого
нет ни в СПИСКАХ, ни в ОДИНОЧНЫХ, гейт не угадывает: новый адрес площадки
классифицирует человек, а до того он находка (075 — гейт, не знающий
предмета, молчать не должен).

Реализует правила каталога:
  212 — список площадки читается до конца; одиночный запрос законен только с
        пределом, названным поимённо и с причиной.

Исходы:
  0 — каждое чтение списка обходит страницы или названо с пределом;
  1 — есть чтение одной страницей без названного предела, незнакомое звено
      или запись таблицы, которой в дереве больше нет;
  2 — проверка не отработала (таблица не прочитана).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Коллекции площадки, которые отдаются страницами. Имя — последнее буквальное
#: звено пути; взято из справочника REST (у адреса есть `per_page`/`page`).
СПИСКИ = frozenset({
    "annotations", "artifacts", "branches", "check-runs", "check-suites",
    "collaborators", "comments", "commits", "events", "files", "issues",
    "jobs", "labels", "milestones", "pulls", "releases", "reviews", "runs",
    "statuses", "tags", "workflows",
})

#: Буквальные окончания адресов, которые отдают ОДИН объект или являются
#: действием. Страниц у них нет.
ОДИНОЧНЫЕ = frozenset({
    "dispatches", "merge", "protection", "rate_limit", "status",
})

#: Флаги `gh api`, за которыми идёт значение: их значение — не путь.
С_ЗНАЧЕНИЕМ = frozenset({
    "-X", "--method", "-H", "--header", "-q", "--jq", "-t", "--template",
    "-f", "--raw-field", "-F", "--field", "--input", "--cache", "-p",
    "--preview", "--hostname",
})

#: Флаги, с которыми gh отправляет тело, а значит меняет метод на POST.
С_ТЕЛОМ = frozenset({"-f", "--raw-field", "-F", "--field", "--input"})

#: Слова оболочки, на которых вызов кончается.
КОНЕЦ = frozenset({"|", "||", "&", "&&", ";", "then", "do"})

#: Вызов в строке оболочки: `gh api` или `gh run list` после начала строки,
#: пробела, `$(`, `(` или разделителя команд.
ВЫЗОВ_В_ОБОЛОЧКЕ = re.compile(r"(?:^|[\s(;|&])gh\s+(api|[a-z-]+\s+list)\b")


def звенья(путь: str) -> list[str]:
    """Звенья пути после репозитория, подстановки — `*`. Запрос отброшен."""
    части = [ч for ч in путь.split("?", 1)[0].strip("/").split("/") if ч]
    подстановка = [("{" in ч or "$" in ч) for ч in части]
    if части and части[0] == "repos":
        части, подстановка = части[1:], подстановка[1:]
        while части and подстановка[0]:
            части, подстановка = части[1:], подстановка[1:]
        # `repos/владелец/имя/…` буквально — два звена репозитория
        if части and not any(подстановка[:2]) and len(части) > 2:
            части, подстановка = части[2:], подстановка[2:]
    return ["*" if п else ч for ч, п in zip(части, подстановка)]


def разбор_api(слова: list[str]) -> tuple[str | None, bool, bool]:
    """Путь, обход страниц и чтение ли это — по словам после `gh api`."""
    путь: str | None = None
    обход = False
    метод: str | None = None
    тело = False
    i = 0
    while i < len(слова):
        с = слова[i]
        if с in КОНЕЦ or с.startswith(")"):
            break
        if с == "--paginate":
            обход = True
        elif с in С_ЗНАЧЕНИЕМ:
            if с in ("-X", "--method") and i + 1 < len(слова):
                метод = слова[i + 1].upper()
            if с in С_ТЕЛОМ:
                тело = True
            i += 1
        elif с.startswith("--method="):
            метод = с.split("=", 1)[1].upper()
        elif с.startswith("-"):
            pass
        elif путь is None:
            путь = с.rstrip(")")    # `$(gh api "путь")` — скобка подстановки
        i += 1
    чтение = метод == "GET" if метод else not тело
    return путь, обход, чтение


def предмет(слова: list[str]) -> str | None:
    """Что это за чтение списка одним запросом; None — не предмет гейта."""
    if len(слова) >= 2 and слова[1] == "list" and слова[0] != "api":
        return f"gh {слова[0]} list"
    if not слова or слова[0] != "api":
        return None
    путь, обход, чтение = разбор_api(слова[1:])
    if путь is None or обход or not чтение:
        return None
    if путь.strip() in ("{}", "*") or путь.startswith("$"):
        return "gh api <выражение>"
    з = звенья(путь)
    if not з or з[-1] == "*" or з[-1] in ОДИНОЧНЫЕ:
        return None
    return f"gh api {'/'.join(з)}"


def незнакомое(что: str) -> bool:
    """Последнее звено адреса не классифицировано ни как список, ни как объект."""
    if not что.startswith("gh api ") or что == "gh api <выражение>":
        return False
    хвост = что.rsplit("/", 1)[-1].split(" ")[-1]
    return хвост not in СПИСКИ and хвост not in ОДИНОЧНЫЕ


def строка_аргумента(узел: ast.expr) -> str | None:
    """Строка аргумента вызова; подстановка f-строки становится `{}`."""
    if isinstance(узел, ast.Constant) and isinstance(узел.value, str):
        return узел.value
    if isinstance(узел, ast.JoinedStr):
        return "".join(ч.value if isinstance(ч, ast.Constant) else "{}"
                       for ч in узел.values)
    return None


def в_питоне(текст: str, файл: str) -> list[tuple[str, str]]:
    """Чтения списков в питоне. Разбором дерева: проза вызовом не станет."""
    try:
        дерево = ast.parse(текст)
    except SyntaxError:
        return []
    найдено: list[tuple[str, str]] = []
    for узел in ast.walk(дерево):
        if not isinstance(узел, ast.Call) or not узел.args:
            continue
        аргументы = list(узел.args)
        # subprocess.run(["gh", "api", …]) — вызов списком, а не через дверь
        if isinstance(аргументы[0], ast.List):
            аргументы = list(аргументы[0].elts)
            if not аргументы or строка_аргумента(аргументы[0]) != "gh":
                continue
            аргументы = аргументы[1:]
        слова = [строка_аргумента(а) for а in аргументы]
        if not слова or not (слова[0] == "api" or слова[1:2] == ["list"]):
            continue
        # не строка (число, имя) — значение флага или путь-выражение
        слова = [с if с is not None else "{}" for с in слова]
        что = предмет(слова)
        if что:
            найдено.append((f"{файл}:{узел.lineno}", что))
    return найдено


def логические_строки(текст: str) -> list[tuple[int, str]]:
    """Строки оболочки со склеенными переносами `\\`, с номером первой."""
    вышло: list[tuple[int, str]] = []
    копим: list[str] = []
    первая = 0
    for n, строка in enumerate(текст.splitlines(), 1):
        if not копим:
            if строка.strip().startswith("#"):
                continue
            первая = n
        if строка.rstrip().endswith("\\"):
            копим.append(строка.rstrip()[:-1])
            continue
        копим.append(строка)
        вышло.append((первая, " ".join(копим)))
        копим = []
    if копим:
        вышло.append((первая, " ".join(копим)))
    return вышло


def слова_оболочки(хвост: str) -> list[str]:
    """Слова до первого места, которое не разбирается. Прочитанное — верно."""
    лексер = shlex.shlex(хвост, posix=True, punctuation_chars="|&;")
    лексер.whitespace_split = True
    слова: list[str] = []
    try:
        for слово in лексер:
            слова.append(слово)
    except ValueError:
        pass
    return слова


def в_оболочке(текст: str, файл: str) -> list[tuple[str, str]]:
    """Чтения списков в файле прогона. Комментарии пропускаются."""
    найдено: list[tuple[str, str]] = []
    for n, строка in логические_строки(текст):
        for м in ВЫЗОВ_В_ОБОЛОЧКЕ.finditer(строка):
            что = предмет(слова_оболочки(строка[м.start(1):]))
            if что:
                найдено.append((f"{файл}:{n}", что))
    return найдено


def предметы(root: Path) -> list[tuple[str, str]]:
    """Все чтения списков одним запросом в дереве, с адресом каждого."""
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


def таблица(root: Path) -> tuple[list[dict] | None, str]:
    """Пределы, названные поимённо. Вторая строка — причина отказа."""
    путь = root / ".rules" / "limits.json"
    имя = путь.relative_to(root)
    if not путь.exists():
        return None, f"{имя} не найден — пределы называет человек"
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


def сверка(найдено: list[tuple[str, str]],
           записи: list[dict]) -> tuple[list[tuple[str, str]], list[dict]]:
    """Находки без названного предела и записи таблицы, не нашедшие вызова."""
    ключи = {(з["where"], з["what"]) for з in записи}
    живые: set[tuple[str, str]] = set()
    без_предела: list[tuple[str, str]] = []
    for где, что in найдено:
        ключ = (где.rsplit(":", 1)[0], что)
        if ключ in ключи:
            живые.add(ключ)
        else:
            без_предела.append((где, что))
    мёртвые = [з for з in записи if (з["where"], з["what"]) not in живые]
    return без_предела, мёртвые


def selftest() -> int:
    """Гейт отличает обход от одной страницы, чтение от записи, объект от списка."""
    питон = [
        ('gh("api", f"repos/{{owner}}/{{repo}}/pulls?state=open")', 1, "список одной страницей"),
        ('gh("api", "--paginate", "repos/{owner}/{repo}/pulls")', 0, "обход страниц"),
        ('gh("api", f"repos/{{owner}}/{{repo}}/issues/{n}")', 0, "одиночный объект"),
        ('gh("api", "repos/{owner}/{repo}/issues", "-f", "title=x")', 0, "запись полями"),
        ('gh("api", "--method", "PATCH", f"repos/{r}/issues/{n}")', 0, "запись методом"),
        ('gh("api", "-X", "GET", "search/issues", "-f", "q=x")', 1, "чтение с полями при GET"),
        ('ghcli.run("api", f"repos/{r}/issues/{i}/comments")', 1, "комментарии через дверь"),
        ('gh("run", "list", "--limit", "40")', 1, "прогоны — всегда предел"),
        ('gh("release", "list")', 1, "любой list — предел умолчанием gh"),
        ('gh("api", путь)', 1, "путь-выражение не читается и не пропускается"),
        ('gh("api", "--paginate", путь)', 0, "путь-выражение с обходом"),
        ('subprocess.run(["gh", "api", "rate_limit"])', 0, "квота — объект"),
        ('# gh("api", "repos/x/y/pulls") — так было', 0, "упоминание в комментарии"),
    ]
    оболочка = [
        ('  open=$(gh api "repos/$R/pulls?state=open" --jq ".[]")', 1, "список в оболочке"),
        ('  gh api --paginate "repos/$R/pulls/$PR/files?per_page=100" \\\n'
         '    --jq ".[].filename"', 0, "обход с переносом строки"),
        ('  gh api "repos/$R/pulls/$PR" --jq .body', 0, "объект в оболочке"),
        ('  gh api "repos/$R/issues" \\\n    -f title="$T" >/dev/null', 0, "запись с переносом"),
        ('  # gh api "repos/$R/pulls" — одной страницей было', 0, "комментарий"),
        ('  gh run list --branch "$B" --limit 40 \\\n    --json conclusion', 1, "прогоны в оболочке"),
        ('  gh workflow list --all', 1, "list другой подкоманды"),
        ('  body=$(gh api "$URL" --jq .body)', 1, "путь-переменная в оболочке"),
    ]
    плохо = []
    for текст, ждём, что in питон:
        вышло = len(в_питоне(текст, "проба.py"))
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    for текст, ждём, что in оболочка:
        вышло = len(в_оболочке(текст, "прогон.yml"))
        print(f"  {'находка ' if вышло else 'чисто   '} — {что}")
        if вышло != ждём:
            плохо.append(f"{что}: ждали {ждём}, вышло {вышло}")
    if not незнакомое("gh api widgets") or незнакомое("gh api pulls/*/files"):
        плохо.append("незнакомое звено: классификация разошлась")
    for строка in плохо:
        print(f"РАСХОЖДЕНИЕ: {строка}", file=sys.stderr)
    if плохо:
        return 1
    print("самопроверка пройдена: обход отличается от одной страницы, "
          "запись — от чтения, объект — от списка")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--selftest", action="store_true",
                   help="прогнать гейт по случаям, а не по дереву (140)")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()

    записи, err = таблица(args.root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    найдено = предметы(args.root)
    без_предела, мёртвые = сверка(найдено, записи)
    незнакомые = [(где, что) for где, что in без_предела if незнакомое(что)]
    без_предела = [(где, что) for где, что in без_предела if not незнакомое(что)]
    имя = args.root / ".rules" / "limits.json"
    имя = имя.relative_to(args.root)

    плохо = False
    if без_предела:
        плохо = True
        print("список площадки читается одной страницей, и предел не назван (212):",
              file=sys.stderr)
        for где, что in без_предела:
            print(f"  • {где}: {что}", file=sys.stderr)
        print("  Пока список короче страницы, разницы не видно; дорос до края — "
              "хвост пропадает молча.\n"
              "  Либо обход (`gh api --paginate`, `ghcli.список()`), либо предел "
              f"поимённо в {имя} с причиной.", file=sys.stderr)
    if незнакомые:
        плохо = True
        print("адрес площадки не классифицирован — список это или объект, "
              "гейт не угадывает:", file=sys.stderr)
        for где, что in незнакомые:
            print(f"  • {где}: {что}", file=sys.stderr)
        print("  Назовите последнее звено в СПИСКАХ или ОДИНОЧНЫХ "
              "scripts/check_paging.py.", file=sys.stderr)
    if мёртвые:
        плохо = True
        print(f"записи {имя}, которым в дереве больше нечего разрешать (102):",
              file=sys.stderr)
        for з in мёртвые:
            print(f"  • {з['where']}: {з['what']}", file=sys.stderr)
        print("  Послабление без предмета снимают: иначе оно разрешит следующий "
              "вызов, о котором никто не думал.", file=sys.stderr)
    if плохо:
        return 1

    print(f"списки площадки читаются до конца: чтений одним запросом "
          f"{len(найдено)}, и у каждого предел назван в {имя}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
