#!/usr/bin/env python3
"""У каждого выпуска есть раздел в истории и строка метрик, сверенная с тегом.

Таблица в `HISTORY.md` держалась договорённостью «дописать строку при выпуске».
Договорённость сломалась молча: после `v0.1.0` вышли `v1.0.0` и `v1.1.0`, и ни
одной строки никто не добавил. Заметил это владелец через два выпуска — то
есть механизма у таблицы не было вовсе (правило 002), а число в прозе держалось
обещанием (005).

ЧТО ПРОВЕРЯЕТСЯ.

  • у каждого тега выпуска есть свой РАЗДЕЛ в истории: единица истории —
    выпуск, и раздел, которого нет, оставляет решения выпуска нерассказанными;
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
  161 — единица истории это выпуск: у каждого тега свой раздел, а незакрытый
        выпуск переименовывает в номер и дату сам выпуск, а не рука;
  106 — вопрос витрины «сколько тестов и тестовых модулей» адресован
        сопровождающему, и ответ ему живёт здесь колонкой снимка, а не
        значком: значок с этим числом дёргался бы от каждого изменения;
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
  # тот же вызов переименовывает «## Не выпущено · X» в «## v1.2.0 · дата · X»
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
#: Заголовок раздела выпуска: «## v1.1.0 · 28 августа 2026 · чем он был».
#: Единица истории — выпуск (правило 161), и раздел, которого нет, оставляет
#: решения выпуска нерассказанными. Форму раздела держит audit_catalogue.py;
#: здесь спрашивается только его НАЛИЧИЕ у каждого тега — теги, их даты и
#: деревья уже живут тут, и второй сборщик того же разошёлся бы с первым (022).
RELEASE_HEAD_RE = re.compile(r"(?m)^## (v?\d+\.\d+\.\d+)\s+·\s+")
#: Незакрытый выпуск. Имя и дату ему ставит `--add`, а не рука: иначе
#: переименование стало бы новой договорённостью — той самой, на которой
#: сломалась строка метрик.
OPEN_HEAD_RE = re.compile(r"(?m)^## Не выпущено\s+·\s+(.+)$")

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
                          capture_output=True, text=True, encoding="utf-8")


def tags(root: Path) -> tuple[list[str] | None, str | None]:
    """Теги выпусков по возрастанию номера. Вторым — причина отказа."""
    done = git(root, "tag", "--list")
    if done.returncode != 0:
        return None, f"{root} — git не ответил: {done.stderr.strip()[:120]}"
    found = [t for t in done.stdout.split() if TAG_RE.match(t)]
    if not found:
        return None, (f"{root} — тегов выпуска нет ни одного. Мелкий клон "
                      "тегов не приносит, а без них сверять строки не с чем")
    # не проза: номер версии — «1.2» режется на числа для сортировки.
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


#: Тестовый модуль и тест. Считаются по дереву тега, как и всё остальное здесь:
#: прогон `pytest -q` дал бы число ТЕКУЩЕГО дерева, а строка выпуска — снимок.
#: Разбор регулярным выражением, а не `ast`: файл дерева тега может быть написан
#: на синтаксисе, который этот интерпретатор не разберёт, и снимок прошлого
#: выпуска упал бы на будущем Python (правило 051).
TEST_MODULE_RE = re.compile(r"^tests/test_[\w.]+\.py$")
TEST_DEF_RE = re.compile(r"(?m)^\s*(?:async\s+)?def\s+test_\w*\s*\(")


def snapshot(files: dict[str, str]) -> dict[str, str]:
    """Шесть чисел выпуска по дереву. Значения — уже ячейками таблицы.

    Тесты и тестовые модули отвечают на вопрос СОПРОВОЖДАЮЩЕГО, и живут они
    здесь, а не значком: значок с этим числом дёргался бы от каждого изменения
    и шумел там, куда смотрят один раз. Адрес назван в `.rules/showcase.json`
    полем `where` — витрина отвечает на вопрос сопровождающего источником, а не
    «значка нет» (правило 049).
    """
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

    modules = [n for n in files if TEST_MODULE_RE.match(n)]
    tests = sum(len(TEST_DEF_RE.findall(files[n])) for n in modules)

    return {"правил": str(len(rules)), "областей": str(len(areas)),
            "ссылок": str(links), "тестов": str(tests),
            "модулей": str(len(modules)), "ничем": nothing}


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


#: Месяцы родительным падежом: заголовок читается «28 августа 2026», а не
#: «2026-08-28». Формат взят у уже написанных разделов, а не выдуман.
MONTHS = ("января", "февраля", "марта", "апреля", "мая", "июня", "июля",
          "августа", "сентября", "октября", "ноября", "декабря")


def tag_date(root: Path, tag: str) -> tuple[str, str]:
    """Дата тега словами. Ошибка возвращается строкой, а не трассировкой."""
    done = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%cs",
                           tag], capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0 or not done.stdout.strip():
        return "", f"у тега {tag} не спросить дату: {done.stderr.strip()}"
    year, month, day = done.stdout.strip().split("-")
    return f"{int(day)} {MONTHS[int(month) - 1]} {year}", ""


def close_section(text: str, tag: str, date: str) -> tuple[str, str]:
    """«## Не выпущено · X» → «## <тег> · <дата> · X».

    Переименование делает выпуск, а не рука. Иначе у раздела появилась бы
    ровно та договорённость «не забыть дописать», на которой сломалась строка
    метрик, — и сломалась бы вторично, тем же способом.
    """
    if RELEASE_HEAD_RE.search(text) and any(
            release(m.group(1)) == release(tag)
            for m in RELEASE_HEAD_RE.finditer(text)):
        return text, ""                 # раздел уже под своим номером
    m = OPEN_HEAD_RE.search(text)
    if not m:
        return text, (f"раздела о выпуске в {HISTORY} нет: ни «## {tag} · …», "
                      "ни «## Не выпущено · …». Строка метрик встанет, а "
                      "решения выпуска останутся нерассказанными")
    return (text[:m.start()] + f"## {tag} · {date} · {m.group(1)}"
            + text[m.end():]), ""


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
    text = path.read_text(encoding="utf-8")
    sections = {release(m.group(1)) for m in RELEASE_HEAD_RE.finditer(text)}
    written = {release(cells(r)[0]): r for r in rows}
    for tag in found:
        num = release(tag)
        if num not in sections:
            problems.append(
                f"выпуск {tag} состоялся, а раздела о нём в {HISTORY} нет. "
                "Единица истории — выпуск: без раздела его решения остаются "
                "нерассказанными, и рядом с рядом тегов стоит пустое место")
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

    print(f"история сошлась с выпусками: их {len(found)}, у каждого свой раздел "
          "и строка метрик, и числа сходятся с деревом тега")
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

    date, err = tag_date(root, tag)
    if err:
        print(f"дописать нечего: {err}", file=sys.stderr)
        return 2

    row = "| " + " | ".join([tag, *snap.values(), key.strip()]) + " |"
    lines = text.splitlines()
    lines.insert(after + 1, row)
    closed, err = close_section("\n".join(lines) + "\n", tag, date)
    if err:
        print(err, file=sys.stderr)
        return 1
    path.write_text(closed, encoding="utf-8")
    print(f"дописано: {row}")
    print(f"раздел выпуска закрыт заголовком «## {tag} · {date} · …»")
    return 0


def recount(root: Path) -> int:
    """Пересчитать числа всех строк по их тегам, сохранив «Ключевое».

    ЗАЧЕМ ОТДЕЛЬНЫЙ КЛЮЧ. Состав колонок меняется: их стало шесть вместо
    четырёх. Дописать новые ячейки в прошлые строки рукой нельзя — это ровно
    то число в прозе, ради запрета которого весь этот скрипт и написан (005).
    Пересчёт делает та же сборка, что и ставит строку при выпуске.

    Ключ применяют РЕДКО — при смене состава колонок. В обычной жизни строку
    ставит выпуск, и трогать прошлые незачем: снимок не устаревает.
    """
    path = root / HISTORY
    if not path.exists():
        print(f"пересчитывать нечего: нет {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    rows, _ = table(text)
    if not rows:
        print(f"пересчитывать нечего: в {HISTORY} нет строк выпусков под "
              f"«{SECTION}»", file=sys.stderr)
        return 2

    known = {release(tag): tag for tag in tags(root)[0]}
    changed = 0
    for row in rows:
        got = cells(row)
        tag = known.get(release(got[0]))
        if tag is None:
            print(f"пересчитывать нечего: строка {got[0]} — тега такого нет",
                  file=sys.stderr)
            return 2
        files, err = files_at_tag(root, tag)
        if err:
            print(f"пересчёт не отработал: {err}", file=sys.stderr)
            return 2
        fresh = "| " + " | ".join([got[0], *snapshot(files).values(),
                                   got[-1]]) + " |"
        if fresh != row:
            text = text.replace(row, fresh, 1)
            changed += 1
    path.write_text(text, encoding="utf-8")
    print(f"пересчитано строк: {changed} из {len(rows)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    parser.add_argument("--check", action="store_true",
                        help="сверить строки выпусков с тегами")
    parser.add_argument("--recount", action="store_true",
                        help="пересчитать числа всех строк по их тегам: нужен "
                             "при смене состава колонок, «Ключевое» сохраняется")
    parser.add_argument("--add", metavar="ТЕГ",
                        help="дописать строку выпуска, посчитав числа")
    parser.add_argument("--key", default="",
                        help="колонка «Ключевое»: что принёс выпуск, одной фразой")
    parser.add_argument("--at-tag", action="store_true",
                        help="считать по дереву тега, а не по рабочему: так "
                             "досыпают строки выпускам, которые уже состоялись")
    args = parser.parse_args(argv)

    if args.recount:
        return recount(args.root)
    if args.add:
        return add(args.root, args.add, args.key, args.at_tag)
    if args.check:
        return check(args.root)
    parser.error("нужен --check или --add")
    return 2


if __name__ == "__main__":
    sys.exit(main())
