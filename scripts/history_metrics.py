#!/usr/bin/env python3
"""У каждого выпуска есть строка в «Эволюции метрик», и её числа сверены с тегом.

Таблица в `HISTORY.md` держалась договорённостью «дописать строку при выпуске».
Договорённость сломалась молча: после `v0.1.0` вышли `v1.0.0` и `v1.1.0`, и ни
одной строки никто не добавил. Заметил это владелец через два выпуска — то
есть механизма у таблицы не было вовсе (правило 002), а число в прозе держалось
обещанием (005).

ЧТО ПРОВЕРЯЕТСЯ.

  • у каждого тега выпуска есть своя строка, а у каждой строки — свой тег;
  • числа в строке равны СНИМКУ, вычисленному по дереву самого тега: правил,
    областей, локальных ссылок, «не обеспечено ничем» из действующих ответов;
  • «Ключевое» непусто и не содержит ссылок.

ПОЧЕМУ ССЫЛКА В «КЛЮЧЕВОМ» ЗАПРЕЩЕНА. Строка живёт в том же дереве, по
которому её и сверяют: ссылка в ячейке увеличила бы число ссылок в этом дереве
на единицу, и строка стала бы неверной о самой себе. Ограничение дешёвое —
ячейка на одну фразу, — а без него гейт краснел бы на верной работе (051).

ПОЧЕМУ «НИЧЕМ» ЗАПИСАНО ДРОБЬЮ. Восемь у `v1.0.0` и сорок один у `v1.1.0` —
это не ухудшение: между выпусками выросло само число ОТВЕТОВ, с 51 до 110.
Голое число сравнивало бы несравнимое, и метрика врала бы в ту сторону, в
какую метрике врать нельзя (041, 146). Знаменатель ставит её на место.

ЧЕГО ЗДЕСЬ НЕТ. Суждения о том, верно ли названо «Ключевое»: что именно
принёс выпуск, машина не знает, и колонку заполняет человек кнопкой выпуска.
Гейт держит числа и форму.

Реализует правила каталога:
  005 — число, вписанное руками, протухает: снимок выпуска сверяется с деревом
        тега, а не с памятью автора;
  002 — «не забыть дописать строку» механизмом не является, и это измерено
        двумя пропущенными выпусками;
  049 — состояние выводится из живого артефакта: числа считает сборка по тегу,
        а не реестр, который ведут руками;
  120 — метрика «не обеспечено ничем» обязана уменьшаться, а увидеть это
        можно только в ряду выпусков;
  046 — «—» с причиной отличается от забытой ячейки: до `v1.0.0` поля
        `mechanism` не существовало, и метрика честно не считается;
  041 — две честные величины вместо одной усреднённой: «ничем» стоит рядом со
        числом действующих ответов;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — нет тегов или нет таблицы — это отказ, а не чистый прогон;
  158 — третий исход называет предмет: какой тег, какой файл.

Запуск:
  python scripts/history_metrics.py --check
  python scripts/history_metrics.py --add v1.2.0 --key "что принёс выпуск"
  python scripts/history_metrics.py --add v1.0.0 --key "..." --at-tag

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

# Определение локальной ссылки берётся у гейта ссылок, а не переписывается:
# две формулировки одной территории расходятся молча (правило 022), а разойдясь
# здесь, они дали бы расхождение чисел на ровном месте.
import check_links

ROOT = Path(__file__).resolve().parent.parent

HISTORY = "HISTORY.md"
SECTION = "## Эволюция метрик каталога"

#: Тег выпуска. Схема — VERSIONING.md: тег ставится только на границе MINOR.
#: Первый тег каталога поставлен без «v», и это факт истории, а не ошибка:
#: сравнение идёт по номеру, а не по написанию.
TAG_RE = re.compile(r"^v?\d+\.\d+\.0$")
ROW_RE = re.compile(r"^\|\s*(v?\d+\.\d+\.\d+)\s*\|")
#: Разделитель шапки таблицы. По нему таблица опознаётся пустой, а не
#: неразобранной: разница между «выпуск забыли» и «таблицы нет» — это разница
#: между находкой и третьим исходом.
HEADER_RE = re.compile(r"^\|\s*-{3,}")
RULE_PATH_RE = re.compile(r"^rules/ru/\d{3}-[a-z0-9-]+\.md$")
AREA_RE = re.compile(r"^\*\*Область\.\*\*\s*(.+?)\s*$", re.M)
#: Ячейка «Ключевое» со ссылкой — см. заголовок: строка сверяется по дереву,
#: в котором сама и лежит.
CELL_LINK_RE = re.compile(r"\[[^\]]*\]\(")
NOTHING_ABSENT = "—"


def release(tag: str) -> str:
    """Номер выпуска без «v»: тег `0.1.0` и строка `v0.1.0` — один выпуск."""
    return tag.lstrip("v")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True)


def tags(root: Path) -> tuple[list[str] | None, str | None]:
    """Теги выпусков по возрастанию номера. Вторым — причина отказа."""
    done = git(root, "tag", "--list")
    if done.returncode != 0:
        return None, f"{root} — git не ответил: {done.stderr.strip()[:120]}"
    found = [t for t in done.stdout.split() if TAG_RE.match(t)]
    if not found:
        return None, (f"{root} — тегов выпуска нет ни одного. Мелкий клон "
                      "тегов не приносит, а без них сверять строки не с чем")
    return sorted(found, key=lambda t: [int(p) for p in release(t).split(".")]), None


def files_at_tag(root: Path, tag: str) -> tuple[dict[str, str] | None, str | None]:
    """Дерево тега целиком: путь → текст. Вторым — причина отказа с адресом."""
    done = subprocess.run(["git", "-C", str(root), "archive", tag],
                          capture_output=True)
    if done.returncode != 0:
        return None, (f"тег {tag} — дерево не выгрузилось: "
                      f"{done.stderr.decode('utf-8', 'replace').strip()[:120]}")
    out: dict[str, str] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(done.stdout)) as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                fh = tar.extractfile(member)
                if fh is None:
                    continue
                out[member.name] = fh.read().decode("utf-8", "replace")
    except (tarfile.TarError, ValueError) as e:
        return None, f"тег {tag} — дерево не разобралось: {e}"
    return out, None


def files_in_tree(root: Path) -> tuple[dict[str, str] | None, str | None]:
    """То же для рабочего дерева, и только для ОТСЛЕЖИВАЕМЫХ файлов.

    Снимок выпуска сверяется по дереву тега, где лежит ровно отслеживаемое.
    Возьми мы здесь всё подряд, забытый в корне черновик сдвинул бы число
    ссылок — и строка разошлась бы с тегом, к которому её приписали.
    """
    done = git(root, "ls-files")
    if done.returncode != 0:
        return None, f"{root} — git не ответил: {done.stderr.strip()[:120]}"
    out: dict[str, str] = {}
    for name in done.stdout.splitlines():
        path = root / name
        if not path.is_file():
            continue
        out[name] = path.read_text(encoding="utf-8", errors="replace")
    if not out:
        return None, f"{root} — ни одного отслеживаемого файла"
    return out, None


def snapshot(files: dict[str, str]) -> dict[str, str]:
    """Четыре числа выпуска по дереву. Значения — уже ячейками таблицы."""
    rules = [n for n in files if RULE_PATH_RE.match(n)]

    areas: set[str] = set()
    for name in rules:
        m = AREA_RE.search(files[name])
        if m:
            areas |= {a.strip() for a in m.group(1).split(",") if a.strip()}

    links = 0
    for name, text in files.items():
        if not name.endswith(".md"):
            continue
        for m in check_links.LINK_RE.finditer(text):
            if not m.group(1).startswith(check_links.EXTERNAL):
                links += 1

    # «Ничем» считается только там, где поле `mechanism` уже существовало.
    # У 0.1.0 ответов каталога не было вовсе — там честный прочерк, а не ноль:
    # ноль означал бы «всё обеспечено», то есть ровно обратное правде (046).
    nothing = NOTHING_ABSENT
    raw = files.get(".rules/bindings.json")
    if raw:
        try:
            answers = json.loads(raw)["rules"].values()
        except (ValueError, KeyError, TypeError, AttributeError):
            answers = []
        active = [a for a in answers if isinstance(a, dict)
                  and a.get("status") == "active"]
        if active and all("mechanism" in a for a in active):
            none = sum(1 for a in active if a["mechanism"] == "none")
            nothing = f"{none} из {len(active)}"

    return {"правил": str(len(rules)), "областей": str(len(areas)),
            "ссылок": str(links), "ничем": nothing}


def table(text: str) -> tuple[list[str] | None, int | None]:
    """Строки таблицы «Эволюции метрик» и номер строки, ПОСЛЕ которой дописывать.

    Пустая таблица — не ошибка разбора: у проекта, забывшего дописать строку с
    первого же выпуска, она и будет пустой, и это находка, а не отказ (039).
    Отказом остаётся отсутствие самой таблицы: тогда разбирать нечего.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, s in enumerate(lines) if s.strip() == SECTION)
    except StopIteration:
        return None, None
    rows: list[str] = []
    after: int | None = None
    for i in range(start, len(lines)):
        if i > start and lines[i].startswith("## "):
            break
        if HEADER_RE.match(lines[i]):
            after = i
        elif ROW_RE.match(lines[i]):
            rows.append(lines[i])
            after = i
    return (rows, after) if after is not None else (None, None)


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def check(root: Path) -> int:
    path = root / HISTORY
    # ── исход 2 ────────────────────────────────────────────────────────────
    if not path.exists():
        print(f"проверка не отработала: нет {path} — документа, в котором "
              "живёт эволюция метрик", file=sys.stderr)
        return 2
    rows, _ = table(path.read_text(encoding="utf-8"))
    if rows is None:
        print(f"проверка не отработала: в {HISTORY} нет таблицы под заголовком "
              f"«{SECTION}» — сверять теги не с чем", file=sys.stderr)
        return 2
    found, err = tags(root)
    if err:
        print(f"проверка не отработала: {err}", file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    written = {release(cells(r)[0]): r for r in rows}
    for tag in found:
        num = release(tag)
        if num not in written:
            problems.append(
                f"выпуск {tag} состоялся, а строки о нём в «{SECTION}» нет. "
                "Ряд обрывается молча: читатель видит последний выпуск и "
                "думает, что он и есть текущий")
            continue
        got = cells(written.pop(num))
        want = snapshot_or_none(root, tag, problems)
        if want is None:
            continue
        for i, (name, value) in enumerate(want.items(), start=1):
            if i >= len(got):
                problems.append(f"строка {tag}: колонки «{name}» нет вовсе")
                continue
            if got[i] != value:
                problems.append(
                    f"строка {tag}: «{name}» = {got[i] or 'пусто'}, а по дереву "
                    f"тега {value}. Снимок разошёлся с тем, что был снимком")
        key = got[-1] if len(got) > len(want) else ""
        if not key:
            problems.append(
                f"строка {tag}: «Ключевое» пусто — ряд чисел без ответа на "
                "вопрос «что это был за выпуск» читается как отчёт, а не как "
                "история")
        elif CELL_LINK_RE.search(key):
            problems.append(
                f"строка {tag}: в «Ключевом» ссылка. Строка сверяется по "
                "дереву, в котором сама и лежит, и ссылка делает её неверной "
                "о себе самой")

    for num, row in written.items():
        problems.append(
            f"строка v{num}: такого тега нет. Строка пережила выпуск либо "
            "поставлена вперёд него и обещает то, чего не было")

    if problems:
        print("эволюция метрик разошлась с выпусками:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"эволюция метрик в порядке: выпусков {len(found)}, "
          "у каждого строка, и числа сходятся с деревом тега")
    return 0


def snapshot_or_none(root: Path, tag: str, problems: list[str]) -> dict | None:
    """Снимок по тегу; неудача выгрузки — находка с адресом, а не трассировка."""
    files, err = files_at_tag(root, tag)
    if err:
        problems.append(f"{err}. Сверить строку не с чем")
        return None
    return snapshot(files)


def add(root: Path, tag: str, key: str, at_tag: bool) -> int:
    path = root / HISTORY
    if not path.exists():
        print(f"дописать некуда: нет {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    rows, after = table(text)
    if rows is None or after is None:
        print(f"дописать некуда: в {HISTORY} нет таблицы под заголовком "
              f"«{SECTION}»", file=sys.stderr)
        return 2
    if release(tag) in {release(cells(r)[0]) for r in rows}:
        print(f"строка про {tag} уже есть — номера не переиспользуются",
              file=sys.stderr)
        return 1
    if not key.strip():
        print("«Ключевое» пусто: ряд чисел без ответа «что это был за выпуск» "
              "историей не является", file=sys.stderr)
        return 1
    if CELL_LINK_RE.search(key):
        print("в «Ключевом» ссылка: строка сверяется по дереву, в котором сама "
              "и лежит, и ссылка сделает её неверной о себе самой",
              file=sys.stderr)
        return 1

    files, err = (files_at_tag(root, tag) if at_tag else files_in_tree(root))
    if err:
        print(f"снимок не собрался: {err}", file=sys.stderr)
        return 2
    snap = snapshot(files)

    row = "| " + " | ".join([tag, *snap.values(), key.strip()]) + " |"
    lines = text.splitlines()
    lines.insert(after + 1, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"дописано: {row}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    parser.add_argument("--check", action="store_true",
                        help="сверить строки выпусков с тегами")
    parser.add_argument("--add", metavar="ТЕГ",
                        help="дописать строку выпуска, посчитав числа")
    parser.add_argument("--key", default="",
                        help="колонка «Ключевое»: что принёс выпуск, одной фразой")
    parser.add_argument("--at-tag", action="store_true",
                        help="считать по дереву тега, а не по рабочему: так "
                             "досыпают строки выпускам, которые уже состоялись")
    args = parser.parse_args(argv)

    if args.add:
        return add(args.root, args.add, args.key, args.at_tag)
    if args.check:
        return check(args.root)
    parser.error("нужен --check или --add")
    return 2


if __name__ == "__main__":
    sys.exit(main())
