#!/usr/bin/env python3
"""Вписанное рукой: сворачиваемые блоки в тексте и версия в манифестах.

Два предмета, и оба — про то, что человек вписывает рукой, а ломается оно
молча. Держатся одним скриптом потому, что ловятся одним приёмом — поиском по
тексту отслеживаемых файлов, — и второй сторож над тем же деревом разошёлся бы
с первым в том, что считать текстом (022).

  • 008 — `<details>` даёт заголовок без содержимого там, где страницу читают
    машинально: в текстовой выгрузке спойлер схлопывается в строку `summary`, и
    следом идёт другой блок. Четыре обзора подряд написали «раздел обрывается»,
    прежде чем причину приняли всерьёз;
  • 035 — версия задаётся в одном месте. У каталога это git-тег, и в файлы она
    не попадает вовсе; `pyproject.toml` держит заглушку `0.0.0`.

ГРАНИЦА ВТОРОЙ ПРОВЕРКИ — МАНИФЕСТЫ, А НЕ ПРОЗА, и это измерено. Поиск числа
вида `X.Y.Z` по дереву даёт шестнадцать файлов, и все шестнадцать законны:
история выпусков в журнале, схема в `VERSIONING`, чужие версии в инцидентах
записей. Отличить число-факт от числа в рассказе машинно нечем — ровно то, что
записано в ответе каталога по 005, — а ложные отказы на прозе приучают
пропускать (051). Поэтому проверяется поле версии в манифесте сборки: там
число обязано быть заглушкой, и разночтения нет.

Реализует правила каталога:
  008 — сворачиваемых блоков нет там, где страницу читают машинально;
  035 — версия не вписывается в файлы: источник один, и это тег;
  164 — номер версии говорит, чего он версия: схема, объявленная в файле и
        не названная в политике версий, читается как версия каталога;
  041 — две честные величины вместо одной усреднённой: номер каталога и номер
        формата двигаются врозь, и каждый назван отдельно;
  025 — номер задачи живёт в инциденте и следе, а не в объяснении;
  089 — запись не ссылается в производное: копия отстаёт всегда;
  046 — обе лицензии названы витриной: файл, о котором молчат, не найдут;
  051 — запрещается достоверное: тег в манифесте — факт, число в прозе — нет;
  039 — три исхода: чисто · есть находки · проверка не отработала;
  075 — ноль просмотренных файлов это отказ, а не чистый прогон.

Исходы:
  0 — чисто;  1 — есть находки;  2 — проверка не отработала.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Текст, который читают машинально: витрина, свод, записи каталога.
PROSE_SUFFIX = (".md",)
#: Манифест сборки: там версия — поле, а не рассказ.
MANIFESTS = {"pyproject.toml": re.compile(r"^version\s*=\s*\"([^\"]+)\"", re.M)}

#: ТРЕТИЙ ПРЕДМЕТ — НОМЕРА ФОРМАТОВ. У каталога один номер версии, тег; всё
#: остальное, что выглядит версией, версионирует ФОРМАТ и живёт своей жизнью.
#: Спутать легко, и это измерено вопросом владельца: в контракте `"schema":
#: "1.2"` стоит рядом с `@v1.1.0`, и «почему 1.2, если выпуска 1.2 не было»
#: спрашивается само собой.
#:
#: Держится это тем же приёмом, что и два предмета выше: поиском по тексту
#: отслеживаемых файлов. Схема, объявленная в файле и НЕ названная в
#: VERSIONING.md, читается как версия каталога — и ровно так и была прочитана.
VERSIONS_DOC = "VERSIONING.md"
SCHEMA_RE = re.compile(r'"schema"\s*:\s*"[\d.]+"')
#: Заготовки — образцы для чужого проекта, а не объявления каталога: их схема
#: описана в контракте потребления, и требовать её здесь значило бы требовать
#: от каталога отвечать за чужой файл (правило 097).
SCHEMA_SKIP = ("templates/",)
#: Заглушка, означающая «версия приходит из тега». Список разрешительный:
#: запретительный («всё, кроме похожего на настоящую версию») завтра пропустит
#: новую форму записи (правило 068).
PLACEHOLDERS = {"0.0.0"}

#: Сворачиваемый блок. Упоминание в обратных кавычках — это код, а не блок:
#: сама запись 008 иначе оказалась бы своим первым нарушителем.
DETAILS_RE = re.compile(r"(?<!`)<details\b", re.I)
FENCE_RE = re.compile(r"^\s*```")

#: Разделы ОБЪЯСНЕНИЯ, где номер задачи мешает: он датирует, а не поясняет.
#: Список запретительный, и это выбор против 068: в «Инциденте» номер законен —
#: там он и есть датировка, — а ошибиться в другую сторону значит краснеть на
#: верной записи, чему цена выше (051). Новый раздел объяснения гейт пропустит;
#: пропущенный номер стоит правки строки, ложный отказ — доверия к гейту.
EXPLAINING = ("Почему", "Why", "Применимость", "Where it applies",
              "Практические границы", "Practical boundaries")
#: Номер задачи: `#123` и `владелец/репо#123`. Не путать с якорем и решёткой
#: заголовка — отсюда требование цифр и границы слова.
ISSUE_RE = re.compile(r"(?<![\w/])#\d{1,5}\b")

#: Производные каталога: их собирает сборка, и они отстают всегда. Ссылка
#: отсюда уводит читателя в прошлое из того самого места, где лежит настоящее.
DERIVED = ("rules/README.md", "export/", ".github/badges/")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def tracked(root: Path) -> list[Path]:
    """Отслеживаемые файлы. Непрослеживаемый мусор проверять незачем."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [root / line for line in out.split("\0") if line]


def details_lines(text: str) -> list[int]:
    """Номера строк со сворачиваемым блоком — вне блоков кода.

    Пример внутри ``` — это показ, а не употребление: запись, объясняющая, чем
    плох спойлер, обязана уметь его процитировать.
    """
    found: list[int] = []
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced and DETAILS_RE.search(line):
            found.append(n)
    return found


def sections_of(text: str) -> list[tuple[str, int, str]]:
    """Разделы файла: имя, номер первой строки, тело. Начало — до первого `##`."""
    out: list[tuple[str, int, list[str]]] = [("начало", 1, [])]
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            out.append((line[3:].strip(), n, []))
        else:
            out[-1][2].append(line)
    return [(name, n, "\n".join(body)) for name, n, body in out]


def issue_numbers(text: str) -> list[tuple[str, str]]:
    """Номера задач в разделах объяснения: раздел и сам номер.

    В «Инциденте» номер — датировка, и она там на месте. В «Почему» он мешает:
    читатель уходит смотреть задачу вместо того, чтобы прочитать механизм
    поломки, а задача расскажет ему то же самое, только длиннее и позже (025).
    """
    found: list[tuple[str, str]] = []
    for name, _, body in sections_of(text):
        if name not in EXPLAINING:
            continue
        fenced = False
        for line in body.splitlines():
            if FENCE_RE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            found += [(name, m.group(0)) for m in ISSUE_RE.finditer(line)]
    return found


def links_to_derived(text: str) -> list[str]:
    """Ссылки записи в производные каталога — указатель, выгрузку, значки."""
    return [t for t in LINK_RE.findall(text)
            if any(d in t for d in DERIVED)]


def schema_unnamed(root: Path) -> list[str]:
    """Номера форматов, объявленные в файлах и НЕ названные в политике версий.

    Нет политики версий — предмета нет: документ принадлежит каталогу, а
    проверка ходит и по подделанным деревьям. Молчание при этом не тихое: итог
    говорит, сколько номеров просмотрено (075).
    """
    doc = root / VERSIONS_DOC
    if not doc.exists():
        return []
    сказано = doc.read_text(encoding="utf-8")
    out: list[str] = []
    for path in sorted(tracked(root)):
        rel = str(path.relative_to(root))
        if not rel.endswith(".json") or rel.startswith(SCHEMA_SKIP):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if SCHEMA_RE.search(text) and rel not in сказано:
            out.append(
                f"{rel}: номер формата объявлен, а в {VERSIONS_DOC} о нём ни "
                "слова. Читатель прочтёт его как версию каталога — так и "
                "случилось с выгрузкой правил")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="корень каталога; по умолчанию сам этот репозиторий")
    args = parser.parse_args(argv)
    root: Path = args.root

    files = tracked(root)
    prose = [p for p in files if p.suffix in PROSE_SUFFIX and p.exists()]

    # ── исход 2 ────────────────────────────────────────────────────────────
    if not prose:
        print("проверка не отработала: отслеживаемых текстовых файлов не "
              "нашлось — смотреть нечего, и зеленеть на этом нельзя",
              file=sys.stderr)
        return 2

    # ── исход 1 ────────────────────────────────────────────────────────────
    problems: list[str] = []
    for path in sorted(prose):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line in details_lines(text):
            problems.append(
                f"{path.relative_to(root)}:{line}: сворачиваемый блок. В "
                "текстовой выгрузке он схлопывается в строку `summary`, и "
                "раздел читается как оборванный — раскройте или не пишите (008)")

    # Записи каталога — оригинал; указатель и выгрузка — его копии.
    for path in sorted(p for p in prose if p.parent.name in ("ru", "en")
                       and p.parent.parent.name == "rules"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        for section, num in issue_numbers(text):
            problems.append(
                f"{rel}: номер задачи {num} в разделе «{section}». Номер "
                "датирует, а не объясняет: в инциденте и следе он на месте, "
                "в объяснении уводит читателя от механизма поломки (025)")
        for target in links_to_derived(text):
            problems.append(
                f"{rel}: ссылка в производное «{target}». Копия отстаёт всегда, "
                "и ссылка отсюда отправляет читателя в прошлое из того места, "
                "где лежит настоящее (089)")

    # ЛИЦЕНЗИЙ ДВЕ, И ОБЕ ОБЯЗАНЫ БЫТЬ НАЗВАНЫ. Площадка показывает одну — ту,
    # что в LICENSE, — и вторая существует ровно настолько, насколько на неё
    # ссылается витрина. Файл, о котором молчат, берущий не найдёт.
    # ПРЕДМЕТ — РЕПОЗИТОРИЙ, ОБЪЯВИВШИЙ ЛИЦЕНЗИЮ. Там, где её нет вовсе,
    # требовать вторую половину не с чего: это не смягчение, а граница —
    # проверка без предмета обязана молчать, а не краснеть (075, 097).
    for lic in (("LICENSE", "LICENSE-CODE") if (root / "LICENSE").exists() else ()):
        if not (root / lic).exists():
            problems.append(f"{lic}: файла нет. Лицензий у каталога две — "
                            "проза и исполняемое, — и обе обязаны лежать")
            continue
        названа = any(lic in (root / doc).read_text(encoding="utf-8")
                      for doc in ("README.md", "README.en.md")
                      if (root / doc).exists())
        if not названа:
            problems.append(
                f"{lic}: лежит, а витрина о нём молчит. Лицензия, которую не "
                "нашли, не действует в глазах того, кто берёт")

    problems += schema_unnamed(root)

    for name, pattern in MANIFESTS.items():
        path = root / name
        if not path.exists():
            continue
        m = pattern.search(path.read_text(encoding="utf-8"))
        if m and m.group(1) not in PLACEHOLDERS:
            problems.append(
                f"{name}: версия «{m.group(1)}» вписана в манифест. Источник "
                "версии один — тег; вписанная расходится с ним молча и "
                "обнаруживается после публикации (035)")

    if problems:
        print("в тексте каталога есть вписанное рукой:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        return 1

    print(f"текст в порядке: просмотрено {len(prose)} документов — "
          "сворачиваемых блоков нет, номера задач стоят в инциденте и следе, "
          "ссылок в производные нет, версия в манифестах не вписана")
    return 0


if __name__ == "__main__":
    sys.exit(main())
