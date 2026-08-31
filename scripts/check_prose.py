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
#: Заглушка, означающая «версия приходит из тега». Список разрешительный:
#: запретительный («всё, кроме похожего на настоящую версию») завтра пропустит
#: новую форму записи (правило 068).
PLACEHOLDERS = {"0.0.0"}

#: Сворачиваемый блок. Упоминание в обратных кавычках — это код, а не блок:
#: сама запись 008 иначе оказалась бы своим первым нарушителем.
DETAILS_RE = re.compile(r"(?<!`)<details\b", re.I)
FENCE_RE = re.compile(r"^\s*```")


def tracked(root: Path) -> list[Path]:
    """Отслеживаемые файлы. Непрослеживаемый мусор проверять незачем."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [root / line for line in out.split("\n") if line]


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

    print(f"текст в порядке: просмотрено {len(prose)} документов, "
          "сворачиваемых блоков нет, версия в манифестах не вписана")
    return 0


if __name__ == "__main__":
    sys.exit(main())
