#!/usr/bin/env python3
"""Значок покрытия: пересобирается из замера, а не пишется рукой.

Реализует правила каталога:
  005 — число в артефакте ставит сборка, а не автор: вписанное рукой устаревает
        молча, и заметить это некому;
  039 — у проверки три исхода, а не два;
  075 — не нашёл предмета замера — падает, а не зеленеет;
  158 — данные замера есть, а не разбираются: отказ называет файл и то, чего
        в дереве не нашлось, а не пролетает чужим исключением.

ГДЕ ЛЕЖИТ ЗНАЧОК. Скрипт кладёт `.github/badges/coverage.json` в рабочее
дерево прогона, а на отдельную ветку `badges` его увозит
`.github/workflows/badges.yml` вместе с остальными значками (160). В общей
ветке значков нет — там `.gitignore`: значок, пересобираемый каждым
изменением, давал конфликт на каждом слиянии. Здесь прежде было написано
обратное — что значок лежит в общей ветке под гейтом свежести; это описание
пережило переезд значков на `badges`.

ПОЧЕМУ ЦВЕТ СЧИТАЕТСЯ, А НЕ ЗАДАЁТСЯ. Зелёный значок над покрытием в 13%
— утверждение, которого никто не делал (правило 049). Порог у цвета один на
всех и подобран так, чтобы значок не льстил.

Исходы:
  0 — чисто (значок пересобран или совпал);
  1 — значок устарел: замер разошёлся с тем, что лежит в ветке;
  2 — замер не отработал: нет данных покрытия либо они не разбираются.

Запуск:  python scripts/coverage_badge.py           # пересобрать
         python scripts/coverage_badge.py --check    # проверить, не устарел ли
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BADGE = ROOT / ".github" / "badges" / "coverage.json"
DATA = ROOT / ".coverage"

LABEL = "coverage"

#: Порог цвета. Нижняя граница названа явно: значок, зелёный при любом числе,
#: перестают читать так же, как гейт, красный всегда.
COLORS = ((90, "brightgreen"), (75, "green"), (50, "yellow"),
          (25, "orange"), (0, "red"))


class Unreadable(Exception):
    """Данные замера есть, а разобрать их нельзя. Сообщение называет файл и причину."""


def measured() -> float | None:
    """Процент покрытия из данных замера. None — замера не было.

    ДАННЫЕ ЕСТЬ, НО НЕ РАЗБИРАЮТСЯ — это не «замера не было», а отдельный
    исход, и он поднимается как `Unreadable` с названным предметом. Чаще всего
    это данные прогона на ДРУГОМ дереве: `.coverage` игнорируется git и
    переживает смену ветки, а замер ссылается на файлы, которых здесь нет.
    Замер 24 сентября: `report()` бросал `NoSource` на `scripts/check_skills.py`
    с соседней ветки, исключение пролетало сквозь `build_facts`, и два его теста
    краснели на изменении, не трогавшем ни покрытия, ни фактов.
    """
    try:
        import coverage
    except ImportError:
        return None
    if not DATA.exists():
        return None
    cov = coverage.Coverage(data_file=str(DATA))
    try:
        cov.load()
        # report() печатает таблицу; вывод глушим — здесь нужно только число.
        with open("/dev/null", "w", encoding="utf-8") as quiet:
            return cov.report(file=quiet)
    except coverage.exceptions.CoverageException as отказ:
        raise Unreadable(f"{DATA} не разбирается: {str(отказ).rstrip('.')}") from отказ


def color(percent: float) -> str:
    return next(c for threshold, c in COLORS if percent >= threshold)


def render(percent: float) -> str:
    """Значок shields.io в формате endpoint — той же формы, что у правил."""
    return (
        "{\n"
        '  "schemaVersion": 1,\n'
        f'  "label": "{LABEL}",\n'
        f'  "message": "{percent:.0f}%",\n'
        f'  "color": "{color(percent)}"\n'
        "}\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="только проверить, не устарел ли значок")
    args = ap.parse_args()

    try:
        percent = measured()
    except Unreadable as отказ:
        print(f"замер не отработал: {отказ}. Данные ссылаются на то, чего в "
              "дереве нет, либо повреждены — пересобрать: "
              "`coverage run -m pytest`", file=sys.stderr)
        return 2
    if percent is None:
        print(f"замер не отработал: {DATA} не прочитан — сначала "
              "`coverage run -m pytest`", file=sys.stderr)
        return 2

    want = render(percent)
    have = BADGE.read_text(encoding="utf-8") if BADGE.exists() else ""

    if args.check:
        if have == want:
            print(f"значок покрытия актуален: {percent:.0f}%")
            return 0
        print(f"значок покрытия устарел: замер даёт {percent:.0f}%, "
              f"в ветке лежит другое.\n  Пересобрать: "
              f"coverage run -m pytest && python scripts/coverage_badge.py",
              file=sys.stderr)
        return 1

    BADGE.parent.mkdir(parents=True, exist_ok=True)
    BADGE.write_text(want, encoding="utf-8")
    print(f"значок покрытия пересобран: {percent:.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
